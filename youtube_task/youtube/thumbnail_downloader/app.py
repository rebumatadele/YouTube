import streamlit as st
from thumbnail_downloader.state import state_init
from thumbnail_downloader.callbacks import fetch_thumbnails

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
    st.markdown('<div class="title-container"><h1>📸 YouTube Thumbnail Downloader</h1></div>', unsafe_allow_html=True)
    st.write("Fetch and download thumbnails from YouTube videos effortlessly.")

    # Input Section
    st.markdown("### 🔗 Enter YouTube URLs or Upload File")
    with st.container():
        # Set a default placeholder URL if no text is present.
        default_placeholder = "https://www.youtube.com/watch?v=6SpNMNQAVnI"
        text_urls = st.text_area(
            label="YouTube URLs (comma-separated)",
            value=st.session_state.get("thumbnail_text_input_urls", default_placeholder),
            placeholder="https://www.youtube.com/watch?v=xxxx, https://www.youtube.com/shorts/yyyy, ...",
            key="thumbnail_urls_input",
            height=100,
        )
        uploaded_file = st.file_uploader("📂 Upload a TXT file with YouTube URLs", type=["txt"], key="thumbnails_file_uploader")

    # Fetch Thumbnails Button
    st.markdown("### 📸 Fetch Thumbnails")
    fetch_btn = st.button(
        "🔍 Fetch Thumbnails",
        type="primary",
        key="button-fetch",
    )

    # Process if button is clicked
    if fetch_btn:
        fetch_thumbnails(uploaded_file, text_urls)

    # Thumbnails Display Section
    st.markdown("### 📷 Thumbnail Preview")
    if "thumbnail_savepaths" in st.session_state and st.session_state.thumbnail_savepaths:
        for ind, thumbnail_savepath in enumerate(st.session_state.thumbnail_savepaths):
            title = st.session_state.thumbnail_data_entries[ind].get("video_title", "Unknown Title")
            with st.container():
                col1, col2 = st.columns([3, 5])
                with col1:
                    st.image(thumbnail_savepath, caption=title, use_column_width=True)
                with col2:
                    try:
                        with open(thumbnail_savepath, "rb") as file:
                            st.download_button(
                                label="📥 Download Thumbnail",
                                data=file,
                                file_name=f"{title}.jpg",
                                mime="image/jpg",
                                type="primary",
                            )
                    except Exception as e:
                        st.error(f"Error downloading thumbnail: {e}")

    # Download Zip Button
    st.markdown("### 📥 Download All Thumbnails")
    if "thumbnails_zip_path" in st.session_state and st.session_state.thumbnail_fetch_count > 0:
        try:
            with open(st.session_state.thumbnails_zip_path, "rb") as file:
                st.download_button(
                    label="📥 Download All as ZIP",
                    data=file,
                    file_name="thumbnails.zip",
                    mime="application/zip",
                    type="primary",
                    key="button-download",
                )
        except Exception as e:
            st.error(f"Error downloading zip: {e}")
