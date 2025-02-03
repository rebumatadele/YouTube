import streamlit as st
from about.app import app as about_page
from video_downloader.app import app as video_downloader
from transcript_downloader.app import app as transcript_downloader
from thumbnail_downloader.app import app as thumbnail_downloader
from channel_downloader.app import app as channel_downloader

# Set page configuration with the new app name.
st.set_page_config(page_title="Youtube Task", layout="wide")

# Branding header in the sidebar.
st.sidebar.markdown("""
    <div style="text-align: center;">
        <h1 style="color: #FF0000;">🎬 Youtube Task</h1>
        <p style="font-size: 14px;">All your YouTube utilities in one place</p>
    </div>
    <hr>
""", unsafe_allow_html=True)

# Sidebar navigation options with icons.
page = st.sidebar.radio(
    "Navigation",
    options=["About", "Channel Downloader", "Video Downloader", "Transcript Downloader", "Thumbnail Downloader"],
    index=0,
    format_func=lambda x: {
        "About": "💡 About",
        "Channel Downloader": "📕 Channel Downloader",
        "Video Downloader": "🎞️ Video Downloader",
        "Transcript Downloader": "📜 Transcript Downloader",
        "Thumbnail Downloader": "📌 Thumbnail Downloader"
    }[x]
)

# Main content area
if page == "About":
    about_page()
elif page == "Channel Downloader":
    channel_downloader()
elif page == "Video Downloader":
    video_downloader()
elif page == "Transcript Downloader":
    transcript_downloader()
elif page == "Thumbnail Downloader":
    thumbnail_downloader()
