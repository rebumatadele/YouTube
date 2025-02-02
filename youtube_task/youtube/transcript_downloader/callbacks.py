from transcript_downloader.yt_transcript_download import get_batch_transcripts
from io import StringIO
import pandas as pd
import streamlit as st
import copy

def convert_to_txt(df: pd.DataFrame) -> str:
    """
    Convert the transcripts DataFrame into a text string
    in the following format for each video:
    
    {video_title}
    {youtube_url}
    -------------------
    {transcript}
    """
    txt_content = ""
    for _, row in df.iterrows():
        # Extract video title and url
        video_title = row.get("video_title", "Unknown Title")
        youtube_url = row.get("youtube_url", "Unknown URL")
        
        # Process transcript
        transcript_data = row.get("transcript", "")
        if isinstance(transcript_data, list):
            transcript_text = " ".join([entry.get("text", "") for entry in transcript_data])
        else:
            transcript_text = str(transcript_data)
        
        txt_content += f"{video_title}\n{youtube_url}\n-------------------\n{transcript_text}\n\n"
    return txt_content

def fetch_transcripts(uploaded_file, text_urls):
    youtube_urls = []
    
    # Handle file upload
    if uploaded_file is not None:
        if text_urls and len(text_urls.strip()) > 0:
            st.warning("You can enter URLs manually or from file, but not both.", icon="⚠️")
            st.stop()
        if uploaded_file.type == "text/plain":
            stringio = StringIO(uploaded_file.read().decode("utf-8"))
            for line in stringio:
                youtube_urls.append(line.strip())
    
    # Handle manual text input
    if text_urls and len(text_urls.strip()) > 0:
        if uploaded_file is not None:
            st.warning("You can enter URLs manually or from file, but not both.", icon="⚠️")
            st.stop()
        try:
            text_urls_split = text_urls.split(",")
            text_urls_split = [v.strip() for v in text_urls_split]
            youtube_urls = text_urls_split
        except Exception:
            st.warning("Please check your manually entered URLs.", icon="⚠️")
            st.stop()

    # Fetch transcripts
    batch_transcripts = get_batch_transcripts(youtube_urls)
    df = pd.DataFrame(batch_transcripts)

    # Create a deep copy for UI preview
    def truncate_and_append(text, length=100, suffix="..."):
        return text[:length] + suffix if len(text) > length else text

    df_table = copy.deepcopy(df).astype(str)
    if "transcript" in df_table.columns:
        df_table["transcript"] = df_table["transcript"].apply(lambda x: truncate_and_append(x))

    # Convert full data into text format
    txt_output = convert_to_txt(df)

    return df_table, txt_output
