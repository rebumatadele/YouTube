import yt_dlp
from yt_dlp import YoutubeDL
import re
import os
import streamlit as st
from video_downloader.state import default_youtube_download_location
from persistence import load_persistent_state, save_persistent_state
import tempfile

def is_valid_youtube_url(url: str) -> bool:
    if not isinstance(url, str):
        return False
    pattern = r"^https://www\.youtube\.com/watch\?v=[A-Za-z0-9_-]{11}$"
    if "shorts" in url:
        pattern = r"^https://www\.youtube\.com/shorts/[A-Za-z0-9_-]{11}$"
    return re.match(pattern, url) is not None

def download_video(url: str, savedir: str, resolution_dropdown: str, progress_bar, status_text, my_proxies: dict = {}) -> str:
    try:
        print("Downloading video from YouTube...")
        if not is_valid_youtube_url(url):
            raise ValueError(f"Invalid input URL: {url}")

        # Extract video info without downloading.
        with YoutubeDL() as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_id = info_dict.get("id", None)
            video_title = info_dict.get("title", None)
            video_title = re.sub(r"[^a-zA-Z0-9]", " ", video_title)
        
        # Construct a save path.
        savepath = os.path.join(savedir, f"{video_title or video_id}.mp4")
        
        def my_progress_hook(d):
            if d.get('status') == 'downloading':
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded_bytes = d.get('downloaded_bytes', 0)
                if total_bytes:
                    progress = downloaded_bytes / total_bytes
                    progress_bar.progress(progress)
                    percentage = int(progress * 100)
                    status_text.text(f"Downloading... {percentage}%")
            elif d.get('status') == 'finished':
                progress_bar.progress(1.0)
                status_text.text("✅ Download completed!")
        
        # Set yt-dlp options.
        ydl_opts = {
            "format": "best[ext=mp4]",
            "outtmpl": savepath,
            "progress_hooks": [my_progress_hook],
            "noplaylist": True,
            "postprocessors": [],
        }
        # Apply resolution filters if specified.
        if resolution_dropdown == "1080":
            ydl_opts["format"] = "best[height<=1080][ext=mp4]"
        elif resolution_dropdown == "720":
            ydl_opts["format"] = "best[height<=720][ext=mp4]"
        elif resolution_dropdown == "360":
            ydl_opts["format"] = "best[height<=360][ext=mp4]"
        
        # Attempt the download.
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        print("✅ Download complete!")
        return savepath

    except Exception as e:
        error_msg = f"Download failed for {url}: {e}"
        # Check if the error message indicates a signin problem and if we have cookies.
        if "signin" in str(e).lower() and st.session_state.get("youtube_cookies", "").strip():
            status_text.text("Detected signin error, retrying with cookies...")
            # Write cookies from session state to a temporary file.
            cookie_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
            cookie_file.write(st.session_state.youtube_cookies.encode("utf-8"))
            cookie_file.close()
            # Add the cookie file option.
            ydl_opts["cookiefile"] = cookie_file.name
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                status_text.text("✅ Download completed with cookies!")
                return savepath
            except Exception as e2:
                error_msg = f"Retry with cookies failed for {url}: {e2}"
        # Log error to a file.
        with open("data/download_errors.log", "a") as log_file:
            log_file.write(error_msg + "\n")
        # Update persistent state.
        persistent_state = st.session_state.get("persistent_state", load_persistent_state())
        if "failed_downloads" not in persistent_state:
            persistent_state["failed_downloads"] = []
        persistent_state["failed_downloads"].append({"url": url, "error": str(e)})
        save_persistent_state(persistent_state)
        status_text.text(error_msg)
        raise
