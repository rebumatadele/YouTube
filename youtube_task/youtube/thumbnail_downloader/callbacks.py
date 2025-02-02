import os
from thumbnail_downloader.yt_thumbnail_downloader import get_batch_thumbnails
from thumbnail_downloader.zip import zip_images
from thumbnail_downloader.state import reset_state
import streamlit as st
from io import StringIO
import tempfile

def urls_normalizer(uploaded_file: "st.uploaded", text_urls: str) -> list:
    youtube_urls = []
    # If a file is uploaded, do not allow manual URL entry.
    if uploaded_file is not None:
        if text_urls and text_urls.strip():
            st.warning("You can enter URLs manually or from file but not both", icon="⚠️")
            st.stop()
        if uploaded_file.type == "text/plain":
            stringio = StringIO(uploaded_file.read().decode("utf-8"))
            for line in stringio:
                youtube_urls.append(line.strip())
    # If manual URLs are entered:
    if text_urls and text_urls.strip():
        if uploaded_file is not None:
            st.warning("You can enter URLs manually or from file but not both", icon="⚠️")
            st.stop()
        try:
            youtube_urls = [v.strip() for v in text_urls.split(",")]
        except Exception:
            st.warning("Please check your manually entered URLs", icon="⚠️")
            st.stop()
    return youtube_urls

def fetch_logic(youtube_urls: list) -> None:
    # Reset state if URLs have changed
    if youtube_urls != st.session_state.get("thumbnail_raw_urls"):
        st.session_state.thumbnail_raw_urls = youtube_urls
        reset_state()
    
    if st.session_state.thumbnail_fetch_count == 0:
        # Create a temporary directory for saving thumbnails.
        savedir = tempfile.mkdtemp()
        thumbnail_savepaths, thumbnail_data_entries = get_batch_thumbnails(youtube_urls, savedir)
        st.session_state.thumbnail_savepaths = thumbnail_savepaths
        st.session_state.thumbnail_data_entries = thumbnail_data_entries
        st.session_state.thumbnail_fetch_count += 1

        # Create zip file path in the temporary directory.
        st.session_state.thumbnails_zip_path = os.path.join(savedir, "thumbnails.zip")
        zip_images(thumbnail_savepaths)

def fetch_thumbnails(uploaded_file, text_urls):
    youtube_urls = urls_normalizer(uploaded_file, text_urls)
    fetch_logic(youtube_urls)
