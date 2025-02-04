import streamlit as st
from transcript_downloader.callbacks import fetch_transcripts_and_prepare_downloads
from transcript_downloader.state import state_init
from persistence import load_persistent_state, clear_persistent_state
from io import BytesIO
import zipfile

def app():
    state_init()
    
    # Load persistent state.
    persistent_state = load_persistent_state()
    st.session_state["persistent_state"] = persistent_state
    if persistent_state.get("transcripts"):
        st.session_state.transcripts_by_video = persistent_state["transcripts"]
    else:
        st.session_state.transcripts_by_video = {}
    
    # Button to clear persistent state.
    if st.button("Clear Persistent State"):
        new_state = clear_persistent_state()
        st.session_state["persistent_state"] = new_state
        st.session_state.transcripts_by_video = {}
        st.experimental_rerun()
    
    st.markdown('<div class="title-container"><h1>📜 YouTube Transcript Downloader</h1></div>', unsafe_allow_html=True)
    st.write("Fetch and download transcripts from YouTube videos effortlessly.")
    
    st.markdown("### 🔗 Enter YouTube URLs or Upload File")
    with st.container():
        manual_urls = st.text_area(
            label="YouTube URLs (comma‑separated)",
            value=st.session_state.get("transcript_raw_urls", ""),
            placeholder="https://www.youtube.com/watch?v=xxxx, https://www.youtube.com/shorts/yyyy, ...",
            key="transcript_urls_input",
            height=100,
        )
        uploaded_file = st.file_uploader("📂 Upload a TXT file with YouTube URLs", type=["txt"], key="transcripts_file_uploader")
    
    st.markdown("### 📜 Fetch Transcripts")
    fetch_btn = st.button("🔍 Fetch Transcripts", type="primary", key="button-fetch")
    if fetch_btn:
        fetch_transcripts_and_prepare_downloads(uploaded_file, manual_urls)
        persistent_state = load_persistent_state()
        st.session_state["persistent_state"] = persistent_state
        st.session_state.transcripts_by_video = persistent_state.get("transcripts", {})
    
    # If transcripts exist, show the grouped preview.
    if st.session_state.transcripts_by_video:
        st.markdown("### ✏️ Edit & Preview Transcript")
        channels = list(st.session_state.transcripts_by_video.keys())
        selected_channel = st.selectbox("Select Channel", channels, key="channel_select")
        videos_dict = st.session_state.transcripts_by_video.get(selected_channel, {})
        if videos_dict:
            video_titles = list(videos_dict.keys())
            selected_video = st.selectbox("Select Video Transcript", video_titles, key="transcript_select")
            transcript_text = st.text_area(
                "Transcript", 
                value=videos_dict[selected_video], 
                height=400, 
                key="transcript_edit_area"
            )
            videos_dict[selected_video] = transcript_text
            st.session_state.transcripts_by_video[selected_channel] = videos_dict
            
            st.markdown("### 📥 Download Selected Transcript")
            st.download_button(
                label="Download Transcript",
                data=videos_dict[selected_video],
                file_name=f"{selected_video}.txt",
                mime="text/plain",
                key="individual-download"
            )
        else:
            st.write("No transcripts found for this channel.")
        
        if st.session_state.get("transcript_all_done", False):
            st.markdown("### 📥 Download All Transcripts as ZIP")
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for channel, videos in st.session_state.transcripts_by_video.items():
                    for title, transcript in videos.items():
                        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title).strip()
                        filename = f"{channel}/{safe_title}.txt"
                        zip_file.writestr(filename, transcript)
            zip_buffer.seek(0)
            st.download_button(
                label="Download ZIP",
                data=zip_buffer,
                file_name="transcripts.zip",
                mime="application/zip",
                key="zip-download"
            )

if __name__ == "__main__":
    app()
