import os
import re
import json
import threading
import subprocess
import datetime
import webview
import yt_dlp
import urllib.request
from .downloaders import get_downloader
from .downloaders.base import BaseDownloader
from .config import get_config, save_config, get_platform_folder, set_platform_folder, get_history, add_history_entry, clear_history
from .logger import create_log_entry, LogLevel
from .hardware import detect_hardware
from .i18n import get_text

import uuid

class YoinkAPI:
    def __init__(self):
        self._window = None
        self._active_downloader = None
        self._is_downloading = False
        self._active_task = None
        self._queue = []
        self._queue_lock = threading.Lock()
        self._worker_thread = None

    def set_window(self, window):
        self._window = window

    def _get_lang(self):
        return get_config().get("language", "en")

    def _emit_log(self, level: str, message: str, details: str = ""):
        log_entry = create_log_entry(level, message, details)
        if self._window:
            js = f"window.onLogEvent && window.onLogEvent({json.dumps(log_entry)});"
            try:
                self._window.evaluate_js(js)
            except Exception as e:
                print(f"Failed to emit log: {e}")
        return log_entry

    def _emit_progress(self, progress_data: dict):
        if self._window:
            js = f"window.onDownloadProgress && window.onDownloadProgress({json.dumps(progress_data)});"
            try:
                self._window.evaluate_js(js)
            except Exception as e:
                print(f"Failed to emit progress: {e}")

    def _emit_queue_update(self):
        if self._window:
            queue_data = self.get_queue()
            js = f"window.onQueueUpdate && window.onQueueUpdate({json.dumps(queue_data)});"
            try:
                self._window.evaluate_js(js)
            except Exception:
                pass

    def get_hardware_info(self) -> dict:
        return detect_hardware()

    def fetch_info(self, platform: str, url: str) -> dict:
        url = (url or "").strip()
        lang = self._get_lang()
        if not url:
            self._emit_log(LogLevel.WARNING, f"⚠️ {get_text('empty_url', lang)}")
            return {"success": False, "error": get_text('empty_url', lang)}

        self._emit_log(LogLevel.INFO, f"🔍 {get_text('analyzing', lang, platform=platform.capitalize())}")
        try:
            downloader = get_downloader(platform)
            res = downloader.fetch_info(url)
            if res.get("success"):
                title = res.get("title", "")
                q_count = len(res.get("qualities", []))
                short_title = (title[:38] + "...") if len(title) > 38 else title
                self._emit_log(LogLevel.SUCCESS, f"✨ {get_text('analyzed', lang, title=short_title, count=q_count)}")
            else:
                self._emit_log(LogLevel.ERROR, res.get("error", "Error fetching metadata."))
            return res
        except Exception as e:
            err = f"Error: {str(e)}"
            self._emit_log(LogLevel.ERROR, err)
            return {"success": False, "error": err}

    def start_download(self, platform: str, url: str, quality: str = "best", format_type: str = "video", title: str = "", thumbnail: str = "") -> dict:
        lang = self._get_lang()
        url = (url or "").strip()
        if not url:
            self._emit_log(LogLevel.ERROR, f"❌ {get_text('empty_url', lang)}")
            return {"success": False, "error": get_text('empty_url', lang)}

        task_id = f"task_{int(datetime.datetime.now().timestamp() * 1000)}_{uuid.uuid4().hex[:6]}"
        task = {
            "id": task_id,
            "platform": platform,
            "url": url,
            "quality": quality,
            "format": format_type,
            "title": title or "Media File",
            "thumbnail": thumbnail or "",
            "percent": 0.0,
            "speed": "-- MB/s",
            "eta": "--:--",
            "message": "In Queue",
            "status": "queued",
            "start_time": datetime.datetime.now().strftime("%H:%M:%S")
        }

        with self._queue_lock:
            self._queue.append(task)
            pos = len(self._queue)
            is_already_active = (self._active_task is not None)

            # Start worker thread if not running
            if self._worker_thread is None or not self._worker_thread.is_alive():
                self._worker_thread = threading.Thread(target=self._queue_worker, daemon=True)
                self._worker_thread.start()

        if is_already_active:
            self._emit_log(LogLevel.INFO, f"⏳ Added to download queue: {task['title'][:35]}... (Position #{pos})")
        else:
            self._emit_log(LogLevel.INFO, f"🚀 Starting download: {task['title'][:35]}...")

        self._emit_queue_update()
        return {"success": True, "task": task, "queue_position": pos, "is_queued": is_already_active}

    def _queue_worker(self):
        while True:
            task = None
            with self._queue_lock:
                if not self._queue:
                    self._active_task = None
                    self._is_downloading = False
                    self._active_downloader = None
                    break
                task = self._queue.pop(0)
                task["status"] = "downloading"
                task["message"] = "Downloading..."
                self._active_task = task
                self._is_downloading = True

            self._emit_queue_update()
            self._execute_task(task)

            with self._queue_lock:
                self._active_task = None
                self._active_downloader = None
            self._emit_queue_update()

        with self._queue_lock:
            self._is_downloading = False
            self._active_task = None
            self._active_downloader = None
        self._emit_queue_update()

    def _execute_task(self, task: dict):
        lang = self._get_lang()
        platform = task["platform"]
        url = task["url"]
        quality = task["quality"]
        format_type = task["format"]

        try:
            cfg = get_config()
            output_dir = get_platform_folder(platform)
            downloader = get_downloader(platform)
            self._active_downloader = downloader
            hw_mode = cfg.get("hardware_acceleration", "auto")

            def progress_cb(prog):
                if self._active_task and self._active_task.get("id") == task.get("id"):
                    self._active_task["percent"] = prog.get("percent", 0.0)
                    self._active_task["speed"] = prog.get("speed", "")
                    self._active_task["eta"] = prog.get("eta", "")
                    self._active_task["message"] = prog.get("message", "")
                prog["task_id"] = task.get("id")
                prog["platform"] = platform
                prog["title"] = task.get("title")
                self._emit_progress(prog)

            def log_cb(lvl, msg):
                self._emit_log(lvl, msg)

            result = downloader.download(
                url=url,
                quality=quality,
                format_type=format_type,
                output_dir=output_dir,
                hardware_mode=hw_mode,
                progress_hook=progress_cb,
                log_hook=log_cb
            )

            result["task_id"] = task.get("id")
            result["platform"] = platform

            if result.get("success"):
                fname = result.get("filename", "")
                fpath = result.get("file_path", "")
                count = result.get("count", 1)

                # Ensure fpath exists on disk
                if not fpath or not os.path.exists(fpath):
                    resolved = BaseDownloader.resolve_final_output_file(
                        output_dir=output_dir,
                        info=None,
                        downloaded_filepath=fpath,
                        format_type=format_type
                    )
                    if resolved and os.path.exists(resolved):
                        fpath = resolved
                        fname = os.path.basename(resolved)
                        result["file_path"] = fpath
                        result["filename"] = fname

                size_str = "--"
                if fpath and os.path.exists(fpath):
                    sz = os.path.getsize(fpath)
                    if sz > 1024 * 1024 * 1024:
                        size_str = f"{sz / (1024 * 1024 * 1024):.2f} GB"
                    elif sz > 1024 * 1024:
                        size_str = f"{sz / (1024 * 1024):.1f} MB"
                    elif sz > 1024:
                        size_str = f"{sz / 1024:.0f} KB"
                    else:
                        size_str = f"{sz} B"

                # If task title was generic or empty, clean up title from result or filename
                final_title = task.get("title")
                if not final_title or final_title == "Media File":
                    if result.get("title"):
                        final_title = result["title"]
                    elif fname:
                        clean_t = re.sub(r'^(FB_|IG_|TT_|YOUTUBE_|FACEBOOK_)', '', fname)
                        clean_t = re.sub(r'(\[[a-zA-Z0-9_-]+\]|_\d+)?\.[a-zA-Z0-9]+$', '', clean_t).strip()
                        final_title = clean_t or fname
                    else:
                        final_title = "Media File"

                final_thumb = task.get("thumbnail") or result.get("thumbnail") or ""

                hist_entry = {
                    "id": str(int(datetime.datetime.now().timestamp() * 1000)),
                    "title": final_title,
                    "thumbnail": final_thumb,
                    "platform": platform,
                    "format": format_type,
                    "file_path": fpath,
                    "filename": fname,
                    "size_str": size_str,
                    "timestamp": datetime.datetime.now().strftime("%H:%M • %d %b %Y")
                }
                add_history_entry(hist_entry)
                result["history_entry"] = hist_entry

                if format_type == "image" and count > 1:
                    msg = get_text("download_images_count", lang, count=count)
                    self._emit_log(LogLevel.SUCCESS, f"🎉 {msg}", details=fpath)
                else:
                    msg = get_text("download_success", lang, filename=fname)
                    self._emit_log(LogLevel.SUCCESS, f"🎉 {msg}", details=fpath)

                if cfg.get("auto_open_folder", False):
                    self.open_folder(platform)

                if self._window:
                    js = f"window.onDownloadComplete && window.onDownloadComplete({json.dumps(result)});"
                    self._window.evaluate_js(js)
            else:
                if result.get("cancelled"):
                    self._emit_log(LogLevel.WARNING, f"🛑 {get_text('download_cancelled', lang)}")
                else:
                    self._emit_log(LogLevel.ERROR, result.get("error", "Download failed."))

                if self._window:
                    js = f"window.onDownloadFailed && window.onDownloadFailed({json.dumps(result)});"
                    self._window.evaluate_js(js)

        except Exception as e:
            err_msg = str(e)
            self._emit_log(LogLevel.ERROR, f"❌ {err_msg}")
            if self._window:
                js = f"window.onDownloadFailed && window.onDownloadFailed({json.dumps({'error': err_msg, 'task_id': task.get('id'), 'platform': platform})});"
                self._window.evaluate_js(js)

    def cancel_download(self, task_id: str = None) -> dict:
        lang = self._get_lang()
        with self._queue_lock:
            # If cancelling specific task from pending queue
            if task_id and self._queue:
                for i, t in enumerate(self._queue):
                    if t.get("id") == task_id:
                        removed = self._queue.pop(i)
                        self._emit_log(LogLevel.WARNING, f"🛑 Removed from queue: {removed.get('title', '')[:30]}")
                        self._emit_queue_update()
                        return {"success": True, "message": "Removed from queue."}

            # If cancelling active task
            if self._active_downloader:
                if not task_id or (self._active_task and self._active_task.get("id") == task_id):
                    self._active_downloader.cancel()
                    self._emit_log(LogLevel.WARNING, f"⏳ {get_text('cancelling', lang)}")
                    return {"success": True, "message": "Cancelling download..."}

        return {"success": False, "message": "No active or queued download found."}

    def get_queue(self) -> dict:
        with self._queue_lock:
            return {
                "active": dict(self._active_task) if self._active_task else None,
                "queue": [dict(t) for t in self._queue],
                "total": (1 if self._active_task else 0) + len(self._queue)
            }

    def get_active_task(self) -> dict:
        with self._queue_lock:
            return dict(self._active_task) if self._active_task else {}

    def get_history(self) -> list:
        return get_history()

    def clear_history(self) -> bool:
        return clear_history()

    def open_folder(self, platform: str) -> dict:
        lang = self._get_lang()
        try:
            folder = get_platform_folder(platform)
            os.makedirs(folder, exist_ok=True)
            if os.name == "nt":
                os.startfile(folder)
            else:
                subprocess.Popen(["explorer", folder])
            self._emit_log(LogLevel.INFO, f"📁 {get_text('folder_opened', lang, folder=folder)}")
            return {"success": True, "folder": folder}
        except Exception as e:
            err = f"Error opening folder: {str(e)}"
            self._emit_log(LogLevel.ERROR, err)
            return {"success": False, "error": err}

    def open_file(self, filepath: str) -> dict:
        try:
            if not filepath:
                return {"success": False, "error": "No file path specified."}
            
            filepath = os.path.normpath(filepath)

            # 1. Directly exists
            if os.path.exists(filepath) and os.path.isfile(filepath):
                os.startfile(filepath)
                return {"success": True}

            # 2. Check directory for resolved counterpart (e.g. .m4a -> .mp4 or stripped .fdash)
            parent_dir = os.path.dirname(filepath)
            if os.path.exists(parent_dir):
                base_name = os.path.basename(filepath)
                stem = re.sub(r'(\.fdash[^\.]*|\.f\d+(-\d+)?|\.part|\.ytdl)?\.[a-zA-Z0-9]+$', '', base_name)
                
                # Check direct common extensions
                for ext in [".mp4", ".mp3", ".m4a", ".webm", ".mkv", ".jpg", ".png"]:
                    cand = os.path.join(parent_dir, stem + ext)
                    if os.path.exists(cand) and os.path.isfile(cand):
                        os.startfile(cand)
                        return {"success": True, "resolved_path": cand}

                # Try prefix search
                prefix = stem[:25].strip()
                if len(prefix) > 5:
                    candidates = [
                        os.path.join(parent_dir, f) for f in os.listdir(parent_dir)
                        if f.startswith(prefix) and os.path.isfile(os.path.join(parent_dir, f)) and not f.endswith((".part", ".ytdl"))
                    ]
                    if candidates:
                        actual_file = max(candidates, key=os.path.getmtime)
                        os.startfile(actual_file)
                        return {"success": True, "resolved_path": actual_file}

            return {"success": False, "error": f"File not found: {filepath}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def choose_folder(self, platform: str) -> dict:
        lang = self._get_lang()
        if not self._window:
            return {"success": False, "error": "Window not ready"}
        
        current = get_platform_folder(platform)
        result = self._window.create_file_dialog(
            webview.FOLDER_DIALOG,
            directory=current,
            allow_multiple=False
        )
        if result and len(result) > 0:
            new_path = result[0]
            set_platform_folder(platform, new_path)
            self._emit_log(LogLevel.SUCCESS, f"📁 {get_text('folder_changed', lang, platform=platform.capitalize(), path=new_path)}")
            return {"success": True, "path": new_path}
        return {"success": False, "cancelled": True}

    def get_settings(self) -> dict:
        cfg = get_config()
        cfg["hardware"] = detect_hardware()
        return cfg

    def save_settings(self, settings_dict: dict) -> dict:
        ok = save_config(settings_dict)
        if ok:
            lang = settings_dict.get("language", "en")
            success_msg = "Settings saved successfully." if lang == "en" else (
                "Pengaturan berhasil disimpan." if lang == "id" else "Configuración guardada con éxito."
            )
            self._emit_log(LogLevel.SUCCESS, f"⚙️ {success_msg}")
        return {"success": ok}

    def check_ytdlp_update(self) -> dict:
        lang = self._get_lang()
        self._emit_log(LogLevel.INFO, "🔄 Checking for latest yt-dlp version...")
        try:
            current = yt_dlp.version.__version__
            url = "https://pypi.org/pypi/yt-dlp/json"
            req = urllib.request.Request(url, headers={"User-Agent": "YoinkSocial/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                latest = data["info"]["version"]
                
                has_update = (current != latest)
                if has_update:
                    self._emit_log(LogLevel.WARNING, f"📢 {get_text('ytdlp_update_avail', lang, latest=latest, current=current)}")
                else:
                    self._emit_log(LogLevel.SUCCESS, f"✅ {get_text('ytdlp_latest', lang, version=current)}")
                
                return {
                    "success": True,
                    "current_version": current,
                    "latest_version": latest,
                    "has_update": has_update
                }
        except Exception as e:
            current = yt_dlp.version.__version__
            msg = f"Failed to check update: {str(e)}"
            self._emit_log(LogLevel.WARNING, f"⚠️ {msg}")
            return {
                "success": False,
                "current_version": current,
                "latest_version": current,
                "has_update": False,
                "error": msg
            }

    def update_ytdlp(self) -> dict:
        lang = self._get_lang()
        self._emit_log(LogLevel.INFO, f"⏳ {get_text('ytdlp_updating', lang)}")
        def run_update():
            try:
                no_win = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
                res = subprocess.run(["pip", "install", "-U", "yt-dlp"], capture_output=True, text=True, creationflags=no_win)
                if res.returncode == 0:
                    self._emit_log(LogLevel.SUCCESS, f"🎉 {get_text('ytdlp_updated', lang)}")
                else:
                    self._emit_log(LogLevel.ERROR, f"❌ Update failed: {res.stderr[:100]}")
            except Exception as e:
                self._emit_log(LogLevel.ERROR, f"❌ Update error: {str(e)}")

        threading.Thread(target=run_update, daemon=True).start()
        return {"success": True, "message": "Update started"}
