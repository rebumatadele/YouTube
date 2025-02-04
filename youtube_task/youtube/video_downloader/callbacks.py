import streamlit as st
from video_downloader.yt_download import download_video
from video_downloader.state import default_youtube_download_location
from video_downloader.config import video_choices
from persistence import load_persistent_state, save_persistent_state

def callback_download_video(url_input: str, resolution_dropdown: str) -> None:
    # Reset progress display in session state
    st.session_state.download_progress = 0
    st.session_state.download_status = "Starting download..."

    # Initialize persistent progress for this download (for a single file, total = 1)
    persistent_state = st.session_state.get("persistent_state", load_persistent_state())
    persistent_state["download_progress"]["total"] = 1
    persistent_state["download_progress"]["downloaded"] = 0
    save_persistent_state(persistent_state)
    st.session_state.persistent_state = persistent_state

    # Create a progress bar and a status text placeholder.
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Download the video with progress tracking.
    temporary_video_location = download_video(
        url_input,
        default_youtube_download_location(),
        resolution_dropdown,
        progress_bar,
        status_text
    )

    # Update persistent state when the download is successful.
    persistent_state["download_progress"]["downloaded"] = 1
    save_persistent_state(persistent_state)

    # Store the download location and selected resolution index in session state.
    st.session_state.youtube_download_location = temporary_video_location
    st.session_state.youtube_download_resolution_index = video_choices.index(resolution_dropdown)
    st.session_state.download_status = "✅ Download complete!"
    st.session_state.download_progress = 1.0
