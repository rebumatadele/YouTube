import streamlit as st

def app():
    st.markdown(
        """
        <div style="text-align: center;">
            <h2>Welcome to Youtube Task</h2>
            <p style="font-size: 16px;">
                <strong>Download YouTube videos, transcripts, thumbnails, and channel data – all in one place.</strong>
            </p>
        </div>
        <hr>
        <h3>How It Works</h3>
        <ul>
            <li><strong>Video Downloader:</strong> Paste a YouTube or Shorts URL to download the video in your chosen resolution.</li>
            <li><strong>Transcript Downloader:</strong> Retrieve transcripts for multiple videos at once.</li>
            <li><strong>Thumbnail Downloader:</strong> Download thumbnails for selected videos.</li>
            <li><strong>Channel Downloader:</strong> Fetch all video IDs and URLs from a YouTube channel.</li>
        </ul>
        """, 
        unsafe_allow_html=True
    )
