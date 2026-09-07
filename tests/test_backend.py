"""
Automated unit verification for Yoink Social backend modules
"""
import os
import sys
import unittest

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.config import get_config, get_platform_folder, ensure_directories, set_platform_folder
from backend.logger import translate_error, format_progress_status, LogLevel, create_log_entry
from backend.downloaders import get_downloader
from backend.api import YoinkAPI

class TestYoinkBackend(unittest.TestCase):
    def test_config_initialization(self):
        ensure_directories()
        cfg = get_config()
        self.assertIn("download_folders", cfg)
        self.assertIn("youtube", cfg["download_folders"])
        self.assertIn("tiktok", cfg["download_folders"])
        self.assertIn("instagram", cfg["download_folders"])
        self.assertIn("facebook", cfg["download_folders"])

        yt_folder = get_platform_folder("youtube")
        self.assertTrue(os.path.exists(yt_folder))

    def test_logger_translations(self):
        # 403 Forbidden
        msg_403 = translate_error("HTTP Error 403: Forbidden", "tiktok")
        self.assertIn("HTTP 403", msg_403)
        self.assertIn("⚠️", msg_403)

        # Private video
        msg_priv = translate_error("This video is private and cannot be downloaded", "youtube")
        self.assertIn("privat", msg_priv)

        # Format progress
        fake_hook = {
            "status": "downloading",
            "total_bytes": 10000000,
            "downloaded_bytes": 4500000,
            "speed": 2097152,
            "eta": 15
        }
        res = format_progress_status(fake_hook, title="Tutorial Python", quality="1080p", format_type="video")
        self.assertEqual(res["percent"], 45.0)
        self.assertIn("2.0 MB/s", res["speed"])
        self.assertEqual(res["eta"], "00:15")
        self.assertIn("⬇️", res["message"])

    def test_downloaders_instantiation(self):
        yt = get_downloader("youtube")
        self.assertEqual(yt.platform_name, "youtube")

        tt = get_downloader("tiktok")
        self.assertEqual(tt.platform_name, "tiktok")

        ig = get_downloader("instagram")
        self.assertEqual(ig.platform_name, "instagram")

        fb = get_downloader("facebook")
        self.assertEqual(fb.platform_name, "facebook")

    def test_api_initialization(self):
        api = YoinkAPI()
        settings = api.get_settings()
        self.assertIn("download_folders", settings)

        # Test empty URL handling (English is default)
        info_res = api.fetch_info("youtube", "")
        self.assertFalse(info_res["success"])
        self.assertTrue("URL" in info_res["error"] or "url" in info_res["error"].lower())

    def test_url_normalization_and_photo_resolvers(self):
        # 1. Instagram shortcode normalization
        ig = get_downloader("instagram")
        shortcode, clean_ig = ig._normalize_url("https://www.instagram.com/reels/C8XYZ123/?igsh=MWx1Y2Vp")
        self.assertEqual(shortcode, "C8XYZ123")
        self.assertEqual(clean_ig, "https://www.instagram.com/p/C8XYZ123/")

        # 2. TikTok address-bar search query cleaning
        tt = get_downloader("tiktok")
        dirty_tt = "https://www.tiktok.com/@thunderclouds_19/video/7637907950903807253?q=harleys%20in%20hawaii&t=1788747881814"
        clean_tt = tt._clean_url(dirty_tt)
        self.assertEqual(clean_tt, "https://www.tiktok.com/@thunderclouds_19/video/7637907950903807253")

        # 3. Facebook photo metadata extraction
        fb = get_downloader("facebook")
        photo_info = fb._fetch_og_photo_info("https://www.facebook.com/photo/?fbid=3562027953978802")
        self.assertTrue(photo_info["success"])
        self.assertTrue(photo_info["has_image"])
        self.assertIn("3562027953978802", photo_info["images"][0])

    def test_facebook_private_detection(self):
        fb = get_downloader("facebook")
        # Private group link without public metadata should flag is_private
        res = fb.fetch_info("https://www.facebook.com/groups/secretgroup12345/posts/9999999999/")
        self.assertFalse(res["success"])
        self.assertTrue(res.get("is_private", False))

    def test_history_fifo(self):
        from backend.config import add_history_entry, get_history, clear_history
        clear_history()
        self.assertEqual(len(get_history()), 0)

        # Add 12 items, verify capped at 10 and FIFO
        for i in range(12):
            add_history_entry({
                "title": f"Video {i}",
                "platform": "youtube",
                "format": "video",
                "filepath": f"C:/fake/path/{i}.mp4"
            })
        history = get_history()
        self.assertEqual(len(history), 10)
        # Most recent item should be at the top (Video 11)
        self.assertEqual(history[0]["title"], "Video 11")
        # Oldest preserved item should be Video 2
        self.assertEqual(history[-1]["title"], "Video 2")
        clear_history()

    def test_universal_queue(self):
        api = YoinkAPI()
        # Empty queue check
        q = api.get_queue()
        self.assertEqual(q["total"], 0)

        # Enqueue tasks for different platforms without network download execution
        with api._queue_lock:
            api._queue.append({"id": "task_1", "platform": "youtube", "title": "YT Video 1", "status": "queued"})
            api._queue.append({"id": "task_2", "platform": "tiktok", "title": "TT Video 1", "status": "queued"})
            api._queue.append({"id": "task_3", "platform": "instagram", "title": "IG Reel 1", "status": "queued"})

        q_after = api.get_queue()
        self.assertEqual(q_after["total"], 3)
        self.assertEqual(len(q_after["queue"]), 3)
        self.assertEqual(q_after["queue"][0]["platform"], "youtube")
        self.assertEqual(q_after["queue"][1]["platform"], "tiktok")
        self.assertEqual(q_after["queue"][2]["platform"], "instagram")

        # Test cancel from queue by ID
        cancel_res = api.cancel_download("task_2")
        self.assertTrue(cancel_res["success"])
        q_cancelled = api.get_queue()
        self.assertEqual(q_cancelled["total"], 2)
        self.assertEqual(q_cancelled["queue"][0]["id"], "task_1")
        self.assertEqual(q_cancelled["queue"][1]["id"], "task_3")

    def test_file_resolution_and_history_healing(self):
        from backend.downloaders.base import BaseDownloader
        from backend.config import _heal_history_item
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Simulate an intermediate DASH stream file that was merged to .mp4
            final_mp4 = os.path.join(tmpdir, "IG_MyVideo_12345.mp4")
            with open(final_mp4, "wb") as f:
                f.write(b"0" * 2048)  # 2KB

            fake_dash_m4a = os.path.join(tmpdir, "IG_MyVideo_12345.fdash-9999.m4a")

            resolved = BaseDownloader.resolve_final_output_file(
                output_dir=tmpdir,
                info=None,
                downloaded_filepath=fake_dash_m4a,
                format_type="video",
                vid_id="12345"
            )
            self.assertEqual(os.path.normpath(resolved), os.path.normpath(final_mp4))

            # Test history item healing
            broken_entry = {
                "id": "test_1",
                "title": "Media File",
                "platform": "instagram",
                "format": "video",
                "file_path": fake_dash_m4a,
                "filename": os.path.basename(fake_dash_m4a),
                "size_str": "--"
            }
            healed = _heal_history_item(broken_entry)
            self.assertTrue(healed)
            self.assertEqual(os.path.normpath(broken_entry["file_path"]), os.path.normpath(final_mp4))
            self.assertEqual(broken_entry["size_str"], "2 KB")
            self.assertIn("MyVideo", broken_entry["title"])

if __name__ == "__main__":
    unittest.main()


