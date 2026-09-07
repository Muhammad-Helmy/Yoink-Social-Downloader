import os
import re
import yt_dlp
import urllib.request
from .base import BaseDownloader
from ..logger import translate_error, format_progress_status, LogLevel

class InstagramDownloader(BaseDownloader):
    def __init__(self):
        super().__init__("instagram")

    def _normalize_url(self, url: str) -> tuple[str, str]:
        """
        Extract clean shortcode and normalized URL from any Instagram URL format.
        Supports /p/, /reel/, /reels/, /tv/, /explore/p/, /{user}/p/, etc.
        """
        url = (url or "").strip()
        match = re.search(r'/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)', url)
        if match:
            shortcode = match.group(1)
            return shortcode, f"https://www.instagram.com/p/{shortcode}/"
        return "", url

    def fetch_info(self, url: str) -> dict:
        self.reset_cancel()
        shortcode, clean_url = self._normalize_url(url)
        target_url = clean_url or url

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }
        
        # 1. Try yt-dlp first with clean URL
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(target_url, download=False)
                if info:
                    title = info.get("title") or info.get("description") or f"Instagram Post [{shortcode}]"
                    if len(title) > 80:
                        title = title[:77] + "..."
                    thumbnail = info.get("thumbnail", "")
                    duration = info.get("duration", 0)
                    uploader = info.get("uploader") or info.get("channel") or "Instagram User"

                    # Check formats & entries
                    has_video = False
                    formats = info.get("formats", [])
                    for f in formats:
                        if f.get("vcodec") and f.get("vcodec") != "none":
                            has_video = True
                            break

                    images = []
                    # Check entries if playlist/carousel
                    entries = info.get("entries")
                    if entries:
                        for entry in entries:
                            if entry:
                                thumb = entry.get("thumbnail") or entry.get("url")
                                if thumb and thumb not in images:
                                    images.append(thumb)
                    elif thumbnail:
                        images.append(thumbnail)

                    return {
                        "success": True,
                        "title": title,
                        "thumbnail": thumbnail,
                        "duration": duration,
                        "duration_str": self.format_duration(duration),
                        "uploader": uploader,
                        "qualities": [{"value": "best", "label": "Best Quality (Automatic)", "height": 0}],
                        "has_video": has_video,
                        "has_audio": True,
                        "has_image": bool(images),
                        "images": images,
                        "error": ""
                    }
        except Exception as yt_err:
            pass

        # 1b. Try yt-dlp with installed browser cookies if blocked
        for browser in ["brave", "chrome", "edge", "firefox"]:
            try:
                with yt_dlp.YoutubeDL({**ydl_opts, "cookiesfrombrowser": (browser, None, None, None)}) as ydl_b:
                    info = ydl_b.extract_info(target_url, download=False)
                    if info:
                        title = info.get("title") or info.get("description") or f"Instagram Post [{shortcode}]"
                        if len(title) > 80:
                            title = title[:77] + "..."
                        thumbnail = info.get("thumbnail", "")
                        duration = info.get("duration", 0)
                        uploader = info.get("uploader") or info.get("channel") or "Instagram User"

                        has_video = any(f.get("vcodec") and f.get("vcodec") != "none" for f in info.get("formats", []))
                        images = [thumbnail] if thumbnail else []

                        return {
                            "success": True,
                            "title": title,
                            "thumbnail": thumbnail,
                            "duration": duration,
                            "duration_str": self.format_duration(duration),
                            "uploader": uploader,
                            "qualities": [{"value": "best", "label": "Best Quality (Browser Session)", "height": 0}],
                            "has_video": has_video,
                            "has_audio": True,
                            "has_image": bool(images),
                            "images": images,
                            "error": ""
                        }
            except Exception:
                continue

        # 2. Fallback to Instaloader for metadata & photos/videos
        if shortcode:
            try:
                import instaloader
                L = instaloader.Instaloader()
                post = instaloader.Post.from_shortcode(L.context, shortcode)
                caption = post.caption or f"Instagram Post [{shortcode}]"
                if len(caption) > 80:
                    caption = caption[:77] + "..."

                images = []
                if post.typename == "GraphSidecar":
                    for node in post.get_sidecar_nodes():
                        images.append(node.display_url)
                else:
                    images.append(post.url)

                return {
                    "success": True,
                    "title": caption,
                    "thumbnail": post.url,
                    "duration": int(post.video_duration) if post.is_video else 0,
                    "duration_str": self.format_duration(post.video_duration if post.is_video else 0),
                    "uploader": f"@{post.owner_username}",
                    "qualities": [{"value": "best", "label": "Best Quality (Instaloader)", "height": 0}],
                    "has_video": bool(post.is_video),
                    "has_audio": bool(post.is_video),
                    "has_image": bool(images),
                    "images": images,
                    "error": ""
                }
            except Exception as inst_err:
                return {
                    "success": False,
                    "error": translate_error(str(inst_err), "instagram"),
                    "raw_error": f"instaloader: {inst_err}"
                }

        return {
            "success": False,
            "error": translate_error("Unsupported or private URL", "instagram")
        }

    def download(self, url: str, quality: str, format_type: str, output_dir: str, hardware_mode: str = "auto", progress_hook=None, log_hook=None) -> dict:
        self.reset_cancel()
        os.makedirs(output_dir, exist_ok=True)
        downloaded_filepath = None
        shortcode, clean_url = self._normalize_url(url)
        target_url = clean_url or url

        # 1. Image download
        if format_type == "image":
            if log_hook:
                log_hook(LogLevel.INFO, "🖼️ Downloading Instagram photo(s)...")
            info_res = self.fetch_info(target_url)
            images = info_res.get("images", [])
            title = info_res.get("title", f"IG_{shortcode or 'Photo'}")
            if not images:
                return {"success": False, "error": "No images available for this post."}
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
                prog_data = format_progress_status(d, quality="Instagram Best", format_type=format_type)
                progress_hook(prog_data)

        if format_type == "audio":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(output_dir, "IG_%(title).60s_%(id)s.%(ext)s"),
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
            ydl_opts = {
                "format": "bestvideo+bestaudio/best[ext=mp4]/best",
                "outtmpl": os.path.join(output_dir, "IG_%(title).60s_%(id)s.%(ext)s"),
                "progress_hooks": [ytdl_hook],
                "quiet": True,
                "no_warnings": True,
                "merge_output_format": "mp4",
            }

        try:
            if log_hook:
                log_hook(LogLevel.INFO, "🚀 Downloading Instagram media...")

            info = None
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(target_url, download=True)
            except Exception as primary_e:
                # Try with browser cookies
                success_cookies = False
                for browser in ["brave", "chrome", "edge", "firefox"]:
                    try:
                        cookie_opts = {**ydl_opts, "cookiesfrombrowser": (browser, None, None, None)}
                        with yt_dlp.YoutubeDL(cookie_opts) as ydl_b:
                            info = ydl_b.extract_info(target_url, download=True)
                            success_cookies = True
                            break
                    except Exception:
                        continue
                if not success_cookies:
                    raise primary_e

            title = info.get("title", "Instagram Post") if info else "Media"
            vid_id = info.get("id", "") if info else (shortcode or "")
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
                "filename": os.path.basename(downloaded_filepath) if downloaded_filepath else "Instagram Media",
                "title": title or "",
                "thumbnail": (info.get("thumbnail") if info else "") or "",
                "error": ""
            }

        except Exception as primary_error:
            if "cancelled" in str(primary_error).lower() or "dibatalkan" in str(primary_error).lower():
                return {"success": False, "error": "Download cancelled.", "cancelled": True}

            # Instaloader Fallback
            if log_hook:
                log_hook(LogLevel.WARNING, "⚠️ Primary engine encountered an error, falling back to Instaloader...")

            try:
                if not shortcode:
                    raise Exception("Invalid Instagram link.")

                import instaloader
                L = instaloader.Instaloader(
                    dirname_pattern=output_dir,
                    filename_pattern=f"IG_{shortcode}",
                    download_pictures=False,
                    download_videos=True,
                    download_video_thumbnails=False,
                    download_geotags=False,
                    download_comments=False,
                    save_metadata=False,
                    compress_json=False
                )

                post = instaloader.Post.from_shortcode(L.context, shortcode)
                if not post.is_video:
                    # It's an image post! Switch to image download
                    images = []
                    if post.typename == "GraphSidecar":
                        for node in post.get_sidecar_nodes():
                            images.append(node.display_url)
                    else:
                        images.append(post.url)
                    return self.download_images(images, output_dir, post.caption or f"IG_{shortcode}", progress_hook)

                L.download_post(post, target=output_dir)
                target_file = os.path.join(output_dir, f"IG_{shortcode}.mp4")
                if not os.path.exists(target_file):
                    candidates = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if shortcode in f and f.endswith(".mp4")]
                    if candidates:
                        target_file = candidates[0]

                if format_type == "audio" and os.path.exists(target_file):
                    import subprocess
                    mp3_path = target_file.rsplit(".", 1)[0] + ".mp3"
                    no_win = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
                    subprocess.run(["ffmpeg", "-y", "-i", target_file, "-vn", "-b:a", "192k", mp3_path], capture_output=True, creationflags=no_win)
                    if os.path.exists(mp3_path):
                        target_file = mp3_path

                return {
                    "success": True,
                    "file_path": target_file,
                    "filename": os.path.basename(target_file),
                    "error": ""
                }
            except Exception as fallback_err:
                return {
                    "success": False,
                    "error": translate_error(str(primary_error), "instagram"),
                    "raw_error": f"Primary: {primary_error} | Fallback: {fallback_err}"
                }
