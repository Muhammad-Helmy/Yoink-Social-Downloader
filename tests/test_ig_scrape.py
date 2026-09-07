import requests
import re
import html

def check_ig_embed(shortcode):
    url = f"https://www.instagram.com/p/{shortcode}/embed/captioned/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }
    r = requests.get(url, headers=headers, timeout=10)
    print("IG embed status:", r.status_code)
    
    # Check video
    video_matches = re.findall(r'video_url["\']:\s*["\']([^"\']+)["\']', r.text)
    if not video_matches:
        video_matches = re.findall(r'class="EmbeddedMediaVideo"[^>]*src="([^"]+)"', r.text)
    
    # Check image
    img_matches = re.findall(r'display_url["\']:\s*["\']([^"\']+)["\']', r.text)
    if not img_matches:
        img_matches = re.findall(r'class="EmbeddedMediaImage"[^>]*src="([^"]+)"', r.text)

    caption_matches = re.findall(r'class="Caption"[^>]*>(.*?)</div>', r.text, re.DOTALL)
    caption = re.sub(r'<[^>]+>', '', caption_matches[0]).strip() if caption_matches else ""

    print("Found video urls:", len(video_matches))
    print("Found image urls:", len(img_matches))
    print("Caption:", caption[:80])

    if img_matches:
        print("First image:", html.unescape(img_matches[0].encode().decode('unicode_escape'))[:120])
    if video_matches:
        print("First video:", html.unescape(video_matches[0].encode().decode('unicode_escape'))[:120])

if __name__ == "__main__":
    check_ig_embed("C8qLqg-vx1P")
