import os
import pandas as pd
import streamlit as st
import time
import copy
from transcript_downloader.yt_transcript_download import get_single_transcript
from persistence import load_persistent_state, save_persistent_state

def convert_to_txt(df: pd.DataFrame) -> str:
    """
    Utility function (unchanged). Converts a DataFrame to a big text block.
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
    """
    Modified to:
      1) Display skip/fetch messages in a single 'alert_placeholder'
         so that older alerts are replaced by new ones.
      2) Maintain a single 'partial_display_container' with a dropdown
         to select *any* already-downloaded transcript for preview.
    """

    # --- A) Gather the YouTube URLs ---
    youtube_urls = []
    if uploaded_file is not None:
        channel = os.path.splitext(uploaded_file.name)[0]
    else:
        channel = "individual"

    # If a file is uploaded
    if uploaded_file is not None:
        if text_urls and text_urls.strip():
            st.warning("Please provide URLs either manually or via file upload, not both.", icon="⚠️")
            st.stop()
        if uploaded_file.type == "text/plain":
            content = uploaded_file.read().decode("utf-8")
            file_urls = [u.strip() for u in content.split(",") if u.strip()]
            youtube_urls.extend(file_urls)

    # If manual text is provided
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

    # --- B) Load / init persistent storage
    persistent_state = st.session_state.get("persistent_state", load_persistent_state())
    if "transcripts" not in persistent_state:
        persistent_state["transcripts"] = {}

    if "downloaded_links" not in persistent_state:
        persistent_state["downloaded_links"] = []
    downloaded_urls_set = set(persistent_state["downloaded_links"])

    channel_dict = persistent_state["transcripts"].get(channel, {})

    # For building final summary
    batch_transcripts = []

    # Show a progress bar
    num_urls = len(youtube_urls)
    progress_bar = st.progress(0)

    # (1) Single placeholder for ephemeral alerts (info/skipping/fetched).
    alert_placeholder = st.empty()

    st.write(f"**Starting to fetch transcripts for {num_urls} URL(s) in channel '{channel}'.**")

    # --- C) Main loop with partial updates
    for i, url in enumerate(youtube_urls):
        # Overwrite the alert each iteration
        alert_placeholder.info(f"Processing {i+1}/{num_urls}: {url}")

        # 1) If this URL is already in downloaded_links, skip
        if url in downloaded_urls_set:
            alert_placeholder.warning(f"Skipping URL (already downloaded): {url}")
            progress_bar.progress((i + 1) / num_urls)
            time.sleep(1)
            continue

        # Otherwise, fetch the transcript
        transcript_entry = get_single_transcript(url)
        batch_transcripts.append(transcript_entry)

        video_id = transcript_entry.get("video_id")
        video_title = transcript_entry.get("video_title", "Unknown Title")
        raw_data = transcript_entry.get("transcript", "")

        # If video_id is in channel_dict, skip
        if video_id and video_id in channel_dict:
            alert_placeholder.info(f"Skipping '{video_title}' (already fetched by video_id).")
        else:
            # Convert list to text
            if isinstance(raw_data, list):
                transcript_text = " ".join(seg.get("text", "") for seg in raw_data)
            else:
                transcript_text = str(raw_data)

            alert_placeholder.success(f"Fetched transcript for '{video_title}'. Saving...")

            if video_id:
                channel_dict[video_id] = {
                    "title": video_title,
                    "transcript": transcript_text
                }
                persistent_state["transcripts"][channel] = channel_dict

        # Add URL to downloaded set
        downloaded_urls_set.add(url)
        persistent_state["downloaded_links"] = list(downloaded_urls_set)

        # Save partial
        save_persistent_state(persistent_state)
        st.session_state["persistent_state"] = persistent_state

        # Reflect updated transcripts
        st.session_state["transcripts_by_video"] = persistent_state["transcripts"]

        # Update progress bar
        progress_bar.progress((i + 1) / num_urls)
        time.sleep(1)

    alert_placeholder.success("All transcripts processed!")
    st.session_state["transcript_all_done"] = True

    # Build a truncated DataFrame for final summary
    df = pd.DataFrame(batch_transcripts)
    def truncate_and_append(txt, length=100, suffix="..."):
        return txt[:length] + suffix if (isinstance(txt, str) and len(txt) > length) else txt

    df_table = copy.deepcopy(df).astype(str)
    if "transcript" in df_table.columns:
        df_table["transcript"] = df_table["transcript"].apply(lambda x: truncate_and_append(x))
    st.session_state["transcript_data_table"] = df_table

    st.session_state.transcripts_by_video = persistent_state["transcripts"]
    # final "Done" message
    st.success("Done fetching all transcripts!")