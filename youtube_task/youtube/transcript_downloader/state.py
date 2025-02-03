import streamlit as st
import pandas as pd

def state_init():
    if "transcript_raw_urls" not in st.session_state:
        st.session_state.transcript_raw_urls = ""
    if "transcript_data_table" not in st.session_state:
        st.session_state.transcript_data_table = pd.DataFrame(columns=["youtube_url", "video_id", "transcript"])
    if "transcript_data_download" not in st.session_state:
        st.session_state.transcript_data_download = ""
    if "transcripts_by_video" not in st.session_state:
        st.session_state.transcripts_by_video = {}
    if "transcript_log" not in st.session_state:
        st.session_state.transcript_log = ""
    if "transcript_all_done" not in st.session_state:
        st.session_state.transcript_all_done = False
