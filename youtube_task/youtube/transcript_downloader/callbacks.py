from transcript_downloader.yt_transcript_download import get_single_transcript
from io import StringIO
import pandas as pd
import streamlit as st
import copy
import time

def convert_to_txt(df: pd.DataFrame) -> str:
    """
    Convert the transcripts DataFrame into a text string.
    Each video's transcript is separated by a header containing its title and URL.
    """
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

    # --- Sanitize and read URLs ---
    # 1. If a file is uploaded, assume it is a comma‑separated list.
    if uploaded_file is not None:
        if text_urls and text_urls.strip():
            st.warning("Please provide URLs either manually or via file upload, not both.", icon="⚠️")
            st.stop()
        if uploaded_file.type == "text/plain":
            # Read entire file content and split on commas.
            content = uploaded_file.read().decode("utf-8")
            file_urls = [u.strip() for u in content.split(",") if u.strip()]
            youtube_urls.extend(file_urls)
    # 2. Otherwise, if manual text input is provided, split on commas and sanitize.
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

    # --- Initialize log and progress display ---
    st.session_state.transcript_log = ""
    log_area = st.empty()  # This area will display log messages.
    num_urls = len(youtube_urls)
    progress_bar = st.progress(0)
    overall_log = []  # To accumulate log messages

    batch_transcripts = []
    for i, url in enumerate(youtube_urls):
        overall_log.append(f"Processing URL {i+1}/{num_urls}: {url}")
        log_area.text("\n".join(overall_log))
        transcript_entry = get_single_transcript(url)
        batch_transcripts.append(transcript_entry)
        # Update progress (as fraction and percentage)
        progress = (i + 1) / num_urls
        progress_bar.progress(progress)
        overall_log.append(f"Completed {i+1} of {num_urls} URLs ({int(progress*100)}% done)")
        log_area.text("\n".join(overall_log))
        time.sleep(0.1)  # Small delay for UI updates

    # Mark that all transcripts are done (to show ZIP download option).
    st.session_state.transcript_all_done = True

    # Prepare a DataFrame for logging/preview if needed.
    df = pd.DataFrame(batch_transcripts)

    # For UI preview, build a truncated transcript summary.
    def truncate_and_append(text, length=100, suffix="..."):
        return text[:length] + suffix if len(text) > length else text

    df_table = copy.deepcopy(df).astype(str)
    if "transcript" in df_table.columns:
        df_table["transcript"] = df_table["transcript"].apply(lambda x: truncate_and_append(x))
    st.session_state.transcript_data_table = df_table

    # Prepare a dictionary of transcripts keyed by video title.
    transcripts_by_video = {}
    for entry in batch_transcripts:
        video_title = entry.get("video_title", "Unknown Title")
        transcript_data = entry.get("transcript", "")
        if isinstance(transcript_data, list):
            transcript_text = " ".join([seg.get("text", "") for seg in transcript_data])
        else:
            transcript_text = str(transcript_data)
        transcripts_by_video[video_title] = transcript_text

    st.session_state.transcripts_by_video = transcripts_by_video

    # Also prepare one large text blob if needed.
    txt_output = convert_to_txt(df)
    st.session_state.transcript_data_download = txt_output

    # Save the complete log in session state (if needed for later reference).
    st.session_state.transcript_log = "\n".join(overall_log)
