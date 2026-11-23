---
name: mapsie-reel
description: Make a Mapsie route-drawing Reel (or video ad) from a saved design, write and check its caption, and queue it for Instagram and Facebook. Use when asked for new Reels, TikToks, video ads or social posts about a trip, a map style or a feature.
---

# Mapsie Reel, start to finish

The Reel shows a real Mapsie poster: the route draws itself stop by stop, then the finished poster appears, then it's shown framed in a room, then the end card. It's 1080×1920, 15 s and 30 fps, with text kept inside Instagram's safe area.

## 1. Pick the trip and the hook

- **The design:** a JSON file in `design/mockups/designs/`. To make a new one, build it in the designer and save it, or add a trip to `design/mockups/trips.ts`.
- **The room photo:** it goes in `design/video/public/rooms/<slug>.jpg` at 1080×1350. Reuse one from `design/ads/vintage/*-room.jpg` or `public/social/*.jpg`.
- **The hook:** write 4–6 options with the **ig-reel** skill, then score them and keep the best:
  `python3 .claude/skills/ig-reel/hookscore.py --hook "…"`
  A score of 50+ is fine and 60+ is good; it usually improves by adding a specific number or naming who it's for.

## 2. Capture the map

With the site running locally (see the root README; `DATA_DIR` and `PORT=3123`), run:

```
SESSION_SECRET=x DATA_DIR=… PORT=3123 npx -y tsx@4.20.3 design/video/capture.ts <slug>
```

This writes `design/video/public/maps/<slug>-base.png`, `-full.png` and `.json`. Convert the PNGs to JPEG at quality 90 to keep the repo small.

## 3. Add it and check it

- Add an entry to `design/video/src/reels.ts`. Copy the design's `theme.colors.accent` and `route.width` so the drawn line matches the poster.
- Render stills at frames 20, 150, 290, 340 and 420:
  ```
  cd design/video && REMOTION_CHROME=<headless shell> npx remotion still <Id> out/x.png --frame=150
  ```
  The headless shell is at `/opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell` in the cloud container.
- Check that nothing important sits in the top 14% or the bottom 35% of the frame, where Instagram puts its buttons.
- Render the video: `npx remotion render <Id> out/<Id>.mp4 --concurrency=4 --crf=20`. It takes about 20 seconds.

Sound is built in: `design/video/sound.py` makes our own music bed, stop "pops" and the reveal whoosh (no samples, so no licensing). Instagram's API can't add in-app music, so Reels go out with this track. Re-run it to change the music.

## 4. Caption

- Write it with the **ig-caption** skill: a concrete first line, one ask ("link in bio"), and three hashtags placed after the text.
- Run both checks and fix anything they flag:
  - `python3 .claude/skills/ig-caption/caption.py cap.txt --keywords "map,road trip,print"` should say READY.
  - `python3 .claude/skills/ig-human/detect.py cap.txt` should score 80 or more.

## 5. Queue it, never post it without approval

- Copy the video to `public/social/reel-<name>.mp4` and its cover (a still at frame 290) to `public/social/cover-<name>.jpg`.
- Add the post to `scripts/social/posts.json` with `"draft": true`.
- Show the owner the video and the caption. Only after they approve: remove `"draft"`, deploy, and schedule the post with `send_later`, running:
  `python3 scripts/social/instagram.py N N 0` then `python3 scripts/social/facebook.py N N 0`
- The posting scripts run `scripts/social/check.py` first. They refuse drafts and captions that fail the checks.

## For ads

- Render a second version with a different hook as its own entry (e.g. `NC500Ad`), and keep it in `design/ads/reels/`.
- Uploading the video to the Meta ad account's media library is fine. Creating or changing ads needs the owner's go-ahead. The ChattyPatty app is in development mode, so a worker builds new ads in Ads Manager.
- Use the **mkt-ad-creative** skill for primary text and headlines.
