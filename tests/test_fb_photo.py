import requests
import re
import html

def check_photo(fbid):
    urls = [
        f"https://www.facebook.com/photo.php?fbid={fbid}",
        f"https://mbasic.facebook.com/photo.php?fbid={fbid}",
        f"https://m.facebook.com/photo.php?fbid={fbid}",
        f"https://m.facebook.com/photo/?fbid={fbid}",
        f"https://lookaside.fbsbx.com/lookaside/crawler/media/?media_id={fbid}"
    ]
    for u in urls:
        print("\n--- Trying URL:", u)
        try:
            # Try with facebookexternalhit first
            r = requests.get(u, headers={'User-Agent': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'}, timeout=8, allow_redirects=True)
            print("bot status:", r.status_code, "final:", r.url)
            og_img = re.search(r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', r.text)
            if og_img:
                print("Found OG Image via bot:", html.unescape(og_img.group(1)))
                return html.unescape(og_img.group(1))

            # Try with Chrome
            r2 = requests.get(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}, timeout=8, allow_redirects=True)
            print("chrome status:", r2.status_code, "final:", r2.url)
            # Find image URLs in HTML
            cdn_imgs = re.findall(r'https://[^\s"\'<>]*(?:fbcdn\.net|fbsbx\.com)[^\s"\'<>]*', r2.text)
            clean_imgs = [html.unescape(x) for x in cdn_imgs if "scontent" in x or "lookaside" in x or "fna" in x]
            if clean_imgs:
                print("Found CDN images:", len(clean_imgs), clean_imgs[0][:120])
                return clean_imgs[0]
        except Exception as e:
            print("Error:", e)
    return None

if __name__ == "__main__":
    check_photo("3562027953978802")
