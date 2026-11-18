"""Ad copy for every platform and angle, checked against each platform's limits.

    python3 design/ads/src/ad_copy.py   ->  design/ads/copy.md (fails if anything is over a limit)

Prices and dates match src/lib/products.ts and src/lib/christmas.ts (UK, Nov 2026):
prints from £34, framed from £69, digital file £19, order by Wed 16 Dec for Christmas.
No reviews, ratings, "bestseller" or customer-count claims until they're real.
"""
from pathlib import Path

LIMITS = {"meta_primary": 125, "meta_headline": 40, "pin_title": 100, "pin_desc": 500, "rsa_headline": 30, "rsa_desc": 90}

ANGLES = {
    "christmas-gift": {
        "label": "Christmas gift",
        "meta_primary": [
            "The gift they'll actually hang up: a map of their favourite trip, every stop and memory. Order by 16 Dec.",
            "Stuck for a present? Turn their best trip into a framed map print. Designed in minutes, delivered free.",
            "Their honeymoon, gap year or road trip, printed, framed and on the wall by Christmas. Prints from £34.",
        ],
        "meta_headline": ["The gift they'll actually hang up", "Their favourite trip, framed", "Order by 16 Dec for Christmas"],
        "pin_title": ["Personalised travel map gift: their favourite trip, framed", "Christmas gift idea for travellers: a custom map print of their trip"],
        "pin_desc": [
            "Looking for a Christmas gift for someone who loves to travel? Design a custom map print of their favourite trip, with every stop, the route between them, illustrated stickers and their own photos. Printed to order, framed if you like, and delivered free in the UK, US and Australia. Order by 16 December for UK delivery before Christmas, or give a gift card.",
        ],
    },
    "honeymoon": {
        "label": "Honeymoon",
        "meta_primary": [
            "Your honeymoon, on your wall: every stop, the route and your own photos, printed and framed.",
            "From the first flight to the last sunset. Turn your honeymoon into a map print you'll keep forever.",
            "A wedding or anniversary gift with a story: a custom map of your honeymoon, from £34.",
        ],
        "meta_headline": ["Your honeymoon, on your wall", "Map your honeymoon", "A gift with your story on it"],
        "pin_title": ["Honeymoon map print: your trip, your photos, framed", "Personalised honeymoon gift: a custom map of your trip together"],
        "pin_desc": [
            "Turn your honeymoon into a custom map print. Add every place you stayed and Mapsie draws the route: the flight out, the train along the coast, the boat to the island. Pin your own photos where they were taken, add your names and wedding date, and choose a frame. A personal wedding, anniversary or Christmas gift, printed and delivered free.",
        ],
    },
    "adventure": {
        "label": "Adventure / road trip / backpacking",
        "meta_primary": [
            "Every stop. Every route. Flights, trains, road trips and tuk-tuks, drawn on the real roads you took.",
            "That trip deserves more than a camera roll. Turn it into a map print for your wall, from £34.",
            "Road trip, gap year or Interrail? Add your stops and Mapsie draws the route. Printed and framed.",
        ],
        "meta_headline": ["Every stop. Every route.", "Your trip as a map print", "Drawn on the real roads"],
        "pin_title": ["Road trip map poster that follows the roads you drove", "Backpacking travel map print: every country, flight and bus on one map"],
        "pin_desc": [
            "Make a custom travel map poster of your road trip, gap year or Interrail adventure. Mapsie follows the real roads you drove, arcs the flights between continents and marks every train, bus, boat and tuk-tuk. Add stickers of what you did and your own photos, choose a style, and get it printed and framed. From £34 with free delivery.",
        ],
    },
    "gift-card": {
        "label": "Gift card",
        "meta_primary": [
            "Not sure where they went? Give a Mapsie gift card and they'll design a map of their favourite trip.",
            "The last-minute gift that isn't last-minute: emailed instantly, or on Christmas morning. From £10.",
            "Let them map their own adventure. A gift card for a custom map print, any amount from £10.",
        ],
        "meta_headline": ["Give a travel map gift card", "Emailed instantly, or on Christmas Day", "They design their own map"],
        "pin_title": ["Travel map gift card: let them design a map of their favourite trip", "Last-minute gift for travellers: a map print gift card"],
        "pin_desc": [
            "Don't know the trip details? Give a Mapsie gift card. They design their own custom map print of a trip they love, with the route, stickers and their own photos, and we print and deliver it. Emailed to you or straight to them, even on Christmas morning, with a printable card for an envelope. Any leftover balance is kept for their next map.",
        ],
    },
    "your-photos": {
        "label": "Your photos",
        "meta_primary": [
            "Pin your own trip photos to the map, right where you took them. Polaroid, heart or stamp. From £34.",
            "Your photos, your route, your stickers: one map of the whole trip, printed and framed for your wall.",
            "Every photo has a place. Add yours to a custom map of your trip and get it printed and delivered.",
        ],
        "meta_headline": ["Pin your photos to the map", "Your trip photos, mapped", "Polaroid, heart or stamp"],
        "pin_title": ["Custom travel map with your own photos pinned where you took them", "Photo map print: your trip photos on a map of your route"],
        "pin_desc": [
            "Turn your travel photos into something better than a camera roll. Upload photos from your trip and pin them to a custom map, right where they were taken, as polaroids, stamps, circles or hearts. Mapsie draws your route between every stop and adds illustrated stickers. Printed sharp at 300 dpi, framed if you like, delivered free.",
        ],
    },
}

