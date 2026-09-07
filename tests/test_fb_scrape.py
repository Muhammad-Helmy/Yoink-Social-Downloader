import urllib.request
import re
import html

def test_fb(url):
    print("Testing Facebook URL:", url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            content = resp.read().decode('utf-8', 'ignore')
            final_url = resp.geturl()
            print("Redirected URL:", final_url)

            # Find og:image
            og_match = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']', content)
            if not og_match:
                og_match = re.search(r'<meta\s+content=["\']([^"\']+)["\']\s+property=["\']og:image["\']', content)

            title_match = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\']([^"\']+)["\']', content)

            if og_match:
                img_url = html.unescape(og_match.group(1))
                print("FOUND og:image:", img_url)
            else:
                print("No og:image meta tag found.")

            if title_match:
                print("FOUND og:title:", html.unescape(title_match.group(1)))

            # Check if video playable_url exists in page content
            video_matches = re.findall(r'"playable_url(?:_quality_hd)?":"([^"]+)"', content)
            if video_matches:
                print("Found video streams count:", len(video_matches))

    except Exception as e:
        print("Scrape failed:", e)

if __name__ == "__main__":
    test_fb("https://www.facebook.com/share/p/1HLry557sd/")
    test_fb("https://www.facebook.com/photo/?fbid=3562027953978802")
