import streamlit as st
from channel_downloader.callbacks import fetch_channel_videos
from channel_downloader.state import state_init, state_reset

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
    st.markdown('<div class="title-container"><h1>📺 YouTube Channel Video IDs</h1></div>', unsafe_allow_html=True)
    st.write("Fetch and download video IDs from a YouTube channel effortlessly.")

    # Input Section
    st.markdown("### 🔗 Enter YouTube Channel Name")
    channel_name = st.text_input(
        label="YouTube Channel Name",
        value=st.session_state.channel_name,
        placeholder="e.g., Sam Eckholm",
    )

    # Fetch Video IDs Button
    st.markdown("### 📋 Fetch Channel Videos")
    fetch_btn = st.button(
        "🔍 Fetch Video IDs",
        type="primary",
        key="button-fetch",
    )

    # Process if button is clicked
    if fetch_btn:
        if channel_name != st.session_state.channel_name:
            state_reset()
        if st.session_state.channel_fetch_count == 0:
            df_table, df_download = fetch_channel_videos(channel_name)
            st.session_state.channel_data_table = df_table
            st.session_state.channel_data_download = df_download
            st.session_state.channel_fetch_count += 1

    # Video ID List Preview
    st.markdown("### 🎥 Video ID List")
    if "channel_data_table" in st.session_state and not st.session_state.channel_data_table.empty:
        st.dataframe(st.session_state.channel_data_table)

    # Download Button
    st.markdown("### 📥 Download Video IDs")
    st.download_button(
        label="📥 Download Video IDs",
        data=st.session_state.channel_data_download,
        file_name="channel_data.csv",
        mime="text/csv",
        type="primary",
        key="button-download",
        disabled=False if st.session_state.channel_fetch_count > 0 else True,
    )