# Google responsive search ads: one ad group per keyword theme.
RSA = {
    "custom travel map print": {
        "keywords": ["custom travel map print", "personalised travel map", "map of my travels print", "travel map poster custom", "personalized trip map"],
        "url": "https://mapsie.shop/?utm_source=google&utm_medium=paid&utm_campaign=adventure&utm_content=rsa-travel-map",
        "headlines": [
            "Custom Travel Map Prints", "Map Your Trip, Every Stop", "Your Route, Drawn for Real", "Prints From £34",
            "Free Delivery", "Framed or Unframed", "Add Your Own Trip Photos", "Design Yours in Minutes",
            "Printed in the UK, US & AU", "12 Map Styles to Choose", "Flights, Trains & Road Trips", "See It on Your Wall First",
            "Personalised Travel Map", "Order by 16 Dec for Xmas", "Mapsie Custom Map Prints",
        ],
        "descriptions": [
            "Add your stops and Mapsie draws the route, on the real roads. Printed at 300 dpi.",
            "Stickers, your own photos and 12 styles. Framed in wood with Perspex, ready to hang.",
            "Free to design and preview on a wall before you buy. Prints from £34, free delivery.",
            "A gift they'll actually hang up. Order by 16 December for UK delivery by Christmas.",
        ],
    },
    "honeymoon map gift": {
        "keywords": ["honeymoon map print", "honeymoon gift", "anniversary map gift", "wedding map print", "personalised honeymoon gift"],
        "url": "https://mapsie.shop/maps/honeymoon-map-print?utm_source=google&utm_medium=paid&utm_campaign=honeymoon&utm_content=rsa-honeymoon",
        "headlines": [
            "Honeymoon Map Prints", "Your Honeymoon, Framed", "Personalised Anniversary Gift", "Add Your Wedding Date",
            "Pin Your Honeymoon Photos", "Every Stop of Your Trip", "Prints From £34", "Free Delivery",
            "Framed and Ready to Hang", "A Gift With Your Story", "Design It in Minutes", "Romantic Blush Map Style",
            "Order by 16 Dec for Xmas", "Paper or Cotton Anniversary", "Mapsie Honeymoon Maps",
        ],
        "descriptions": [
            "Turn your honeymoon into a map print: every stop, the route and your own photos.",
            "Add your names, wedding date and a message. Framed in wood, delivered free.",
            "A personal wedding or anniversary gift. Preview it on a wall before you order.",
            "Matte art or cotton rag paper for paper and cotton anniversaries. From £34.",
        ],
    },
    "road trip map poster": {
        "keywords": ["road trip map poster", "road trip map print", "route 66 map print", "custom road trip map", "campervan trip map"],
        "url": "https://mapsie.shop/maps/road-trip-map-poster?utm_source=google&utm_medium=paid&utm_campaign=adventure&utm_content=rsa-road-trip",
        "headlines": [
            "Road Trip Map Posters", "Follows the Roads You Drove", "Your Route, Every Detour", "Custom Road Trip Print",
            "Route 66, NC500 & More", "Add Every Stop", "Prints From £34", "Free Delivery",
            "Framed or Unframed", "Campervan & Motorbike Icons", "Add Your Trip Photos", "Design Yours in Minutes",
            "Vintage Road-Atlas Styles", "Order by 16 Dec for Xmas", "Mapsie Road Trip Maps",
        ],
        "descriptions": [
            "Most map prints draw straight lines. Mapsie follows the real roads you drove.",
            "Add as many stops as you like, mark each leg, add stickers and your own photos.",
            "Vintage, Explorer and 10 more styles. Printed at 300 dpi and delivered free.",
            "The perfect gift for road trippers. Order by 16 December for UK Christmas delivery.",
        ],
    },
    "travel map gift card": {
        "keywords": ["travel gift card", "map gift card", "gift for travellers", "last minute travel gift", "travel map gift"],
        "url": "https://mapsie.shop/gift?utm_source=google&utm_medium=paid&utm_campaign=gift-card&utm_content=rsa-gift-card",
        "headlines": [
            "Travel Map Gift Cards", "They Design Their Own Map", "Emailed Instantly", "Send on Christmas Morning",
            "Gift Cards From £10", "Any Amount From £10", "Printable Gift Card", "Leftover Balance Kept",
            "Gift for Travel Lovers", "Valid for 2 Years", "No Need to Know the Trip", "Last-Minute Gift Sorted",
            "Custom Map Print Gift", "Add a Personal Message", "Mapsie Gift Cards",
        ],
        "descriptions": [
            "Don't know the trip details? They design a map of their favourite trip themselves.",
            "Emailed to you or straight to them, even on Christmas morning. Printable card too.",
            "Choose an amount to cover a print, a framed print or a digital file. From £10.",
            "Any balance they don't use is kept as a new code for their next map. Valid 2 years.",
        ],
    },
}

