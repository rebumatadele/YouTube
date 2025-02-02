import os
from video_downloader.config import video_choices, default_clip_video_path
import streamlit as st
import tempfile

def ensure_file_exists(filepath):
    """Ensure the file exists by creating its directory and an empty file if needed."""
    directory = os.path.dirname(filepath)
    os.makedirs(directory, exist_ok=True)
    if not os.path.exists(filepath):
        with open(filepath, "wb") as f:
            pass  # Create an empty file

def default_youtube_download_location():
    with tempfile.TemporaryDirectory() as tmpdirname:
        return tmpdirname

def state_init():
    if "resolution_dropdown" not in st.session_state:
        st.session_state.resolution_dropdown = video_choices
    if "youtube_download_location" not in st.session_state:
        # Ensure the default blank file exists before setting the location
        ensure_file_exists(default_clip_video_path)
        st.session_state.youtube_download_location = default_clip_video_path
    if "youtube_download_resolution_index" not in st.session_state:
        st.session_state.youtube_download_resolution_index = 0
