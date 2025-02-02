import yt_dlp
from yt_dlp import YoutubeDL
import re

def is_valid_youtube_url(url: str) -> bool:
    """Checks if the URL is a valid YouTube video URL."""
    if not isinstance(url, str):
        return False
    pattern = r"^https://www\.youtube\.com/watch\?v=[A-Za-z0-9_-]{11}$"
    if "shorts" in url:
        pattern = r"^https://www\.youtube\.com/shorts/[A-Za-z0-9_-]{11}$"
    return re.match(pattern, url) is not None

def download_video(url: str, savedir: str, resolution_dropdown: str, progress_bar, status_text, my_proxies: dict = {}) -> str:
    """Downloads a YouTube video without merging separate audio/video streams."""
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
        
        # Construct a save path. (Ensure savedir exists.)
        savepath = f"{savedir}/{video_title or video_id}.mp4"
        
        # Define a progress hook to update the UI.
        def my_progress_hook(d):
            if d.get('status') == 'downloading':
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                if total_bytes:
                    progress = d.get('downloaded_bytes', 0) / total_bytes
                    progress_bar.progress(progress)
                    status_text.text(f"Downloading... {d.get('downloaded_bytes', 0)} / {total_bytes} bytes")
            elif d.get('status') == 'finished':
                progress_bar.progress(1.0)
                status_text.text("✅ Download completed!")
        
        # Set yt-dlp options to download a self-contained MP4.
        # Using "best[ext=mp4]" downloads a single file and does not merge streams.
        ydl_opts = {
            "format": "best[ext=mp4]",
            "outtmpl": savepath,
            "progress_hooks": [my_progress_hook],
            "noplaylist": True,  # Only download a single video.
            "postprocessors": [],  # Do not process (merge) streams.
        }
        
        # Apply resolution filters if desired.
        # Note: Filtering by height in a self-contained stream may or may not work depending on available formats.
        if resolution_dropdown == "1080":
            ydl_opts["format"] = "best[height<=1080][ext=mp4]"
        elif resolution_dropdown == "720":
            ydl_opts["format"] = "best[height<=720][ext=mp4]"
        elif resolution_dropdown == "360":
            ydl_opts["format"] = "best[height<=360][ext=mp4]"
        # Otherwise, "best" is used.
        
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        print("✅ Download complete!")
        return savepath
    except Exception as e:
        raise ValueError(f"yt_download failed with exception: {e}")
