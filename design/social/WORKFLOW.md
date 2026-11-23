# Social and marketing workflow (with the project's Claude skills)

The skills live in `.claude/skills` and load automatically in Claude Code sessions in this repo. Each skill folder keeps its source's licence; sources are listed at the end.

## The quick way

Ask for "a new Reel about …" and the **mapsie-reel** skill runs the whole recipe:
- capture a real design;
- animate the route with Remotion (`design/video`);
- score the hooks;
- write and check the caption;
- queue it as a draft for approval.

`scripts/social/check.py` runs the caption and human-sounding checks automatically before anything is posted, and drafts can't be posted.

## A Reel or post, start to finish

1. **Plan:** `/ig-plan` builds a week of posts around what's selling (vintage styles, gift cards, Christmas dates). `/mkt-marketing-ideas` helps when we're stuck.
2. **Hook and script:**
   - `/ig-reel` writes the beats and scores the opening line. To check a hook on its own: `python3 .claude/skills/ig-reel/hookscore.py --hook "…"`.
   - `/ig-carousel` and `/ig-story` cover the other formats.
3. **Make the video:**
   - Today, Reels are built with `design/mockups/compose.py` and the ad graphics script (`design/ads/src/graphics.ts`).
   - For new animated pieces, the Remotion skills apply: `/remotion-create`, `/remotion-best-practices`, `/remotion-captions` and `/remotion-render`. `/remotion-maps` covers animated routes and flight paths, which suits Mapsie.
   - `/remocn` and `/remocn-add` provide ready-made animated pieces (text reveals, lower thirds and the like).
   - Remotion is free for individuals and companies of up to 3 people; see `/remotion-license`.
4. **Caption:**
   - `/ig-caption` writes the caption, and its script checks length, hashtags and line breaks.
   - `/ig-human` removes AI-sounding phrasing, both from captions and from replies.
5. **Post:** `scripts/social/instagram.py` and `scripts/social/facebook.py` (posts are in `scripts/social/posts.json`; media goes in `public/social`). Scheduled posts use scheduled tasks. We only post once the owner has approved the post.
6. **Engage:** `/ig-comment`, `/ig-reply` and `/ig-dm` draft responses for approval. Nothing is sent automatically.
7. **Review:** `/ig-audit` and `/ig-profile` check the profile and recent posts; `/ig-viral` breaks down posts that did well elsewhere.

## Ads, website and partners

- **Ads:** `/mkt-ad-creative` writes ad copy and variations for Meta, Pinterest and Google; `/mkt-marketing-psychology` explains why an angle works.
- **Website:** `/mkt-cro` and `/mkt-copywriting` cover landing pages and the designer's start screen; `/mkt-copy-editing` polishes text.
- **SEO:** `/mkt-programmatic-seo` covers occasion and trip pages; `/mkt-ai-seo` covers being recommended by AI assistants.
- **Partners and referrals:** `/mkt-co-marketing` and `/mkt-referrals` support the partner programme and a future "give £5, get £5" scheme.

## Sources

| Skills | Source | Licence |
|---|---|---|
| `ig-*` | github.com/Jakeschincariol/instagram-agent-skill | MIT |
| `mkt-*` (a selection) | github.com/coreyhaines31/marketingskills | MIT |
| `remotion-*` | github.com/remotion-dev/skills | Published by Remotion for use in projects; Remotion itself has its own licence |
| `remocn*` | github.com/Remocn/remocn | MIT |

To update a set, download the repo again into a scratch folder, read what changed, then copy over the same folders.
