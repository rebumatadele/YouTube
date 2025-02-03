from channel_downloader.yt_channel_download import get_channel_videos
import pandas as pd
import streamlit as st

@st.cache_data
def convert_df(df: pd.DataFrame) -> bytes:
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")

def fetch_channel_videos(channel_name: str):
    # Now get three outputs: video_ids, video_urls, video_titles
    video_ids, video_urls, video_titles = get_channel_videos(channel_name)
    if video_ids is not None and video_urls is not None and video_titles is not None:
        # Build DataFrame with three columns
        df_table = pd.DataFrame({
            "youtube_url": video_urls,
            "video_id": video_ids,
            "video_title": video_titles,
        })
        df_download = convert_df(df_table)
        return df_table, df_download
    return None, None
