<p align="center">
  <img src="assets/icons/app_icon.png" alt="Yoink Social Logo" width="130" height="130" style="border-radius: 26px; box-shadow: 0 12px 30px rgba(0, 240, 255, 0.35);">
</p>

<h1 align="center">Yoink Social PRO</h1>

<p align="center">
  <b>The Ultimate Multi-Platform Social Media Downloader with a Modern Cyber-Glass Interface</b>
</p>

<p align="center">
  <a href="https://github.com/Muhammad-Helmy/Yoink-Social-Downloader/releases/latest"><img src="https://img.shields.io/github/v/release/Muhammad-Helmy/Yoink-Social-Downloader?style=for-the-badge&color=00f0ff&label=Release" alt="Latest Release"></a>
  <img src="https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011%20(64--bit)-00f0ff?style=for-the-badge&logo=windows" alt="Platform">
  <img src="https://img.shields.io/badge/Python-3.10+-7928ca?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-00f0ff?style=for-the-badge" alt="License">
</p>

<p align="center">
  <a href="https://github.com/Muhammad-Helmy/Yoink-Social-Downloader/releases/latest/download/YoinkSocial_Setup_v1.0.exe">
    <img src="https://img.shields.io/badge/DOWNLOAD%20NOW-Windows%20Installer%20(.exe)-00f0ff?style=for-the-badge&logo=windows&logoColor=black" alt="Download Windows Installer" height="42">
  </a>
</p>

---

## ⚡ Overview

**Yoink Social PRO** is a premium, high-performance desktop application designed to download media effortlessly from the world's most popular social networks—**YouTube**, **TikTok**, **Instagram**, and **Facebook**.

Engineered with an ultra-responsive **Dark Cyber Glass UI**, fluid real-time micro-animations, liquid glass water-drop sound effects (SFX), and an asynchronous multi-threaded download engine, Yoink Social gives you full control over your media archive in resolutions up to 4K / 60 FPS and pristine audio bitrates.

---

## 📥 Direct Download (Windows)

You can grab the official one-click Windows Setup installer directly from the releases page:

| Package | Version | Download Link | Architecture |
| :--- | :--- | :--- | :--- |
| **Yoink Social Setup** (`.exe`) | **v1.0.0** | [**Download YoinkSocial_Setup_v1.0.exe**](https://github.com/Muhammad-Helmy/Yoink-Social-Downloader/releases/latest/download/YoinkSocial_Setup_v1.0.exe) | Windows 10/11 (64-bit) |
| **All Releases & Changelogs** | — | [**View GitHub Releases**](https://github.com/Muhammad-Helmy/Yoink-Social-Downloader/releases) | Standalone & Setup |

> **Note:** If Windows SmartScreen or antivirus prompts a warning on your first run, click **"More Info"** → **"Run anyway"** (this is standard for newly published open-source binaries that do not yet have paid EV code signing certificates).

---

## ✨ Key Features

### 🌐 Comprehensive Platform Support
* **YouTube**: Download full videos (up to 4K/60fps), audio-only extraction (high-bitrate MP3/M4A), video thumbnails, and entire playlist sequences.
* **TikTok**: Instant watermark-free HD video downloads, slideshow carousel photo sets, and isolated audio extraction.
* **Instagram**: Download Reels, single video/photo feed posts, and multi-slide carousel albums with one click.
* **Facebook**: Download Reels, public HD videos, and full-resolution photo posts directly from feed URLs.

### 🎨 State-of-the-Art Cyber Glass Aesthetics
* **Dynamic Glassmorphism**: Deep space obsidian theme with neon cyan & electric purple glow accents, frosted glass backdrop blurs, and polished chrome borders.
* **Liquid Glass SFX**: Satisfying tactile audio feedback (fluid water-drop sound) synchronized with interactive clicks.
* **Responsive Layout**: Dedicated platform viewports with custom scroll containers and adaptive spacing.

### 🔄 Smart Universal Queue & Task Separation
* **Platform-Dedicated Queues**: Clean, independent input spaces for each social platform so queues never cross-contaminate.
* **FIFO Universal Scheduler**: Tasks execute sequentially in the background while queued items remain visible in the queue without freezing the UI.
* **Live Task Tracker**: Real-time progress bar, transfer speed (KB/s - MB/s), ETA countdown, and file size detection.
* **History Management**: Comprehensive log of completed downloads with direct **"Open File"** and **"Open Folder"** explorer buttons.

### 🛡️ Intelligent Private-Content Modal
* Detects private Facebook groups, restricted accounts, and inaccessible media URLs automatically.
* Displays an informative cyber glass modal advising the user of permission limitations instead of throwing generic crashes.

### 🌍 Multi-Language Ready
* Seamless one-click toggle between **English** and **Bahasa Indonesia** with instant UI translation.

---

## 🚀 Installation & Getting Started

### Method 1: Windows Installer (Recommended for Users)
1. Download **[YoinkSocial_Setup_v1.0.exe](https://github.com/Muhammad-Helmy/Yoink-Social-Downloader/releases/latest/download/YoinkSocial_Setup_v1.0.exe)**.
2. Run the installer wizard and follow the on-screen instructions.
3. Launch **Yoink Social** from your Desktop shortcut or Start Menu.

### Method 2: Running from Source (For Developers)

#### Prerequisites
* Windows 10 or 11 (64-bit)
* Python 3.10, 3.11, or 3.12 installed
* Git installed

#### Step 1: Clone Repository
```bash
git clone https://github.com/Muhammad-Helmy/Yoink-Social-Downloader.git
cd Yoink-Social-Downloader
```

#### Step 2: Set Up Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Run Application
```bash
python main.py
```

---

## 🛠️ Building the Binary & Installer

If you wish to package Yoink Social into an executable and Inno Setup installer locally:

```bash
# Compile standalone binary (PyInstaller) and Setup installer (Inno Setup)
python build_exe.py
```
* **Executable Output**: `dist/YoinkSocial/YoinkSocial.exe`
* **Installer Output**: `dist_installer/YoinkSocial_Setup_v1.0.exe`

---

## 🧩 Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **GUI Framework** | [PyWebView](https://pywebview.flowrl.com/) + Win32 Native Integration |
| **Frontend UI** | HTML5, Modern CSS3 Glassmorphism, Vanilla ES6+ JavaScript |
| **Backend Core** | Python 3.10+, Asynchronous Workers, Multi-Threading |
| **Downloader Engines** | [yt-dlp](https://github.com/yt-dlp/yt-dlp), Instaloader, Beautiful Soup 4, Requests |
| **Packaging & Setup** | PyInstaller, Inno Setup 6 |

---

## ⚠️ Disclaimer

Yoink Social PRO is developed for personal archiving, backup, and fair-use educational purposes. Please respect the copyright, licensing, and intellectual property rights of content creators on YouTube, TikTok, Instagram, and Facebook. Always obtain permission before downloading or repurposing media that is not yours.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

<p align="center">
  Crafted with ❤️ by <a href="https://github.com/Muhammad-Helmy">Muhammad Helmy</a>
</p>