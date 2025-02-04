import yt_dlp
import scrapetube
from typing import Tuple
import streamlit as st
import tempfile

def get_channel_id_from_name(channel_name: str) -> str | None:
    """
    Uses yt-dlp to search for the channel by name and returns its channel_id.
    If an error occurs that suggests a signin issue and cookies are available in session state,
    a retry is attempted with the cookiefile option attached.
    """
    # Base options
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
        "force_generic_extractor": True,
    }
    
    # If cookies are available, attach them.
    cookies = st.session_state.get("youtube_cookies", "").strip() if "youtube_cookies" in st.session_state else ""
    if cookies:
        try:
            cookie_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
            cookie_file.write(cookies.encode("utf-8"))
            cookie_file.close()
            ydl_opts["cookiefile"] = cookie_file.name
            st.write("DEBUG: Attached cookie file for channel lookup:", cookie_file.name)
        except Exception as ce:
            st.warning("Failed to attach cookies in channel lookup: " + str(ce))
    
    # Try the initial extraction
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch1:{channel_name}", download=False)
            return info["entries"][0]["channel_id"]
        except Exception as e:
            st.write("Channel search error: " + str(e))
            # If error message suggests signin and cookies exist but were not attached, try again.
            if "signin" in str(e).lower() and cookies and not ydl_opts.get("cookiefile"):
                st.write("Retrying channel search with cookies...")
                try:
                    cookie_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
                    cookie_file.write(cookies.encode("utf-8"))
                    cookie_file.close()
                    ydl_opts["cookiefile"] = cookie_file.name
                    st.write("DEBUG: Attached cookie file on retry:", cookie_file.name)
                except Exception as ce:
                    st.warning("Failed to attach cookies on retry: " + str(ce))
                with yt_dlp.YoutubeDL(ydl_opts) as ydl_retry:
                    try:
                        info = ydl_retry.extract_info(f"ytsearch1:{channel_name}", download=False)
                        return info["entries"][0]["channel_id"]
                    except Exception as e2:
                        st.write("Retry with cookies failed: " + str(e2))
                        return None
            return None

def extract_title(raw_title) -> str:
    """
    Extracts a plain text title from the structured title object.
    """
    if isinstance(raw_title, str):
        return raw_title
    if isinstance(raw_title, dict):
        if "runs" in raw_title and isinstance(raw_title["runs"], list):
            return "".join([run.get("text", "") for run in raw_title["runs"]])
        if "accessibility" in raw_title:
            acc_data = raw_title["accessibility"].get("accessibilityData", {})
            label = acc_data.get("label")
            if label:
                return label
    return str(raw_title)

def get_videourl_from_channel_id(channel_id: str) -> Tuple[list, list, list] | Tuple[None, None, None]:
    try:
        videos = scrapetube.get_channel(channel_id)
        video_urls = []
        video_ids = []
        video_titles = []  # New list for titles
        for video in videos:
            vid = video["videoId"]
            raw_title = video.get("title", "No Title")
            title = extract_title(raw_title)
            vurl = "https://www.youtube.com/watch?v=" + vid
            video_ids.append(vid)
            video_urls.append(vurl)
            video_titles.append(title)
        return video_ids, video_urls, video_titles
    except Exception as e:
        st.write(f"FAILURE: get_videourls_from_channel_id failed with exception {e}")
        return None, None, None

def get_channel_videos(channel_name: str) -> Tuple[list, list, list] | Tuple[None, None, None]:
    try:
        st.write("INFO: starting channel video id puller...")
        channel_id = get_channel_id_from_name(channel_name)
        if channel_id is not None:
            video_ids, video_urls, video_titles = get_videourl_from_channel_id(channel_id)
            if video_ids is not None and video_urls is not None and video_titles is not None:
                st.write("...done!")
                return video_ids, video_urls, video_titles
            else:
                st.write("...done!")
                return None, None, None
        else:
            st.write("...done!")
            return None, None, None
    except Exception as e:
        st.write(f"FAILURE: get_channel_videos failed with exception {e}")
        return None, None, None
