# Copy for the Etsy occasion listings (UK = British spelling, US = American).
# Run to check Etsy's limits: titles <= 140 chars, 13 tags of <= 20 chars.
HOW_UK = """HOW IT WORKS
1. Choose your size and finish here and check out. Please add your email address in the personalisation box so we can send you your design link.
2. Go to mapsie.shop/etsy and enter your Etsy order number and postcode. Add your stops, the route between them (plane, train, car, boat, tuk-tuk…), stickers, your own photos and a title. It takes about 5 minutes, and you see exactly how it will look before it's printed.
3. Press Send to print. We print it near you on thick 200gsm matte art paper (or frame it), and deliver it to your door.

SIZES & FINISHES
A4, A3, A2, 50 × 70 cm and A1. Unframed on matte art, cotton rag, etching or lustre paper, or framed in black, white, natural wood, brown, grey, gold or silver, with or without a white mount. A digital 300 dpi file is also available.

🎄 CHRISTMAS
Order by Wed 16 Dec and finish your design straight away for UK delivery before Christmas. Short on time? Choose the digital file and print it at home or give it as a card.

Questions? Message us any time; we're happy to help with your design."""
HOW_US = HOW_UK.replace("personalisation", "personalization").replace("postcode", "ZIP code").replace("200gsm", "heavyweight 200gsm").replace(
    "Order by Wed 16 Dec and finish your design straight away for UK delivery before Christmas.", "Order by Sat 12 Dec and finish your design straight away for US delivery before Christmas.").replace(
    "We print it near you", "We print it in the US").replace("colour", "color")

L = {
 "honeymoon": dict(
  photo="04-sri-lanka.jpg",
  uk_title="Personalised Honeymoon Map Print, Custom Travel Map of Your Honeymoon Route, Wedding Gift for Couples, Framed or Unframed",
  us_title="Personalized Honeymoon Map Print, Custom Travel Map of Your Honeymoon Route, Wedding Gift for Couples, Framed or Unframed",
  tags=["honeymoon gift","honeymoon map","wedding gift couple","custom travel map","personalised map","travel map print","newlywed gift","honeymoon print","couples gift","anniversary gift","map wall art","just married gift","destination wedding"],
  us_tags_swap={"personalised map":"personalized map"},
  intro="Turn your honeymoon into a map print you'll keep for ever. Every place you stayed, the route between them (the flight out, the train along the coast, the boat to the island), stickers of what you did and your own photos, with your names and wedding date in the title.\n\nA wedding or anniversary gift that couldn't be anyone else's: design it in about 5 minutes, and we print, frame and deliver it.",
 ),
 "roadtrip": dict(
  photo="03-route-66.jpg",
  uk_title="Custom Road Trip Map Poster, Personalised Route Map Print That Follows the Real Roads, Route 66, NC500, Campervan Gift",
  us_title="Custom Road Trip Map Poster, Personalized Route Map Print That Follows the Real Roads, Route 66, PCH, Road Trip Gift",
  tags=["road trip map","road trip gift","route 66 print","custom route map","campervan gift","road trip poster","travel map print","personalised map","map wall art","adventure gift","nc500","van life gift","custom map poster"],
  us_tags_swap={"personalised map":"personalized map","nc500":"pacific coast hwy"},
  intro="Most map prints draw a straight line between stops. Ours follows the actual roads you drove: the coast road, the mountain pass and every detour.\n\nAdd as many stops as you like, mark the car, campervan or motorbike legs, and drop in stickers for the diners, national parks and viewpoints along the way. Route 66, the Pacific Coast Highway, the NC500, the Great Ocean Road: if you drove it, you can hang it.",
 ),
 "backpacking": dict(
  photo="01-southeast-asia.jpg",
  uk_title="Personalised Backpacking Map Print, Gap Year Travel Map, Custom Map of Your Trip Around the World, Traveller Gift",
  us_title="Personalized Backpacking Map Print, Gap Year Travel Map, Custom Map of Your Trip Around the World, Traveler Gift",
  tags=["backpacking gift","gap year gift","travel map print","world travel map","backpacker gift","custom travel map","personalised map","traveller gift","travel poster","southeast asia map","map wall art","adventure map","travel memories"],
  us_tags_swap={"personalised map":"personalized map","traveller gift":"traveler gift"},
  intro="Months on the road, a dozen countries and more night buses than you'd like to remember, on one map. The flights arcing between continents, the buses, boats and trains in between, and every stop along the way.\n\nLight up the countries you visited, add stickers for the dives, temples and treks, and pin your own photos where they were taken. The souvenir that doesn't fit in a backpack.",
 ),
 "anniversary": dict(
  photo="07-your-photos.jpg",
  uk_title="Personalised Anniversary Map Gift, Custom Map of Places You've Been Together, Paper Anniversary, Gift for Him or Her",
  us_title="Personalized Anniversary Map Gift, Custom Map of Places You've Been Together, Paper Anniversary, Gift for Him or Her",
  tags=["anniversary gift","paper anniversary","map of our story","where we met map","couples map","custom map print","personalised gift","gift for her","gift for him","1st anniversary","cotton anniversary","our adventures","valentines gift"],
  us_tags_swap={"personalised gift":"personalized gift"},
  intro="Where you met, your first holiday, the city where you got engaged, the place you live now. Your story together as a map, with a stop for every chapter, a short note on each place and your own photos.\n\nPaper (1st anniversary)? Choose matte art paper. Cotton (2nd)? Choose cotton rag. Ready to hang the day it arrives.",
 ),
}

def check():
    ok = True
    for k, v in L.items():
        for t in ("uk_title", "us_title"):
            if len(v[t]) > 140: print(k, t, "TOO LONG", len(v[t])); ok = False
        for tags in (v["tags"], [v["us_tags_swap"].get(x, x) for x in v["tags"]]):
            if len(tags) != 13 or len(set(tags)) != 13: print(k, "needs 13 unique tags", len(tags)); ok = False
            for x in tags:
                if len(x) > 20: print(k, "tag too long:", x, len(x)); ok = False
    print("limits OK" if ok else "FIX ABOVE")

def markdown():
    out = ["# Etsy occasion listings\n", "Copy of the existing UK listing (4619251037) / US listing (4619377622), with new title, tags, description and first photo. Variations, prices, SKUs, personalisation and delivery profile stay as copied.\n"]
    for k, v in L.items():
        for region in ("UK", "US"):
            title = v["uk_title" if region == "UK" else "us_title"]
            tags = v["tags"] if region == "UK" else [v["us_tags_swap"].get(x, x) for x in v["tags"]]
            intro = v["intro"] if region == "UK" else v["intro"].replace("Personalised", "Personalized").replace("holiday", "vacation").replace("colour", "color")
            desc = intro + "\n\n" + (HOW_UK if region == "UK" else HOW_US)
            out += [f"\n## {k} ({region})\n", f"**First photo:** {v['photo']}\n", f"**Title:** {title}\n", f"**Tags:** {', '.join(tags)}\n", "**Description:**\n", "```", desc, "```"]
    return "\n".join(out)

if __name__ == "__main__":
    check()
    open("design/etsy/occasion-listings.md", "w").write(markdown())
