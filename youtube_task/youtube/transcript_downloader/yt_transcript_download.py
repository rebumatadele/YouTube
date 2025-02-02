import re
from typing import List, Dict
from youtube_transcript_api import YouTubeTranscriptApi
import streamlit as st

def is_valid_youtube_url(url: str) -> bool:
    if not isinstance(url, str):
        return False
    pattern = r"^https://www\.youtube\.com/watch\?v=[A-Za-z0-9_-]{11}$"  # youtube vido ids are always 11 chars long
    if "shorts" in url:
        pattern = r"^https://www\.youtube\.com/shorts/[A-Za-z0-9_-]{11}$"  # youtube vido ids are always 11 chars long
    return re.match(pattern, url) is not None


def get_single_transcript(youtube_url: str) -> dict:
    if is_valid_youtube_url(youtube_url):
        video_id = youtube_url.split("/")[-1] if "shorts" in youtube_url else youtube_url.split("=")[-1]
        try:
            # Try forcing language 'en'
            video_transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            return {
                "youtube_url": youtube_url,
                "video_id": video_id,
                "video_title": f"Video {video_id}",
                "transcript": video_transcript,
            }
        except Exception as e:
            # Log the complete error so we can diagnose
            st.error(f"Error retrieving transcript for {youtube_url}: {e}")
            # If the error message contains "Subtitles are disabled", fall back; otherwise, return the error message
            if "Subtitles are disabled for this video" in str(e):
                return {
                    "youtube_url": youtube_url,
                    "video_id": video_id,
                    "video_title": f"Video {video_id}",
                    "transcript": "Subtitles are disabled for this video",
                }
            else:
                return {
                    "youtube_url": youtube_url,
                    "video_id": video_id,
                    "video_title": f"Video {video_id}",
                    "transcript": f"Error: {e}",
                }
    else:
        st.error(f"FAILURE: youtube_url is not valid - {youtube_url}")


def get_batch_transcripts(youtube_urls: List[str]) -> List[Dict]:
    try:
        entries = []
        for i, youtube_url in enumerate(youtube_urls):
            entry = get_single_transcript(youtube_url)
            if entry is not None:
                entries.append(entry)
        return entries
    except Exception as e:
        print(f"FAILURE: get_batch_transcripts function failed with exception {e}")
        return []
