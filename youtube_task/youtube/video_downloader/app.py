import streamlit as st
from video_downloader.config import video_choices
from video_downloader.callbacks import callback_download_video
from video_downloader.state import state_init

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
        div:has(#button-fetch) + div button {
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
        video_download_col_a, video_download_col_b = st.columns([3, 1])
        with video_download_col_a:
            url_input = st.text_input(
                label="YouTube URL",
                value="https://www.youtube.com/shorts/F3JJy79I7Tg",
                placeholder="Paste a YouTube URL here...",
                key="youtube_download_text_input"
            )
        with video_download_col_b:
            resolution_dropdown = st.selectbox(
                label="Resolution",
                options=video_choices,
                index=st.session_state.youtube_download_resolution_index,
            )

    # Fetch Video Button
    st.markdown("### 🎬 Start Download")
    fetch_btn = st.button(
        "🔽 Fetch & Download Video",
        type="primary",
        key="youtube_download_fetch_button",
        on_click=callback_download_video,
        args=(url_input, resolution_dropdown),
    )

    # Progress and Status UI
    if "download_status" in st.session_state:
        st.markdown("### ⏳ Download Progress")
        st.progress(st.session_state.download_progress)
        st.text(st.session_state.download_status)

    # Download & Video Preview Section
    if "youtube_download_location" in st.session_state and st.session_state.youtube_download_location:
        st.markdown("### ✅ Download Ready")
        with open(st.session_state.youtube_download_location, "rb") as file:
            st.download_button(
                label="📥 Download Video",
                data=file,
                file_name=st.session_state.youtube_download_location.split("/")[-1],
                mime="video/mp4",
                type="primary",
                key="button-download",
            )

        st.video(st.session_state.youtube_download_location, format="video/mp4")
