import os
import re
import yt_dlp
from .base import BaseDownloader
from ..logger import translate_error, format_progress_status, LogLevel
from ..hardware import get_ffmpeg_hardware_args

class YouTubeDownloader(BaseDownloader):
    def __init__(self):
        super().__init__("youtube")

    def fetch_info(self, url: str) -> dict:
        self.reset_cancel()
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return {"success": False, "error": "Could not read info from this YouTube link."}

                title = info.get("title", "YouTube Video")
                thumbnail = info.get("thumbnail", "")
                duration = info.get("duration", 0)
                uploader = info.get("uploader") or info.get("channel") or "YouTube Creator"
                
                # Extract available video resolutions
                formats = info.get("formats", [])
                resolutions = set()
                
                for f in formats:
                    height = f.get("height")
                    if height and height >= 144:
                        resolutions.add(height)
                        
                sorted_heights = sorted(list(resolutions), reverse=True)
                
                quality_list = []
                for h in sorted_heights:
                    if h >= 2160:
                        tag = f"{h}p (4K UHD)"
                    elif h >= 1440:
                        tag = f"{h}p (2K QHD)"
                    elif h >= 1080:
                        tag = f"{h}p (Full HD)"
                    elif h >= 720:
                        tag = f"{h}p (HD)"
                    else:
                        tag = f"{h}p"
                    quality_list.append({"value": str(h), "label": tag, "height": h})

                if not quality_list:
                    quality_list.append({"value": "best", "label": "Auto Best Quality", "height": 0})

                images = [thumbnail] if thumbnail else []

                return {
                    "success": True,
                    "title": title,
                    "thumbnail": thumbnail,
                    "duration": duration,
                    "duration_str": self.format_duration(duration),
                    "uploader": uploader,
                    "qualities": quality_list,
                    "has_video": True,
                    "has_audio": True,
                    "has_image": bool(images),
                    "images": images,
                    "error": ""
                }

        except Exception as e:
            err_str = str(e)
            return {
                "success": False,
                "error": translate_error(err_str, "youtube"),
                "raw_error": err_str
            }

    def download(self, url: str, quality: str, format_type: str, output_dir: str, hardware_mode: str = "auto", progress_hook=None, log_hook=None) -> dict:
        self.reset_cancel()
        os.makedirs(output_dir, exist_ok=True)
        downloaded_filepath = None

        # 1. Image Download (Thumbnail)
        if format_type == "image":
            if log_hook:
                log_hook(LogLevel.INFO, "🖼️ Downloading YouTube thumbnail/cover...")
            info_res = self.fetch_info(url)
            images = info_res.get("images", [])
            title = info_res.get("title", "YT_Thumbnail")
            if not images:
                return {"success": False, "error": "No image available."}
            return self.download_images(images, output_dir, title, progress_hook)

        # 2. Video / Audio Download
        def ytdl_hook(d):
            nonlocal downloaded_filepath
            if self.is_cancelled:
                raise Exception("Download cancelled by user.")

            if d.get("status") == "finished":
                filename = d.get("filename")
                if filename:
                    downloaded_filepath = filename

            if progress_hook:
                prog_data = format_progress_status(d, quality=quality, format_type=format_type)
                progress_hook(prog_data)

        if format_type == "audio":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(output_dir, "%(title).80s [%(id)s].%(ext)s"),
                "progress_hooks": [ytdl_hook],
                "quiet": True,
                "no_warnings": True,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }
        else:
            if quality and quality.isdigit():
                h = int(quality)
                fmt = f"bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={h}]+bestaudio/best[height<={h}]/best"
            else:
                fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"

            ydl_opts = {
                "format": fmt,
                "outtmpl": os.path.join(output_dir, "%(title).80s [%(id)s].%(ext)s"),
                "progress_hooks": [ytdl_hook],
                "quiet": True,
                "no_warnings": True,
                "merge_output_format": "mp4",
            }

        try:
            if log_hook:
                log_hook(LogLevel.INFO, f"🚀 Starting YouTube download ({format_type.upper()}, {quality or 'auto'})...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title", "YouTube Video") if info else "Video"
                vid_id = info.get("id", "") if info else ""
                safe_title = re.sub(r'[\\/*?:"<>|]', "", title)[:80]

                downloaded_filepath = self.resolve_final_output_file(
                    output_dir=output_dir,
                    info=info,
                    downloaded_filepath=downloaded_filepath,
                    format_type=format_type,
                    vid_id=vid_id,
                    safe_title=safe_title
                )

            return {
                "success": True,
                "file_path": downloaded_filepath,
                "filename": os.path.basename(downloaded_filepath) if downloaded_filepath else "YouTube Media",
                "title": title or "",
                "thumbnail": (info.get("thumbnail") if info else "") or "",
                "error": ""
            }

        except Exception as e:
            err_str = str(e)
            if "cancelled" in err_str.lower() or "dibatalkan" in err_str.lower():
                return {"success": False, "error": "Download cancelled.", "cancelled": True}
            return {
                "success": False,
                "error": translate_error(err_str, "youtube"),
                "raw_error": err_str
            }
