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
            video_title = re.sub(r"[^a-zA-Z0-9]", " ", video_title)  # remove any problematic characters
        
        # Construct a save path (ensure the savedir exists).
        savepath = f"{savedir}/{video_title or video_id}.mp4"
        
        # Define a progress hook that updates a single progress bar and status text.
        def my_progress_hook(d):
            if d.get('status') == 'downloading':
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded_bytes = d.get('downloaded_bytes', 0)
                if total_bytes:
                    progress = downloaded_bytes / total_bytes
                    progress_bar.progress(progress)
                    percentage = int(progress * 100)
                    # Convert bytes to KB or MB as needed.
                    if downloaded_bytes < 1024 * 1024:
                        downloaded_str = f"{downloaded_bytes/1024:.2f} KB"
                        total_str = f"{total_bytes/1024:.2f} KB"
                    else:
                        downloaded_str = f"{downloaded_bytes/1024/1024:.2f} MB"
                        total_str = f"{total_bytes/1024/1024:.2f} MB"
                    status_text.text(f"Downloading... {percentage}% ({downloaded_str} / {total_str})")
            elif d.get('status') == 'finished':
                progress_bar.progress(1.0)
                status_text.text("✅ Download completed!")
        
        # Set yt-dlp options – using "best[ext=mp4]" downloads a self-contained MP4 file.
        ydl_opts = {
            "format": "best[ext=mp4]",
            "outtmpl": savepath,
            "progress_hooks": [my_progress_hook],
            "noplaylist": True,  # Only download a single video.
            "postprocessors": [],  # No extra postprocessing.
        }
        
        # Apply resolution filters if desired.
        if resolution_dropdown == "1080":
            ydl_opts["format"] = "best[height<=1080][ext=mp4]"
        elif resolution_dropdown == "720":
            ydl_opts["format"] = "best[height<=720][ext=mp4]"
        elif resolution_dropdown == "360":
            ydl_opts["format"] = "best[height<=360][ext=mp4]"
        
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        print("✅ Download complete!")
        return savepath
    except Exception as e:
        raise ValueError(f"yt_download failed with exception: {e}")
