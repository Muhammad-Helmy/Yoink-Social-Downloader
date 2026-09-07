import os
import re
import yt_dlp
from .base import BaseDownloader
from ..logger import translate_error, format_progress_status, LogLevel
from ..hardware import get_ffmpeg_hardware_args

class TikTokDownloader(BaseDownloader):
    def __init__(self):
        super().__init__("tiktok")

    def _clean_url(self, url: str) -> str:
        url = (url or "").strip()
        # Strip tracking & search query params from browser address bar
        url = re.sub(r'(\/(?:video|photo)\/\d+).*', r'\1', url)
        return url

    def fetch_info(self, url: str) -> dict:
        self.reset_cancel()
        target_url = self._clean_url(url)
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(target_url, download=False)
                if not info:
                    return {"success": False, "error": "Could not retrieve TikTok metadata."}

                title = info.get("title") or info.get("description") or "TikTok Post"
                if len(title) > 80:
                    title = title[:77] + "..."
                thumbnail = info.get("thumbnail", "")
                duration = info.get("duration", 0)
                uploader = info.get("uploader") or info.get("creator") or "@tiktokuser"

                # Check formats
                formats = info.get("formats", [])
                has_video = False
                has_audio = False
                has_no_watermark = False

                for f in formats:
                    vcodec = f.get("vcodec")
                    acodec = f.get("acodec")
                    if vcodec and vcodec != "none":
                        has_video = True
                    if acodec and acodec != "none":
                        has_audio = True

                    fmt_note = (f.get("format_note") or "").lower()
                    fmt_id = (f.get("format_id") or "").lower()
                    if "watermark" not in fmt_note and ("download_addr" in fmt_id or "hd" in fmt_id or "no_watermark" in fmt_note):
                        has_no_watermark = True

                # Check if it's photo mode (slideshow)
                images = []
                thumbnails = info.get("thumbnails") or []
                if not thumbnail and thumbnails:
                    thumbnail = thumbnails[-1].get("url") or ""
                for t in thumbnails:
                    u = t.get("url")
                    if u and u not in images:
                        images.append(u)

                has_image = bool(images) or bool(thumbnail)
                if not images and thumbnail:
                    images = [thumbnail]

                qualities = [
                    {"value": "best_hd", "label": "HD (No-Watermark Preferred)", "height": 1080},
                    {"value": "standard", "label": "Standard Quality", "height": 720}
                ]

                return {
                    "success": True,
                    "title": title,
                    "thumbnail": thumbnail,
                    "duration": duration,
                    "duration_str": self.format_duration(duration),
                    "uploader": uploader,
                    "qualities": qualities,
                    "has_video": has_video,
                    "has_audio": has_audio,
                    "has_image": has_image,
                    "images": images,
                    "error": ""
                }

        except Exception as e:
            err_str = str(e)
            return {
                "success": False,
                "error": translate_error(err_str, "tiktok"),
                "raw_error": err_str
            }

    def download(self, url: str, quality: str, format_type: str, output_dir: str, hardware_mode: str = "auto", progress_hook=None, log_hook=None) -> dict:
        self.reset_cancel()
        os.makedirs(output_dir, exist_ok=True)
        downloaded_filepath = None
        target_url = self._clean_url(url)

        # 1. Handle Image Download
        if format_type == "image":
            if log_hook:
                log_hook(LogLevel.INFO, "🖼️ Fetching TikTok photo(s)...")
            info_res = self.fetch_info(target_url)
            images = info_res.get("images", [])
            title = info_res.get("title", "TikTok_Photo")
            if not images:
                return {"success": False, "error": "No images available for this post."}
            return self.download_images(images, output_dir, title, progress_hook)

        # 2. Handle Video or Audio Download
        def ytdl_hook(d):
            nonlocal downloaded_filepath
            if self.is_cancelled:
                raise Exception("Download cancelled by user.")

            if d.get("status") == "finished":
                filename = d.get("filename")
                if filename:
                    downloaded_filepath = filename

            if progress_hook:
                prog_data = format_progress_status(d, quality="TikTok HD", format_type=format_type)
                progress_hook(prog_data)

        if format_type == "audio":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(output_dir, "TT_%(title).60s_%(id)s.%(ext)s"),
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
            fmt = "best[format_id!*=watermark]/bestvideo+bestaudio/best[ext=mp4]/best"
            ydl_opts = {
                "format": fmt,
                "outtmpl": os.path.join(output_dir, "TT_%(title).60s_%(id)s.%(ext)s"),
                "progress_hooks": [ytdl_hook],
                "quiet": True,
                "no_warnings": True,
                "merge_output_format": "mp4",
            }

        try:
            if log_hook:
                log_hook(LogLevel.INFO, "🚀 Downloading TikTok media...")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(target_url, download=True)
                title = info.get("title", "TikTok Video") if info else "Video"

                # Check format note safely without NoneType crashes
                format_note = (info.get("format_note") or "") if info else ""
                if "watermark" in format_note.lower() and log_hook:
                    log_hook(LogLevel.WARNING, "ℹ️ No-watermark stream was unavailable. Downloaded original stream.")

                vid_id = info.get("id", "") if info else ""
                safe_title = re.sub(r'[\\/*?:"<>|]', "", title)[:60]

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
                "filename": os.path.basename(downloaded_filepath) if downloaded_filepath else "TikTok Media",
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
                "error": translate_error(err_str, "tiktok"),
                "raw_error": err_str
            }
