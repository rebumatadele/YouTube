import streamlit as st
from transcript_downloader.callbacks import fetch_transcripts_and_prepare_downloads
from transcript_downloader.state import state_init
from io import BytesIO
import zipfile

def app():
    state_init()

    # Custom Styling for Better UI
    st.markdown(
        """
        <style>
        /* Hide Streamlit footer & menu */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Style buttons */
        .stButton>button {
            border-radius: 10px;
            padding: 10px;
            font-size: 16px;
            font-weight: bold;
        }

        /* Fetch button */
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

        /* Input styles */
        .stTextArea>div>textarea, .stTextInput>div>div>input {
            font-size: 16px !important;
            border-radius: 8px;
        }

        /* Center align title */
        .title-container {
            text-align: center;
        }

        /* Reduce spacing */
        .block-container {
            padding-top: 1rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Page Title with Icon
    st.markdown('<div class="title-container"><h1>📜 YouTube Transcript Downloader</h1></div>', unsafe_allow_html=True)
    st.write("Fetch and download transcripts from YouTube videos effortlessly.")

    # Input Section for URLs
    st.markdown("### 🔗 Enter YouTube URLs or Upload File")
    with st.container():
        manual_urls = st.text_area(
            label="YouTube URLs (comma‑separated)",
            value=st.session_state.transcript_raw_urls,
            placeholder="https://www.youtube.com/watch?v=xxxx, https://www.youtube.com/shorts/yyyy, ...",
            key="transcript_urls_input",
            height=100,
        )
        uploaded_file = st.file_uploader("📂 Upload a TXT file with YouTube URLs", type=["txt"], key="transcripts_file_uploader")

    # Fetch Transcript Button
    st.markdown("### 📜 Fetch Transcripts")
    fetch_btn = st.button(
        "🔍 Fetch Transcripts",
        type="primary",
        key="button-fetch",
    )

    if fetch_btn:
        # This function handles sanitation, transcript fetching (with retries, logs, progress updates),
        # and prepares downloadable content.
        fetch_transcripts_and_prepare_downloads(uploaded_file, manual_urls)

    # If transcripts have been fetched, allow the user to switch between them:
    if st.session_state.transcripts_by_video:
        st.markdown("### ✏️ Edit & Preview Transcript")
        # Build a dropdown list of video titles as they become available.
        video_titles = list(st.session_state.transcripts_by_video.keys())
        selected_video = st.selectbox("Select Video Transcript", video_titles, key="transcript_select")
        # Show the transcript in an editable text area.
        transcript_text = st.text_area("Transcript", value=st.session_state.transcripts_by_video[selected_video], height=400, key="transcript_edit_area")
        # Save any changes back to session state.
        st.session_state.transcripts_by_video[selected_video] = transcript_text

        # Provide an individual download button for the selected transcript.
        st.markdown("### 📥 Download Selected Transcript")
        st.download_button(
            label="Download Transcript",
            data=st.session_state.transcripts_by_video[selected_video],
            file_name=f"{selected_video}.txt",
            mime="text/plain",
            key="individual-download"
        )

        # Show ZIP download option only after all URLs have been processed.
        if st.session_state.get("transcript_all_done", False):
            st.markdown("### 📥 Download All Transcripts as ZIP")
            # Build a ZIP file in memory.
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for title, transcript in st.session_state.transcripts_by_video.items():
                    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title).strip()
                    filename = f"{safe_title}.txt"
                    zip_file.writestr(filename, transcript)
            zip_buffer.seek(0)
            st.download_button(
                label="Download ZIP",
                data=zip_buffer,
                file_name="transcripts.zip",
                mime="application/zip",
                key="zip-download"
            )
