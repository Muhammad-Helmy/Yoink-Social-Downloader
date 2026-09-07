from .base import BaseDownloader
from .youtube import YouTubeDownloader
from .facebook import FacebookDownloader
from .instagram import InstagramDownloader
from .tiktok import TikTokDownloader

def get_downloader(platform: str) -> BaseDownloader:
    p = platform.lower()
    if p == "youtube":
        return YouTubeDownloader()
    elif p == "facebook":
        return FacebookDownloader()
    elif p == "instagram":
        return InstagramDownloader()
    elif p == "tiktok":
        return TikTokDownloader()
    else:
        raise ValueError(f"Platform tidak didukung: {platform}")
