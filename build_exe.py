"""
Yoink Social — Automated Packaging Script
1. Compiles Python application into a standalone Windows EXE using PyInstaller.
2. Compiles Inno Setup script (if ISCC is available) into Setup.exe wizard.
"""
import os
import sys
import shutil
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def find_inno_compiler():
    # 1. Check in PATH
    iscc = shutil.which("iscc")
    if iscc:
        return iscc

    # 2. Check standard Program Files locations
    candidates = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 7\ISCC.exe",
        r"C:\Program Files\Inno Setup 7\ISCC.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe")
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def build():
    print("==================================================")
    print("      Yoink Social — Build & Packaging Pipeline   ")
    print("==================================================")

    # 1. Ensure latest app icons and installer branding exist
    print("[Build] Generating latest high-res app icons & wizard branding...")
    subprocess.run([sys.executable, os.path.join(PROJECT_ROOT, "assets", "generate_icons.py")], check=True)
    ico_path = os.path.join(PROJECT_ROOT, "assets", "icons", "app_icon.ico")

    # 2. Run PyInstaller
    print("\n[1/2] Compiling standalone Windows binaries via PyInstaller...")
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        f"--icon={ico_path}",
        "--name=YoinkSocial",
        "--add-data=frontend;frontend",
        "--add-data=assets;assets",
        "--collect-all=yt_dlp",
        "--collect-all=webview",
        "--hidden-import=backend",
        "--hidden-import=instaloader",
        "--hidden-import=pythonnet",
        "--hidden-import=clr",
        "main.py"
    ]

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print("\n[Build ERROR] PyInstaller build failed.")
        sys.exit(result.returncode)

    exe_dist = os.path.join(PROJECT_ROOT, "dist", "YoinkSocial", "YoinkSocial.exe")
    if os.path.exists(exe_dist):
        print(f"\n[PyInstaller SUCCESS] Executable created at:\n  -> {exe_dist}")

    # 3. Compile Inno Setup Installer
    print("\n[2/2] Checking for Inno Setup compiler (ISCC)...")
    iscc_path = find_inno_compiler()
    iss_file = os.path.join(PROJECT_ROOT, "installer", "yoink_social.iss")

    if iscc_path:
        print(f"Found Inno Setup at: {iscc_path}")
        print("Compiling Setup.exe wizard...")
        iscc_cmd = [iscc_path, iss_file]
        res_iss = subprocess.run(iscc_cmd, cwd=os.path.join(PROJECT_ROOT, "installer"))
        if res_iss.returncode == 0:
            setup_exe = os.path.join(PROJECT_ROOT, "dist_installer", "YoinkSocial_Setup_v1.0.exe")
            print(f"\n==================================================")
            print(f"[SUCCESS] BUILD COMPLETE!")
            print(f"Installer Wizard: {setup_exe}")
            print(f"Standalone Folder: {os.path.dirname(exe_dist)}")
            print(f"==================================================")
        else:
            print("[Build Warning] Inno Setup compilation exited with error code.")
    else:
        print("ℹ️ Inno Setup compiler (ISCC.exe) belum terdeteksi di sistem.")
        print("Untuk menghasilkan file 'Setup.exe' wizard:")
        print("1. Install Inno Setup via PowerShell: winget install JRSoftware.InnoSetup -e")
        print("2. Jalankan ulang script ini: python build_exe.py")
        print("\nStandalone executable siap dijalankan dari:")
        print(f"  -> {exe_dist}")

if __name__ == "__main__":
    build()