ETSY_NOTES = """- Etsy Ads (Shop Manager > Marketing > Etsy Ads): start at £2/day across both listings; Etsy chooses keywords automatically.
- Keep listing titles keyword-led for Etsy search, e.g. "Personalised Travel Map Print, Custom Trip Map, Honeymoon Gift, Road Trip Poster, Framed".
- Use the 13 tags for: custom travel map, personalised map print, honeymoon gift, anniversary gift, road trip poster, backpacking gift, interrail map, travel lover gift, map with photos, christmas gift traveller, framed map print, wedding gift map, gap year gift.
- Lead with photo 01 (framed South East Asia) and video 01 (describe/design); put the Christmas order-by date in the first line of the description until 16 Dec.
- Turn off ads for any listing with a cost per sale above about £15 after two weeks (Etsy Ads > listing stats); Etsy also takes its offsite-ads fee on sales it brings from Google/Meta.
- Etsy doesn't allow UTM links; Etsy sales show up as the "Etsy" channel in /admin/channels automatically."""


def check():
    errors = []
    for a, d in ANGLES.items():
        for key in ("meta_primary", "meta_headline", "pin_title", "pin_desc"):
            for t in d[key]:
                if len(t) > LIMITS[key]:
                    errors.append(f"{a} {key} ({len(t)}>{LIMITS[key]}): {t}")
    for g, d in RSA.items():
        if len(d["headlines"]) != 15 or len(d["descriptions"]) != 4:
            errors.append(f"{g}: need 15 headlines and 4 descriptions")
        if len(set(d["headlines"])) != len(d["headlines"]):
            errors.append(f"{g}: duplicate headlines")
        for t in d["headlines"]:
            if len(t) > LIMITS["rsa_headline"]:
                errors.append(f"{g} headline ({len(t)}>30): {t}")
        for t in d["descriptions"]:
            if len(t) > LIMITS["rsa_desc"]:
                errors.append(f"{g} description ({len(t)}>90): {t}")
    if errors:
        raise SystemExit("Over the limit:\n" + "\n".join(errors))


def md():
    out = ["# Mapsie ad copy", "", "Generated by `design/ads/src/ad_copy.py`, which checks every line against the platform limits "
           "(Meta primary text 125 / headline 40, Pinterest title 100 / description 500, Google RSA headline 30 / description 90). "
           "Prices and dates match the site (UK): prints from £34, framed from £69, digital £19, order by Wed 16 Dec for Christmas.", ""]
    out += ["## Meta (Instagram / Facebook)", ""]
    for a, d in ANGLES.items():
        out += [f"### {d['label']} (`{a}`)", "", "**Primary text**", ""]
        out += [f"{i + 1}. {t}  _({len(t)})_" for i, t in enumerate(d["meta_primary"])]
        out += ["", "**Headlines**", ""]
        out += [f"{i + 1}. {t}  _({len(t)})_" for i, t in enumerate(d["meta_headline"])]
        out += [""]
    out += ["## Pinterest", ""]
    for a, d in ANGLES.items():
        out += [f"### {d['label']} (`{a}`)", "", "**Titles**", ""]
        out += [f"- {t}  _({len(t)})_" for t in d["pin_title"]]
        out += ["", "**Description**", ""] + [f"> {t}  _({len(t)})_" for t in d["pin_desc"]] + [""]
    out += ["## Google Search (responsive search ads)", ""]
    for g, d in RSA.items():
        out += [f"### Ad group: {g}", "", "**Keywords** (phrase match): " + ", ".join(f'"{k}"' for k in d["keywords"]), "", f"**Final URL:** {d['url']}", "", "**Headlines (15)**", ""]
        out += [f"{i + 1}. {t}  _({len(t)})_" for i, t in enumerate(d["headlines"])]
        out += ["", "**Descriptions (4)**", ""] + [f"{i + 1}. {t}  _({len(t)})_" for i, t in enumerate(d["descriptions"])] + [""]
    out += ["## Etsy Ads", "", ETSY_NOTES, ""]
    Path("design/ads/copy.md").write_text("\n".join(out))


if __name__ == "__main__":
    check()
    md()
    print("copy.md written; all within limits")
