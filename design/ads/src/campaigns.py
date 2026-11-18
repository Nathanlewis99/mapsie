"""design/ads/campaigns.csv: every ad, where it runs, its file and its tagged link.

    python3 design/ads/src/campaigns.py
utm_source = platform, utm_medium = paid, utm_campaign = angle, utm_content = file stem,
so each sale shows under the right campaign in /admin/channels.
"""
import csv
from pathlib import Path
from urllib.parse import urlencode

SITE = "https://mapsie.shop"
DEST = {
    "xmas-gift": "/maps/christmas-travel-map-gift",
    "honeymoon": "/maps/honeymoon-map-print",
    "adventure": "/maps/road-trip-map-poster",
    "adventure-backpacking": "/maps/backpacking-travel-map",
    "gift-card": "/gift",
    "photos": "/create",
    "design": "/create",
}
# (file, campaign, destination key)
STATICS = [
    ("christmas-gift", "xmas-gift", "xmas-gift"),
    ("honeymoon", "honeymoon", "honeymoon"),
    ("adventure", "adventure", "adventure"),
    ("gift-card", "gift-card", "gift-card"),
    ("your-photos", "photos", "photos"),
]
VIDEOS = [
    ("describe-your-trip", "adventure", "design"),
    ("your-photos", "photos", "photos"),
    ("framed-detail-vertical", "adventure", "adventure-backpacking"),
    ("gift-card-christmas", "gift-card", "gift-card"),
]
PLACEMENTS = {
    # platform: [(placement, kind, size)]
    "instagram": [("Feed", "static", "1080x1350"), ("Reels / Stories", "video", None)],
    "facebook": [("Feed", "static", "1080x1080"), ("Reels / Stories", "video", None)],
    "pinterest": [("Standard pin", "static", "1000x1500"), ("Video pin", "video", None)],
}


def url(platform, campaign, dest, content):
    q = urlencode({"utm_source": platform, "utm_medium": "paid", "utm_campaign": campaign, "utm_content": content})
    return f"{SITE}{DEST[dest]}?{q}"


rows = []
for platform, places in PLACEMENTS.items():
    for placement, kind, size in places:
        items = STATICS if kind == "static" else VIDEOS
        for name, campaign, dest in items:
            f = f"static/{name}-{size}.jpg" if kind == "static" else f"video/{name}.mp4"
            stem = Path(f).stem
            rows.append({
                "ad_name": f"{platform}-{campaign}-{stem}",
                "platform": platform,
                "placement": placement,
                "format": "image" if kind == "static" else "video 9:16",
                "file": f"design/ads/{f}",
                "campaign": campaign,
                "destination_url": url(platform, campaign, dest, stem),
            })
# Google Search ads (copy in copy.md) and Etsy Ads (no links: Etsy places them itself).
for group, campaign, dest in [("rsa-travel-map", "adventure", "design"), ("rsa-honeymoon", "honeymoon", "honeymoon"), ("rsa-road-trip", "adventure", "adventure"), ("rsa-gift-card", "gift-card", "gift-card")]:
    rows.append({"ad_name": f"google-{campaign}-{group}", "platform": "google", "placement": "Search (responsive search ad)", "format": "text", "file": "design/ads/copy.md", "campaign": campaign, "destination_url": url("google", campaign, dest, group)})
rows.append({"ad_name": "etsy-ads-listings", "platform": "etsy", "placement": "Etsy Ads (search)", "format": "listing", "file": "design/ads/copy.md", "campaign": "etsy", "destination_url": "(Etsy listings; no UTM links on Etsy)"})

with open("design/ads/campaigns.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(len(rows), "ads")
