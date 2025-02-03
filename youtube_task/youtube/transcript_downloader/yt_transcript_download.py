import json
import re
import time
from typing import List, Dict
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import streamlit as st
import yt_dlp
import requests

def is_valid_youtube_url(url: str) -> bool:
    if not isinstance(url, str):
        return False
    # A simple pattern; adjust as needed.
    pattern = r"^https://www\.youtube\.com/watch\?v=[A-Za-z0-9_-]{11}$"
    if "shorts" in url:
        pattern = r"^https://www\.youtube\.com/shorts/[A-Za-z0-9_-]{11}$"
    return re.match(pattern, url) is not None

def get_video_title(video_id: str) -> str:
    """Use yt-dlp to extract the video title from YouTube."""
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': True,
    }
    url = f"https://www.youtube.com/watch?v={video_id}"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info.get("title", f"Video {video_id}")
        except Exception:
            return f"Video {video_id}"

def get_subtitles_with_yt_dlp(video_url: str) -> str:
    """
    Attempt to fetch subtitles (captions) using yt-dlp.
    Returns a plain text transcript if available, or an empty string otherwise.
    This function now supports both VTT and JSON subtitle formats.
    """
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,         # try to get manually provided subtitles
        'writeautomaticsub': True,      # fallback to auto-generated subtitles if needed
        'subtitleslangs': ['en', 'es'],  # try English or Spanish (adjust as needed)
        'extract_flat': False,
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
    except Exception as e:
        st.warning(f"yt-dlp extraction failed for fallback: {e}")
        return ""
    # Check for subtitles in the info dictionary.
    subtitles = info.get("subtitles", {})
    automatic_captions = info.get("automatic_captions", {})
    subtitle_url = None
    if 'en' in subtitles:
        subtitle_url = subtitles['en'][0]['url']
    elif 'en' in automatic_captions:
        subtitle_url = automatic_captions['en'][0]['url']
    elif subtitles:
        first_lang = next(iter(subtitles))
        subtitle_url = subtitles[first_lang][0]['url']
    elif automatic_captions:
        first_lang = next(iter(automatic_captions))
        subtitle_url = automatic_captions[first_lang][0]['url']

    if subtitle_url:
        try:
            r = requests.get(subtitle_url)
            if not r.ok:
                return ""
            text = r.text
            # Check if the response is JSON (starts with '{' after stripping)
            if text.lstrip().startswith('{'):
                try:
                    data = json.loads(text)
                    # If the JSON contains an "events" key, process it.
                    if "events" in data:
                        transcript_lines = []
                        for event in data["events"]:
                            # Each event may have a "segs" list; join the "utf8" parts.
                            segs = event.get("segs", [])
                            line = "".join(seg.get("utf8", "") for seg in segs)
                            if line.strip():
                                transcript_lines.append(line.strip())
                        return "\n".join(transcript_lines)
                except Exception as je:
                    st.warning(f"Failed to parse JSON subtitles: {je}")
                    # Fall through to attempt VTT processing.
            # Otherwise, assume it's VTT and perform minimal processing.
            lines = text.splitlines()
            transcript_lines = []
            for line in lines:
                if "-->" in line:
                    continue
                if line.strip() == "" or "WEBVTT" in line:
                    continue
                transcript_lines.append(line)
            return "\n".join(transcript_lines)
        except Exception as e:
            st.warning(f"Failed to download subtitles via yt-dlp: {e}")
            return ""
    return ""


def get_single_transcript(youtube_url: str) -> dict:
    if not is_valid_youtube_url(youtube_url):
        st.error(f"Invalid URL: {youtube_url}")
        return {
            "youtube_url": youtube_url,
            "video_id": None,
            "video_title": "Invalid URL",
            "transcript": "Invalid URL format."
        }
    # Extract video ID
    video_id = youtube_url.split("/")[-1] if "shorts" in youtube_url else youtube_url.split("=")[-1]
    # Get the proper video title using yt-dlp.
    video_title = get_video_title(video_id)
    
    max_retries = 5
    delay = 1  # initial delay in seconds
    for attempt in range(max_retries):
        try:
            # Try to force language 'en' (or try alternatives).
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'es', 'auto'])
            return {
                "youtube_url": youtube_url,
                "video_id": video_id,
                "video_title": video_title,
                "transcript": transcript,
            }
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            # Fallback to yt-dlp method
            fallback_transcript = get_subtitles_with_yt_dlp(youtube_url)
            if fallback_transcript:
                return {
                    "youtube_url": youtube_url,
                    "video_id": video_id,
                    "video_title": video_title,
                    "transcript": fallback_transcript,
                }
            else:
                return {
                    "youtube_url": youtube_url,
                    "video_id": video_id,
                    "video_title": video_title,
                    "transcript": f"Transcript not available: {e}"
                }
        except Exception as e:
            st.warning(f"Attempt {attempt+1} for {youtube_url} failed: {e}")
            time.sleep(delay)
            delay *= 2  # exponential backoff
    return {
        "youtube_url": youtube_url,
        "video_id": video_id,
        "video_title": video_title,
        "transcript": "Failed to retrieve transcript after multiple attempts."
    }

def get_batch_transcripts(youtube_urls: List[str]) -> List[Dict]:
    entries = []
    for url in youtube_urls:
        sanitized_url = url.strip()
        if not sanitized_url:
            continue
        entry = get_single_transcript(sanitized_url)
        if entry is not None:
            entries.append(entry)
    return entries
