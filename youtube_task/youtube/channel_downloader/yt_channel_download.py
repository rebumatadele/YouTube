import yt_dlp
import scrapetube
from typing import Tuple

def get_channel_id_from_name(channel_name: str) -> str | None:
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
        "force_generic_extractor": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch1:{channel_name}", download=False)
            return info["entries"][0]["channel_id"]
        except Exception as e:
            print(f"FAILURE: get_channel_id_from_name failed with exception {e}")
            return None

def extract_title(raw_title) -> str:
    """
    Extracts a plain text title from the structured title object.
    """
    # If raw_title is already a string, return it directly.
    if isinstance(raw_title, str):
        return raw_title

    # If it's a dict, try to extract the text from "runs" if available.
    if isinstance(raw_title, dict):
        if "runs" in raw_title and isinstance(raw_title["runs"], list):
            # Join all text pieces (in case there are multiple runs)
            return "".join([run.get("text", "") for run in raw_title["runs"]])
        # As a fallback, try getting the accessibility label
        if "accessibility" in raw_title:
            acc_data = raw_title["accessibility"].get("accessibilityData", {})
            label = acc_data.get("label")
            if label:
                return label
    # Fallback: convert to string
    return str(raw_title)

def get_videourl_from_channel_id(channel_id: str) -> Tuple[list, list, list] | Tuple[None, None, None]:
    try:
        videos = scrapetube.get_channel(channel_id)
        video_urls = []
        video_ids = []
        video_titles = []  # New list for titles
        for video in videos:
            vid = video["videoId"]
            # Use our helper to extract the title text.
            raw_title = video.get("title", "No Title")
            title = extract_title(raw_title)
            vurl = "https://www.youtube.com/watch?v=" + vid
            video_ids.append(vid)
            video_urls.append(vurl)
            video_titles.append(title)
        return video_ids, video_urls, video_titles
    except Exception as e:
        print(f"FAILURE: get_videourls_from_channel_id failed with exception {e}")
        return None, None, None

def get_channel_videos(channel_name: str) -> Tuple[list, list, list] | Tuple[None, None, None]:
    try:
        print("INFO: starting channel video id puller...")
        channel_id = get_channel_id_from_name(channel_name)
        if channel_id is not None:
            video_ids, video_urls, video_titles = get_videourl_from_channel_id(channel_id)
            if video_ids is not None and video_urls is not None and video_titles is not None:
                print("...done!")
                return video_ids, video_urls, video_titles
            else:
                print("...done!")
                return None, None, None
        else:
            print("...done!")
            return None, None, None
    except Exception as e:
        print(f"FAILURE: get_channel_videos failed with exception {e}")
        return None, None, None
