import streamlit as st
from transcript_downloader.callbacks import fetch_transcripts
from transcript_downloader.state import state_init

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

    # Input Section
    st.markdown("### 🔗 Enter YouTube URLs or Upload File")
    with st.container():
        text_urls = st.text_area(
            label="YouTube URLs (comma-separated)",
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

    # Process if button is clicked
    if fetch_btn:
        _, txt_output = fetch_transcripts(uploaded_file, text_urls)
        st.session_state.transcript_data_download = txt_output

    # Editable Transcript Preview
    st.markdown("### ✏️ Edit & Preview Transcripts")
    if "transcript_data_download" in st.session_state:
        edited_transcript = st.text_area(
            label="Edit transcript before downloading",
            value=st.session_state.transcript_data_download,
            height=400,
            key="transcript_edit_area",
        )

        # Save edited text
        st.session_state.transcript_data_download = edited_transcript

        # Download Button
        st.markdown("### 📥 Download Transcripts")
        st.download_button(
            label="📥 Download Transcripts",
            data=st.session_state.transcript_data_download,
            file_name="transcripts.txt",
            mime="text/plain",
            type="primary",
            key="button-download",
        )
