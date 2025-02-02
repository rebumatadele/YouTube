import yt_dlp
from yt_dlp import YoutubeDL
import re


def is_valid_youtube_url(url: str) -> bool:
    """Checks if the URL is a valid YouTube video URL"""
    if not isinstance(url, str):
        return False
    pattern = r"^https://www\.youtube\.com/watch\?v=[A-Za-z0-9_-]{11}$"
    if "shorts" in url:
        pattern = r"^https://www\.youtube\.com/shorts/[A-Za-z0-9_-]{11}$"
    return re.match(pattern, url) is not None


def download_video(url: str, savedir: str, resolution_dropdown: str, progress_bar, status_text, my_proxies: dict = {}) -> str:
    """Downloads the YouTube video without requiring ffmpeg"""
    try:
        print("Downloading video from YouTube...")
        if is_valid_youtube_url(url):
            with YoutubeDL() as ydl:
                info_dict = ydl.extract_info(url, download=False)
                video_id = info_dict.get("id", None)
                video_title = info_dict.get("title", None)
                video_title = re.sub(r"[^a-zA-Z0-9]", " ", video_title)

                # Save path for the video
                savepath = f"{savedir}/{video_title or video_id}.mp4"

            # Progress hook to update UI
            def my_progress_hook(d):
                if d['status'] == 'downloading':
                    total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                    if total_bytes:
                        progress = d.get('downloaded_bytes', 0) / total_bytes
                        progress_bar.progress(progress)
                        status_text.text(f"Downloading... {d.get('downloaded_bytes', 0)} / {total_bytes} bytes")
                elif d['status'] == 'finished':
                    progress_bar.progress(1.0)
                    status_text.text("✅ Download completed!")

            # yt-dlp options to avoid ffmpeg dependency
            ydl_opts = {
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                "outtmpl": savepath,
                "progress_hooks": [my_progress_hook],
                "noplaylist": True,  # Ensures only a single video is downloaded
                "postprocessors": [],  # Removes any need for ffmpeg
            }

            # Apply resolution filters
            if resolution_dropdown == "1080":
                ydl_opts["format"] = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]"
            elif resolution_dropdown == "720":
                ydl_opts["format"] = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]"
            elif resolution_dropdown == "360":
                ydl_opts["format"] = "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]"

            # Download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            print("✅ Download complete!")
            return savepath
        else:
            raise ValueError(f"Invalid input URL: {url}")
    except Exception as e:
        raise ValueError(f"yt_download failed with exception: {e}")
