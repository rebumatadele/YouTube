import streamlit as st
from transcript_downloader.callbacks import fetch_transcripts_and_prepare_downloads
from transcript_downloader.state import state_init
from persistence import load_persistent_state, clear_persistent_state
from io import BytesIO
import zipfile

def app():
    state_init()

    # Load persistent state from disk
    persistent_state = load_persistent_state()
    st.session_state["persistent_state"] = persistent_state

    if persistent_state.get("transcripts"):
        st.session_state.transcripts_by_video = persistent_state["transcripts"]
    else:
        st.session_state.transcripts_by_video = {}

    # Button to clear persistent state
    if st.button("Clear Persistent State"):
        new_state = clear_persistent_state()
        st.session_state["persistent_state"] = new_state
        st.session_state.transcripts_by_video = {}
        st.experimental_rerun()

    st.markdown("<h1>📜 YouTube Transcript Downloader</h1>", unsafe_allow_html=True)

    # 1) Collect file or manual URLs
    manual_urls = st.text_area("Enter YouTube URLs (comma‑separated)", "", height=100)
    uploaded_file = st.file_uploader("Upload .txt with YouTube URLs", type=["txt"])

    # 2) Button to fetch them all (with partial updates)
    if st.button("Fetch Transcripts"):
        fetch_transcripts_and_prepare_downloads(uploaded_file, manual_urls)
        # Re-load persistent state to get final updates
        # persistent_state = load_persistent_state()
        # st.session_state["persistent_state"] = persistent_state
        # st.session_state["transcripts_by_video"] = persistent_state.get("transcripts", {})

    # 3) Single *final* dropdown for channels
    if st.session_state.transcripts_by_video:
        st.markdown("## View/Edit Downloaded Transcripts")
        channels = list(st.session_state.transcripts_by_video.keys())
        selected_channel = st.selectbox("Select Channel", channels, key="channel_select")

        videos_dict = st.session_state.transcripts_by_video[selected_channel]
        video_ids = list(videos_dict.keys())
        labels = [videos_dict[vid_id]["title"] for vid_id in video_ids]

        selected_label = st.selectbox("Select Video Transcript", labels, key="video_select")
        chosen_index = labels.index(selected_label)
        chosen_vid_id = video_ids[chosen_index]

        # Show the transcript
        transcript_text = videos_dict[chosen_vid_id]["transcript"]
        new_text = st.text_area("Transcript", transcript_text, height=300, key="transcript_text_area")

        # If user edits, update
        videos_dict[chosen_vid_id]["transcript"] = new_text
        st.session_state.transcripts_by_video[selected_channel] = videos_dict

        # Download single
        st.download_button(
            "Download This Transcript",
            data=new_text,
            file_name=f"{selected_label}.txt",
            mime="text/plain"
        )

        # Download all as ZIP
        st.markdown("### Download All Transcripts as ZIP")
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for ch_name, channel_data in st.session_state.transcripts_by_video.items():
                for vid_id, vid_info in channel_data.items():
                    vid_title = vid_info["title"]
                    text_data = vid_info["transcript"]
                    safe_title = "".join(c if c.isalnum() else "_" for c in vid_title).strip()
                    file_path = f"{ch_name}/{safe_title}.txt"
                    zip_file.writestr(file_path, text_data)
        zip_buffer.seek(0)
        st.download_button(
            "Download ZIP",
            data=zip_buffer,
            file_name="transcripts.zip",
            mime="application/zip"
        )
