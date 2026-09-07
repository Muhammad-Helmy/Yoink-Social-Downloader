from abc import ABC, abstractmethod
import os
import re
import threading
import urllib.request

class BaseDownloader(ABC):
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self._cancel_flag = threading.Event()

    def cancel(self):
        """Signal ongoing download operation to cancel."""
        self._cancel_flag.set()

    def reset_cancel(self):
        self._cancel_flag.clear()

    @property
    def is_cancelled(self) -> bool:
        return self._cancel_flag.is_set()

    @abstractmethod
    def fetch_info(self, url: str) -> dict:
        """
        Fetch media metadata: title, thumbnail, duration, uploader, qualities, images.
        Returns:
            {
                "success": bool,
                "title": str,
                "thumbnail": str,
                "duration": int,
                "duration_str": str,
                "uploader": str,
                "qualities": list,
                "has_video": bool,
                "has_audio": bool,
                "has_image": bool,
                "images": list,
                "error": str
            }
        """
        pass

    @abstractmethod
    def download(self, url: str, quality: str, format_type: str, output_dir: str, hardware_mode: str = "auto", progress_hook=None, log_hook=None) -> dict:
        pass

    def download_images(self, image_urls: list, output_dir: str, title: str = "", progress_hook=None) -> dict:
        """
        Utility to download one or multiple image files (JPG/PNG).
        """
        self.reset_cancel()
        os.makedirs(output_dir, exist_ok=True)
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title)[:60] if title else "Image"
        downloaded_files = []

        total = len(image_urls)
        for i, img_url in enumerate(image_urls, start=1):
            if self.is_cancelled:
                return {"success": False, "error": "Download cancelled", "cancelled": True}

            ext = "jpg"
            if ".png" in img_url.lower():
                ext = "png"
            elif ".webp" in img_url.lower():
                ext = "webp"

            if total == 1:
                filename = f"{self.platform_name.upper()}_{safe_title}.{ext}"
            else:
                filename = f"{self.platform_name.upper()}_{safe_title}_{i:02d}.{ext}"

            dest_path = os.path.join(output_dir, filename)
            
            try:
                headers = {
                    "User-Agent": "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)" if ("fbsbx.com" in img_url or "facebook.com" in img_url) else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
                }
                req = urllib.request.Request(
                    img_url,
                    headers=headers
                )
                with urllib.request.urlopen(req, timeout=20) as resp:
                    with open(dest_path, "wb") as f:
                        f.write(resp.read())
                downloaded_files.append(dest_path)
            except Exception as e:
                print(f"Failed to download image {i}: {e}")

            if progress_hook:
                percent = (i / total) * 100.0
                progress_hook({
                    "percent": percent,
                    "speed": "",
                    "eta": "",
                    "message": f"🖼️ Saved {i}/{total} images",
                    "is_finished": (i == total)
                })

        if downloaded_files:
            return {
                "success": True,
                "file_path": downloaded_files[0],
                "filename": os.path.basename(downloaded_files[0]),
                "all_files": downloaded_files,
                "count": len(downloaded_files),
                "error": ""
            }
        return {"success": False, "error": "Failed to download image(s)."}

    @staticmethod
    def format_duration(seconds) -> str:
        if not seconds or seconds <= 0:
            return ""
        seconds = int(seconds)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    @staticmethod
    def resolve_final_output_file(output_dir: str, info: dict = None, downloaded_filepath: str = "", format_type: str = "video", vid_id: str = "", safe_title: str = "") -> str:
        """
        Robustly resolves the actual existing file on disk after yt-dlp download and postprocessing
        (such as ffmpeg audio extraction or DASH video+audio merging).
        """
        # 1. Check requested_downloads inside yt-dlp info dict if available
        if info:
            reqs = info.get("requested_downloads")
            if reqs and isinstance(reqs, list):
                for r in reversed(reqs):
                    rf = r.get("filepath") or r.get("_filename")
                    if rf and os.path.exists(rf) and not rf.endswith((".part", ".ytdl")):
                        return os.path.abspath(rf)
            
            inf_f = info.get("_filename")
            if inf_f and os.path.exists(inf_f) and not inf_f.endswith((".part", ".ytdl")):
                return os.path.abspath(inf_f)

        # 2. Check downloaded_filepath and variations (stripping intermediate DASH/format fragments)
        if downloaded_filepath:
            stem, ext = os.path.splitext(downloaded_filepath)
            clean_stem = re.sub(r'(\.fdash[^\.]*|\.f\d+(-\d+)?|\.part|\.ytdl)$', '', stem)
            target_ext = ".mp3" if format_type == "audio" else ".mp4"

            if clean_stem != stem or not os.path.exists(downloaded_filepath):
                cand = clean_stem + target_ext
                if os.path.exists(cand):
                    return os.path.abspath(cand)
                for e in [".mp4", ".mp3", ".m4a", ".webm", ".mkv", ".jpg", ".png"]:
                    cand = clean_stem + e
                    if os.path.exists(cand):
                        return os.path.abspath(cand)

            if os.path.exists(downloaded_filepath) and not downloaded_filepath.endswith((".part", ".ytdl")):
                return os.path.abspath(downloaded_filepath)

        # 3. Search directory by video/media ID
        target_ext = ".mp3" if format_type == "audio" else ".mp4"
        if vid_id and os.path.exists(output_dir):
            candidates = [
                os.path.join(output_dir, f) for f in os.listdir(output_dir)
                if vid_id in f and os.path.isfile(os.path.join(output_dir, f)) and not f.endswith((".part", ".ytdl"))
            ]
            if candidates:
                ext_matches = [c for c in candidates if c.lower().endswith(target_ext)]
                if ext_matches:
                    return os.path.abspath(max(ext_matches, key=os.path.getmtime))
                return os.path.abspath(max(candidates, key=os.path.getmtime))

        # 4. Search directory by safe title prefix
        if safe_title and os.path.exists(output_dir):
            st_prefix = safe_title[:25].strip()
            if len(st_prefix) > 5:
                candidates = [
                    os.path.join(output_dir, f) for f in os.listdir(output_dir)
                    if st_prefix in f and os.path.isfile(os.path.join(output_dir, f)) and not f.endswith((".part", ".ytdl"))
                ]
                if candidates:
                    ext_matches = [c for c in candidates if c.lower().endswith(target_ext)]
                    if ext_matches:
                        return os.path.abspath(max(ext_matches, key=os.path.getmtime))
                    return os.path.abspath(max(candidates, key=os.path.getmtime))

        return os.path.abspath(downloaded_filepath) if downloaded_filepath else ""

