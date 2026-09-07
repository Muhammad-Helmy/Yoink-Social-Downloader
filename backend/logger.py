import re
import datetime
from .i18n import get_text
from .config import get_config

class LogLevel:
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

def get_current_lang():
    try:
        return get_config().get("language", "en")
    except Exception:
        return "en"

def create_log_entry(level: str, message: str, details: str = ""):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    
    icon_map = {
        LogLevel.INFO: "ℹ️",
        LogLevel.SUCCESS: "✅",
        LogLevel.WARNING: "⚠️",
        LogLevel.ERROR: "❌"
    }
    icon = icon_map.get(level, "💬")

    return {
        "timestamp": now,
        "level": level,
        "icon": icon,
        "message": message,
        "details": details
    }

def translate_error(error_msg: str, platform: str = "", lang: str = None) -> str:
    """
    Translates raw backend or yt-dlp exceptions into clear, human-readable text.
    """
    if not lang:
        lang = get_current_lang()

    err_lower = error_msg.lower()
    plat_name = platform.capitalize() if platform else "Platform"

    if "403" in err_lower or "forbidden" in err_lower:
        return f"⚠️ {get_text('err_403', lang)}"
    
    if "private video" in err_lower or "login required" in err_lower or "this video is private" in err_lower:
        return f"🔒 {get_text('err_private', lang)}"
    
    if "video unavailable" in err_lower or "not found" in err_lower or "404" in err_lower:
        return f"❌ {get_text('err_not_found', lang)}"
    
    if "sign in to confirm you’re not a bot" in err_lower or "bot verification" in err_lower or "captcha" in err_lower:
        return f"🤖 {get_text('err_bot', lang)}"

    if "unsupported url" in err_lower or "not a valid url" in err_lower:
        return f"❌ {get_text('err_invalid_url', lang, platform=plat_name)}"

    if "connection timed out" in err_lower or "network is unreachable" in err_lower or "name or service not known" in err_lower:
        return f"🌐 {get_text('err_network', lang)}"

    if "ffmpeg not found" in err_lower:
        return f"⚠️ {get_text('err_ffmpeg', lang)}"

    if platform.lower() == "tiktok" and ("extractor" in err_lower or "unable to extract" in err_lower):
        return f"⚠️ {get_text('err_tiktok_extractor', lang)}"

    if platform.lower() == "instagram" and ("rate limit" in err_lower or "challenge_required" in err_lower):
        return f"⚠️ {get_text('err_ig_rate_limit', lang)}"

    # Generic clean fallback
    clean = re.sub(r'\[.*?\]', '', error_msg).strip()
    if len(clean) > 160:
        clean = clean[:160] + "..."
    return f"❌ {plat_name}: {clean}"

def format_progress_status(d: dict, title: str = "", quality: str = "", format_type: str = "video", lang: str = None) -> dict:
    """
    Parses a yt-dlp progress hook dict into human-readable details.
    """
    if not lang:
        lang = get_current_lang()

    status = d.get("status")
    
    if status == "downloading":
        total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
        downloaded = d.get("downloaded_bytes") or 0
        
        percent = 0.0
        if total_bytes > 0:
            percent = (downloaded / total_bytes) * 100.0
        elif "_percent_str" in d:
            p_str = d["_percent_str"].replace("%", "").strip()
            try:
                percent = float(p_str)
            except ValueError:
                percent = 0.0

        speed = d.get("speed") or 0
        speed_str = ""
        if speed:
            if speed > 1024 * 1024:
                speed_str = f"{speed / (1024 * 1024):.1f} MB/s"
            else:
                speed_str = f"{speed / 1024:.0f} KB/s"
        else:
            speed_str = d.get("_speed_str", "")

        eta = d.get("eta")
        eta_str = ""
        if eta is not None:
            m, s = divmod(eta, 60)
            eta_str = f"{int(m):02d}:{int(s):02d}"
        else:
            eta_str = d.get("_eta_str", "")

        if format_type == "audio":
            type_label = "Audio MP3"
        elif format_type == "image":
            type_label = "Images" if lang == "en" else ("Gambar" if lang == "id" else "Imágenes")
        else:
            type_label = f"Video ({quality or 'Best'})"

        short_title = (title[:35] + "...") if len(title) > 35 else title

        action_word = "Downloading" if lang == "en" else ("Mengunduh" if lang == "id" else "Descargando")
        rem_word = "ETA" if lang == "en" else ("Sisa" if lang == "id" else "Restante")

        msg = f"⬇️ {action_word} {type_label}"
        if short_title:
            msg += f' "{short_title}"'
        msg += f" — {percent:.1f}%"
        if speed_str:
            msg += f" ({speed_str})"
        if eta_str:
            msg += f" [{rem_word}: {eta_str}]"

        return {
            "percent": round(percent, 1),
            "speed": speed_str,
            "eta": eta_str,
            "message": msg,
            "is_finished": False
        }

    elif status == "finished":
        final_msg = "⚙️ Merging streams & finalizing..." if lang == "en" else (
            "⚙️ Menggabungkan stream & finalisasi..." if lang == "id" else "⚙️ Fusionando transmisiones..."
        )
        return {
            "percent": 100.0,
            "speed": "",
            "eta": "",
            "message": final_msg,
            "is_finished": True
        }

    connecting_msg = "Connecting to server..." if lang == "en" else (
        "Menghubungkan ke server..." if lang == "id" else "Conectando al servidor..."
    )
    return {
        "percent": 0.0,
        "speed": "",
        "eta": "",
        "message": connecting_msg,
        "is_finished": False
    }
