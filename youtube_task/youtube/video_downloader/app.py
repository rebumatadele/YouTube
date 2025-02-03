import streamlit as st
from video_downloader.config import video_choices
from video_downloader.callbacks import callback_download_video
from video_downloader.state import state_init, default_clip_video_path

def app():
    state_init()

    # Custom CSS Styling for better UI
    st.markdown(
        """
        <style>
        /* Hide the Streamlit footer and menu */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Improve button styling */
        .stButton>button {
            border-radius: 10px;
            padding: 10px;
            font-size: 16px;
            font-weight: bold;
        }

        /* Primary button */
        div:has(#youtube_download_fetch_button) + div button {
            background-color: #FF0000 !important;
            color: white !important;
            border-color: #FF0000 !important;
        }

        /* Download button */
        div:has(#button-download) + div button {
            background-color: #008000 !important;
            color: white !important;
            border-color: #008000 !important;
        }

        /* Input field styles */
        .stTextInput>div>div>input {
            font-size: 16px !important;
            border-radius: 8px;
        }

        /* Center align the main title */
        .title-container {
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # App Title with Icon
    st.markdown('<div class="title-container"><h1>🎞️ YouTube Video Downloader</h1></div>', unsafe_allow_html=True)
    st.write("Download YouTube & Shorts videos in various resolutions.")

    # Input Fields & Selection
    st.markdown("### 🔗 Enter YouTube URL & Select Resolution")
    with st.container():
        col_url, col_res = st.columns([3, 1])
        with col_url:
            url_input = st.text_input(
                label="YouTube URL",
                value="https://www.youtube.com/watch?v=6SpNMNQAVnI",
                placeholder="Paste a YouTube URL here...",
                key="youtube_download_text_input"
            )
        with col_res:
            resolution_dropdown = st.selectbox(
                label="Resolution",
                options=video_choices,
                index=st.session_state.youtube_download_resolution_index,
            )

    # Fetch & Download Video Button
    st.markdown("### 🎬 Start Download")
    fetch_btn = st.button(
        "🔽 Fetch & Download Video",
        type="primary",
        key="youtube_download_fetch_button",
        on_click=callback_download_video,
        args=(url_input, resolution_dropdown),
    )

    # Single progress display container – shown only while a download is in progress.
    if "download_status" in st.session_state and st.session_state.download_status:
        with st.container():
            st.markdown("### ⏳ Download Progress")
            st.progress(st.session_state.download_progress)
            st.write(st.session_state.download_status)

    # Video preview and download button – shown only after a successful download.
    if (
        "youtube_download_location" in st.session_state
        and st.session_state.youtube_download_location
        and st.session_state.youtube_download_location != default_clip_video_path
    ):
        st.markdown("### ✅ Download Ready")
        # First show the video preview...
        st.video(st.session_state.youtube_download_location, format="video/mp4")
        # ...and then the download button below the video.
        with open(st.session_state.youtube_download_location, "rb") as file:
            st.download_button(
                label="📥 Download Video",
                data=file,
                file_name=st.session_state.youtube_download_location.split("/")[-1],
                mime="video/mp4",
                type="primary",
                key="button-download",
            )
