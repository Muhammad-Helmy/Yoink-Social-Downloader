import os
import re
import json
from pathlib import Path

DEFAULT_APP_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "YoinkSocial")
CONFIG_FILE_PATH = os.path.join(DEFAULT_APP_DIR, "config.json")

def get_default_downloads_base():
    user_profile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
    downloads_dir = os.path.join(user_profile, "Downloads", "YoinkSocial")
    return downloads_dir

def get_default_config():
    base_dl = get_default_downloads_base()
    return {
        "version": "1.0",
        "theme": "dark",
        "language": "en",
        "hardware_acceleration": "auto",
        "auto_open_folder": False,
        "download_folders": {
            "youtube": os.path.join(base_dl, "YouTube"),
            "tiktok": os.path.join(base_dl, "TikTok"),
            "instagram": os.path.join(base_dl, "Instagram"),
            "facebook": os.path.join(base_dl, "Facebook")
        }
    }

def ensure_directories():
    os.makedirs(DEFAULT_APP_DIR, exist_ok=True)
    config = get_config()
    for platform, folder in config.get("download_folders", {}).items():
        try:
            os.makedirs(folder, exist_ok=True)
        except Exception:
            pass

def get_config():
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                saved = json.load(f)
                default = get_default_config()
                # Merge keys
                for k, v in default.items():
                    if k not in saved:
                        saved[k] = v
                    elif isinstance(v, dict) and isinstance(saved[k], dict):
                        for sub_k, sub_v in v.items():
                            if sub_k not in saved[k]:
                                saved[k][sub_k] = sub_v
                return saved
    except Exception as e:
        print(f"[Config] Error loading config: {e}")
    
    # Return default and save
    default = get_default_config()
    save_config(default)
    return default

def save_config(new_config: dict):
    try:
        os.makedirs(DEFAULT_APP_DIR, exist_ok=True)
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(new_config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[Config] Error saving config: {e}")
        return False

def get_platform_folder(platform: str) -> str:
    config = get_config()
    folders = config.get("download_folders", {})
    folder = folders.get(platform.lower())
    if not folder:
        base_dl = get_default_downloads_base()
        folder = os.path.join(base_dl, platform.capitalize())
    os.makedirs(folder, exist_ok=True)
    return folder

def set_platform_folder(platform: str, path: str):
    config = get_config()
    if "download_folders" not in config:
        config["download_folders"] = {}
    config["download_folders"][platform.lower()] = path
    save_config(config)
    os.makedirs(path, exist_ok=True)

HISTORY_FILE_PATH = os.path.join(DEFAULT_APP_DIR, "history.json")

def _heal_history_item(item: dict) -> bool:
    """Attempts to resolve actual file, size, and clean title for a history entry."""
    modified = False
    fpath = item.get("file_path", "")
    platform = item.get("platform", "youtube")
    fname = item.get("filename", "")

    # 1. Resolve file path if non-existent or has intermediate markers
    if not fpath or not os.path.exists(fpath):
        dir_path = os.path.dirname(fpath) if fpath else ""
        if not dir_path or not os.path.exists(dir_path):
            dir_path = get_platform_folder(platform)

        if os.path.exists(dir_path):
            target_name = os.path.basename(fpath or fname)
            stem = re.sub(r'(\.fdash[^\.]*|\.f\d+(-\d+)?|\.part|\.ytdl)?\.[a-zA-Z0-9]+$', '', target_name)
            
            # Check common target extensions
            resolved_cand = None
            for ext in [".mp4", ".mp3", ".m4a", ".webm", ".mkv", ".jpg", ".png"]:
                cand = os.path.join(dir_path, stem + ext)
                if os.path.exists(cand) and os.path.isfile(cand):
                    resolved_cand = cand
                    break

            # Search by prefix if direct extension not found
            if not resolved_cand:
                prefix = stem[:25].strip()
                if len(prefix) > 5:
                    candidates = [
                        os.path.join(dir_path, f) for f in os.listdir(dir_path)
                        if f.startswith(prefix) and os.path.isfile(os.path.join(dir_path, f)) and not f.endswith((".part", ".ytdl"))
                    ]
                    if candidates:
                        resolved_cand = max(candidates, key=os.path.getmtime)

            if resolved_cand and os.path.exists(resolved_cand):
                item["file_path"] = os.path.abspath(resolved_cand)
                item["filename"] = os.path.basename(resolved_cand)
                fpath = item["file_path"]
                fname = item["filename"]
                modified = True

    # 2. Recalculate file size if '--' or empty
    if (item.get("size_str") in ["--", "", None]) and fpath and os.path.exists(fpath):
        try:
            sz = os.path.getsize(fpath)
            if sz > 1024 * 1024 * 1024:
                item["size_str"] = f"{sz / (1024 * 1024 * 1024):.2f} GB"
            elif sz > 1024 * 1024:
                item["size_str"] = f"{sz / (1024 * 1024):.1f} MB"
            elif sz > 1024:
                item["size_str"] = f"{sz / 1024:.0f} KB"
            else:
                item["size_str"] = f"{sz} B"
            modified = True
        except Exception:
            pass

    # 3. Heal title if 'Media File' or empty
    if item.get("title") in ["Media File", "", None] and fname:
        clean_t = re.sub(r'^(FB_|IG_|TT_|YOUTUBE_|FACEBOOK_)', '', fname)
        clean_t = re.sub(r'(\[[a-zA-Z0-9_-]+\]|_\d+)?\.[a-zA-Z0-9]+$', '', clean_t).strip()
        if clean_t:
            item["title"] = clean_t
            modified = True

    return modified

def get_history() -> list:
    try:
        if os.path.exists(HISTORY_FILE_PATH):
            with open(HISTORY_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    any_modified = False
                    for item in data:
                        if isinstance(item, dict):
                            if _heal_history_item(item):
                                any_modified = True
                    if any_modified:
                        try:
                            with open(HISTORY_FILE_PATH, "w", encoding="utf-8") as fw:
                                json.dump(data, fw, indent=2, ensure_ascii=False)
                        except Exception:
                            pass
                    return data[:10]
    except Exception as e:
        print(f"[History] Error reading history: {e}")
    return []

def add_history_entry(entry: dict) -> list:
    """
    Adds a completed download entry to persistent history, capped at 10 items (most recent first).
    """
    history = get_history()
    # Prepend new entry
    history.insert(0, entry)
    history = history[:10]
    try:
        os.makedirs(DEFAULT_APP_DIR, exist_ok=True)
        with open(HISTORY_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[History] Error saving history: {e}")
    return history

def clear_history() -> bool:
    try:
        if os.path.exists(HISTORY_FILE_PATH):
            with open(HISTORY_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump([], f)
        return True
    except Exception as e:
        print(f"[History] Error clearing history: {e}")
        return False

