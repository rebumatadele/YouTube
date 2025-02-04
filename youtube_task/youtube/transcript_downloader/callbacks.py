import os
import pandas as pd
import streamlit as st
import time
import copy
from transcript_downloader.yt_transcript_download import get_single_transcript
from persistence import load_persistent_state, save_persistent_state

def convert_to_txt(df: pd.DataFrame) -> str:
    txt_content = ""
    for _, row in df.iterrows():
        video_title = row.get("video_title", "Unknown Title")
        youtube_url = row.get("youtube_url", "Unknown URL")
        transcript_data = row.get("transcript", "")
        if isinstance(transcript_data, list):
            transcript_text = " ".join([entry.get("text", "") for entry in transcript_data])
        else:
            transcript_text = str(transcript_data)
        txt_content += f"{video_title}\n{youtube_url}\n-------------------\n{transcript_text}\n\n"
    return txt_content

def fetch_transcripts_and_prepare_downloads(uploaded_file, text_urls):
    youtube_urls = []
    # Determine channel key: if a file is uploaded, use its name (without extension); otherwise, "individual"
    if uploaded_file is not None:
        channel = os.path.splitext(uploaded_file.name)[0]
    else:
        channel = "individual"

    # --- Sanitize and read URLs ---
    if uploaded_file is not None:
        if text_urls and text_urls.strip():
            st.warning("Please provide URLs either manually or via file upload, not both.", icon="⚠️")
            st.stop()
        if uploaded_file.type == "text/plain":
            content = uploaded_file.read().decode("utf-8")
            file_urls = [u.strip() for u in content.split(",") if u.strip()]
            youtube_urls.extend(file_urls)
    if text_urls and text_urls.strip():
        if uploaded_file is not None:
            st.warning("Please provide URLs either manually or via file upload, not both.", icon="⚠️")
            st.stop()
        try:
            urls_from_text = [u.strip() for u in text_urls.split(",") if u.strip()]
            youtube_urls.extend(urls_from_text)
        except Exception:
            st.warning("Error processing the provided URLs.", icon="⚠️")
            st.stop()
    if not youtube_urls:
        st.error("No valid YouTube URLs were provided.")
        st.stop()

    num_urls = len(youtube_urls)
    progress_bar = st.progress(0)
    status_placeholder = st.empty()
    
    # We'll update the status text with a summary of processed videos.
    processed_titles = []
    transcripts_by_video = {}
    batch_transcripts = []
    for i, url in enumerate(youtube_urls):
        # Update status with current URL and summary of processed titles.
        status_placeholder.text(f"Processing URL {i+1}/{num_urls}: {url}\nProcessed: {', '.join(processed_titles)}")
        transcript_entry = get_single_transcript(url)
        batch_transcripts.append(transcript_entry)
        video_title = transcript_entry.get("video_title", "Unknown Title")
        transcript_data = transcript_entry.get("transcript", "")
        if isinstance(transcript_data, list):
            transcript_text = " ".join([seg.get("text", "") for seg in transcript_data])
        else:
            transcript_text = str(transcript_data)
        transcripts_by_video[video_title] = transcript_text
        processed_titles.append(video_title)
        progress_bar.progress((i + 1) / num_urls)
        time.sleep(0.1)
    
    status_placeholder.text("All transcripts processed!")
    st.session_state.transcript_all_done = True

    df = pd.DataFrame(batch_transcripts)
    def truncate_and_append(text, length=100, suffix="..."):
        return text[:length] + suffix if len(text) > length else text
    df_table = copy.deepcopy(df).astype(str)
    if "transcript" in df_table.columns:
        df_table["transcript"] = df_table["transcript"].apply(lambda x: truncate_and_append(x))
    st.session_state.transcript_data_table = df_table

    # Update persistent state: group transcripts under the chosen channel.
    persistent_state = st.session_state.get("persistent_state", load_persistent_state())
    if "transcripts" not in persistent_state:
        persistent_state["transcripts"] = {}
    # Merge with any existing transcripts under this channel.
    existing = persistent_state["transcripts"].get(channel, {})
    existing.update(transcripts_by_video)
    persistent_state["transcripts"][channel] = existing
    save_persistent_state(persistent_state)
    st.session_state.persistent_state = persistent_state

    # Also update the session state (grouped by channel).
    if "transcripts_by_video" not in st.session_state or not st.session_state.transcripts_by_video:
        st.session_state.transcripts_by_video = {}
    st.session_state.transcripts_by_video[channel] = existing
