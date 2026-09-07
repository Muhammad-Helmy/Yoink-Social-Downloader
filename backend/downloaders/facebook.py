import os
import re
import html
import urllib.request
import yt_dlp
from .base import BaseDownloader
from ..logger import translate_error, format_progress_status, LogLevel
from ..hardware import get_ffmpeg_hardware_args

class FacebookDownloader(BaseDownloader):
    def __init__(self):
        super().__init__("facebook")

    def _fetch_og_photo_info(self, url: str) -> dict:
        """
        Extract photo metadata and direct lookaside CDN image URL using Facebook externalhit OpenGraph crawler.
        """
        fbid_m = re.search(r'fbid=(\d+)', url) or re.search(r'/photos/[^/]+/(\d+)', url)
        fbid = fbid_m.group(1) if fbid_m else ""

        headers = {
            "User-Agent": "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        
        title = ""
        img = ""
        uploader = "Facebook"

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                content = resp.read().decode("utf-8", errors="ignore")
                title_m = (re.search(r'property=[\"\']og:title[\"\']\s+content=[\"\']([^\"\']+)[\"\']', content) or
                           re.search(r'content=[\"\']([^\"\']+)[\"\']\s+property=[\"\']og:title[\"\']', content))
                img_m = (re.search(r'property=[\"\']og:image[\"\']\s+content=[\"\']([^\"\']+)[\"\']', content) or
                         re.search(r'content=[\"\']([^\"\']+)[\"\']\s+property=[\"\']og:image[\"\']', content))
                site_m = (re.search(r'property=[\"\']og:site_name[\"\']\s+content=[\"\']([^\"\']+)[\"\']', content) or
                          re.search(r'content=[\"\']([^\"\']+)[\"\']\s+property=[\"\']og:site_name[\"\']', content))

                if title_m:
                    title = html.unescape(title_m.group(1).strip())
                    title = re.sub(r'\s*\|\s*Facebook$', '', title)
                if site_m:
                    uploader = html.unescape(site_m.group(1).strip())
                if img_m:
                    img = html.unescape(img_m.group(1).strip())
        except Exception:
            pass

        if not img and fbid:
            img = f"https://lookaside.fbsbx.com/lookaside/crawler/media/?media_id={fbid}"
        if not title and fbid:
            title = f"Facebook Photo {fbid}"
        elif not title:
            title = "Facebook Photo"

        # Check if title indicates login barrier / private group
        is_private = (
            "groups" in url.lower() and not img
        ) or (
            title and any(phrase in title.lower() for phrase in ["log in to facebook", "masuk ke facebook", "iniciar sesión"])
        )

        if is_private:
            return {
                "success": False,
                "is_private": True,
                "error": "This content is from a private Facebook group or private profile and is not accessible publicly."
            }

        if img:
            return {
                "success": True,
                "title": title[:80],
                "thumbnail": img,
                "duration": 0,
                "duration_str": "",
                "uploader": uploader,
                "qualities": [
                    {"value": "original", "label": "Original Quality (HD Photo)", "height": 0}
                ],
                "has_video": False,
                "has_audio": False,
                "has_image": True,
                "images": [img],
                "error": ""
            }
        return {
            "success": False,
            "is_private": "groups" in url.lower(),
            "error": "Could not extract Facebook photo from this link. If it's a private group, it cannot be downloaded."
        }

    def fetch_info(self, url: str) -> dict:
        self.reset_cancel()
        url = (url or "").strip()

        # Check if URL explicitly indicates a photo
        is_photo_url = bool(re.search(r'fbid=\d+', url) or "/photo/" in url or "/photos/" in url or "photo.php" in url)
        if is_photo_url:
            og_res = self._fetch_og_photo_info(url)
            if og_res.get("success"):
                return og_res

        # Try yt-dlp first (for videos, reels, watch)
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    title = info.get("title") or info.get("description") or "Facebook Media"
                    if len(title) > 90:
                        title = title[:87] + "..."
                    thumbnail = info.get("thumbnail", "")
                    duration = info.get("duration", 0)
                    uploader = info.get("uploader") or "Facebook User"

                    has_video = False
                    formats = info.get("formats", [])
                    for f in formats:
                        if f.get("vcodec") and f.get("vcodec") != "none":
                            has_video = True
                            break

                    images = []
                    if thumbnail:
                        images.append(thumbnail)

                    qualities = [
                        {"value": "best", "label": "Best Quality (Auto Server Max)", "height": 0},
                        {"value": "hd", "label": "HD (When Available)", "height": 720},
                        {"value": "sd", "label": "SD (Standard Quality)", "height": 480}
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
                        "has_audio": True,
                        "has_image": bool(images),
                        "images": images,
                        "error": ""
                    }
        except Exception as yt_err:
            err_str = str(yt_err)
            # If yt-dlp fails with "Cannot parse data", "Unsupported URL", or photo issue, fall back to OpenGraph photo parser
            if ("cannot parse data" in err_str.lower() or 
                "unsupported url" in err_str.lower() or 
                "extractor error" in err_str.lower() or 
                "/share/p/" in url or 
                "/posts/" in url or 
                "permalink" in url):
                og_res = self._fetch_og_photo_info(url)
                if og_res.get("success"):
                    return og_res
                if og_res.get("is_private"):
                    return og_res

            # Check if login is required and try with browser cookies
            if "registered users" in err_str.lower():
                for browser in ["brave", "chrome", "edge", "firefox"]:
                    try:
                        with yt_dlp.YoutubeDL({**ydl_opts, "cookiesfrombrowser": (browser, None, None, None)}) as ydl_b:
                            info = ydl_b.extract_info(url, download=False)
                            if info:
                                title = info.get("title") or "Facebook Media"
                                thumbnail = info.get("thumbnail", "")
                                duration = info.get("duration", 0)
                                return {
                                    "success": True,
                                    "title": title[:87] + "...",
                                    "thumbnail": thumbnail,
                                    "duration": duration,
                                    "duration_str": self.format_duration(duration),
                                    "uploader": info.get("uploader") or "Facebook",
                                    "qualities": [{"value": "best", "label": "Best Quality (Auto)", "height": 0}],
                                    "has_video": True,
                                    "has_audio": True,
                                    "has_image": bool(thumbnail),
                                    "images": [thumbnail] if thumbnail else [],
                                    "error": ""
                                }
                    except Exception:
                        continue

            # Check if this indicates private group or private content
            is_private = (
                "/groups/" in url.lower() or
                any(p in err_str.lower() for p in [
                    "private", "permission", "login", "registered users", 
                    "not available", "may have been removed", "only shared with a small audience"
                ])
            )
            if is_private:
                return {
                    "success": False,
                    "is_private": True,
                    "error": "Konten Facebook ini berasal dari grup privat atau akun privat dan tidak dapat diakses secara publik. Silakan coba link media lain yang bersifat publik."
                }

            return {
                "success": False,
                "error": translate_error(err_str, "facebook"),
                "raw_error": err_str
            }

    def download(self, url: str, quality: str, format_type: str, output_dir: str, hardware_mode: str = "auto", progress_hook=None, log_hook=None) -> dict:
        self.reset_cancel()
        os.makedirs(output_dir, exist_ok=True)
        downloaded_filepath = None

        # 1. Image Download (Facebook Photos)
        if format_type == "image":
            if log_hook:
                log_hook(LogLevel.INFO, "🖼️ Downloading Facebook photo...")
            info_res = self.fetch_info(url)
            images = info_res.get("images", [])
            title = info_res.get("title", "FB_Photo")
            if not images:
                return {"success": False, "error": "No images available for this Facebook post."}
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
                prog_data = format_progress_status(d, quality="Facebook Best", format_type=format_type)
                progress_hook(prog_data)

        if format_type == "audio":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(output_dir, "FB_%(title).60s_%(id)s.%(ext)s"),
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
            if quality == "hd":
                fmt = "hd/best[ext=mp4]/best"
            elif quality == "sd":
                fmt = "sd/worst[ext=mp4]/best"
            else:
                fmt = "bestvideo+bestaudio/best[ext=mp4]/best"

            ydl_opts = {
                "format": fmt,
                "outtmpl": os.path.join(output_dir, "FB_%(title).60s_%(id)s.%(ext)s"),
                "progress_hooks": [ytdl_hook],
                "quiet": True,
                "no_warnings": True,
                "merge_output_format": "mp4",
            }

        try:
            if log_hook:
                log_hook(LogLevel.INFO, "🚀 Downloading Facebook media...")

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
            except Exception as first_err:
                # If error is registered users, try browser cookies
                if "registered users" in str(first_err).lower():
                    downloaded = False
                    for browser in ["brave", "chrome", "edge", "firefox"]:
                        try:
                            cookie_opts = {**ydl_opts, "cookiesfrombrowser": (browser, None, None, None)}
                            with yt_dlp.YoutubeDL(cookie_opts) as ydl_b:
                                info = ydl_b.extract_info(url, download=True)
                                downloaded = True
                                break
                        except Exception:
                            continue
                    if not downloaded:
                        raise first_err
                else:
                    raise first_err

            title = info.get("title", "Facebook Video") if info else "Video"
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
                "filename": os.path.basename(downloaded_filepath) if downloaded_filepath else "Facebook Media",
                "title": title or "",
                "thumbnail": (info.get("thumbnail") if info else "") or "",
                "error": ""
            }

        except Exception as e:
            err_str = str(e)
            if "cancelled" in err_str.lower() or "dibatalkan" in err_str.lower():
                return {"success": False, "error": "Download cancelled.", "cancelled": True}
            
            # If download fails because it was a photo post all along:
            if "cannot parse data" in err_str.lower() or "unsupported url" in err_str.lower():
                og_res = self._fetch_og_photo_info(url)
                if og_res.get("success") and og_res.get("images"):
                    return self.download_images(og_res["images"], output_dir, og_res.get("title", "FB_Photo"), progress_hook)

            return {
                "success": False,
                "error": translate_error(err_str, "facebook"),
                "raw_error": err_str
            }
