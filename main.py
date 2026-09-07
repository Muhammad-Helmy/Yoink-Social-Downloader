import os
import sys
import ctypes
import webview
from backend.api import YoinkAPI
from backend.config import ensure_directories

def get_asset_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller bundle."""
    if hasattr(sys, '_MEIPASS'):
        target = os.path.join(sys._MEIPASS, relative_path)
        if os.path.exists(target):
            return target
    # Check directory of executable in onedir mode
    exe_dir = os.path.dirname(sys.executable)
    path_next_to_exe = os.path.join(exe_dir, relative_path)
    if os.path.exists(path_next_to_exe):
        return path_next_to_exe
    return os.path.join(os.path.abspath("."), relative_path)

def main():
    # Set explicit AppUserModelID on Windows for pristine taskbar grouping & icon resolution
    if sys.platform == "win32":
        try:
            myappid = "yoink.social.downloader.pro.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            print(f"[Main] AppUserModelID notice: {e}")

    # Ensure download directories exist in AppData and User Downloads
    ensure_directories()

    # Paths
    html_path = get_asset_path(os.path.join("frontend", "index.html"))
    icon_path = get_asset_path(os.path.join("assets", "icons", "app_icon.ico"))
    
    if not os.path.exists(icon_path):
        icon_path = None

    # Instantiate API bridge
    api = YoinkAPI()

    window_title = "Yoink Social — Multi-Platform Media Downloader"

    # Create PyWebView window with local path (not file:// to avoid .NET UriFormatException)
    window = webview.create_window(
        title=window_title,
        url=html_path,
        js_api=api,
        width=1140,
        height=820,
        min_size=(1000, 700),
        background_color="#090c13"
    )

    api.set_window(window)

    def on_shown():
        try:
            if sys.platform == "win32" and icon_path and os.path.exists(icon_path):
                # Apply native Win32 WM_SETICON directly to window HWND for both taskbar & titlebar
                user32 = ctypes.windll.user32
                hwnd = None
                if hasattr(window, 'native') and window.native:
                    try:
                        hwnd = int(window.native.Handle.ToInt64())
                    except Exception:
                        pass
                if not hwnd and hasattr(window, 'gui') and window.gui:
                    try:
                        hwnd = int(window.gui.Handle.ToInt64())
                    except Exception:
                        pass
                if not hwnd:
                    hwnd = user32.FindWindowW(None, window_title)

                if hwnd:
                    IMAGE_ICON = 1
                    LR_LOADFROMFILE = 0x00000010
                    LR_DEFAULTSIZE = 0x00000040
                    WM_SETICON = 0x0080
                    hicon_big = user32.LoadImageW(None, icon_path, IMAGE_ICON, 0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE)
                    hicon_small = user32.LoadImageW(None, icon_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)
                    if hicon_big:
                        user32.SendMessageW(hwnd, WM_SETICON, 1, hicon_big)
                    if hicon_small:
                        user32.SendMessageW(hwnd, WM_SETICON, 0, hicon_small)
        except Exception as e:
            print(f"[Main] Icon setting error: {e}")

    # Start pywebview loop with http_server=True
    # This serves frontend via local Bottle server, preventing file:// cross-origin and Uri issues
    webview.start(
        on_shown,
        debug=False,
        http_server=True,
        gui="edgechromium",
        icon=icon_path if (icon_path and os.path.exists(icon_path)) else None
    )

if __name__ == "__main__":
    main()
