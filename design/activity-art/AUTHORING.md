# Drawing Mapsie Originals

Mapsie Originals are the activity stickers customers put on their travel map
prints (posters up to A1). Every drawing is written as code once and renders in
two styles and several palettes automatically:

- **Papercut**: layered paper with soft drop shadows, in a circle. Five palettes.
- **Line**: one pen line plus a single spot colour. Four colourways.

Read `artkit.py` (the drawing API) and `concepts/pilot.py` (nine finished
concepts that set the quality bar) before you start. Shared shapes and helpers
are in `concepts/_common.py`: import from it, don't edit it.

## What to make

For each activity you're given, draw **three different concepts**. Make the three
genuinely different ideas, mixing these kinds of subject:

- an **animal or creature** (shark, turtle, horse, penguin)
- a **vehicle or object** (jeep, kayak, surfboard, ramen bowl, camera)
- a **landscape or landmark** (balloons over the Himalayas, Mount Fuji, a temple)
- a **close-up** of the most iconic detail (the balloon's flame, a ski boot in a binding, a ticket)
- a **person doing it**, only where it's the clearest way to show the activity. Keep people simple and
  readable (see the pilot diver). People in motion are the hardest thing to draw well; prefer a
  strong object or scene where one exists.

Example, safari: giraffe at sunset / safari jeep / elephant. Hot air balloon: valley sunrise /
over the Himalayas / big flame close-up.

## Canvas and composition

- 200 × 200 viewBox. Papercut shows a circle of radius 92 centred at (100, 100); keep the subject
  inside a radius of about 80. Background bands should run edge to edge (x from -30 to 230).
- One clear subject, big enough to read at sticker size (about 4 cm on a poster). Few, bold shapes
  beat lots of small detail. 3 to 6 layers is typical.
- Build back to front: sky (automatic) → sun/moon `disc` → distant `band`s → mid layers → subject →
  foreground band.
- The papercut look comes from layering: every `shape`/`band`/`disc` gets a soft shadow unless you
  pass `shadow=False` (use that for flat details sitting on a shape, like windows or stripes).

## Colour roles (never hex values)

`sky, sky2, glow, glow2, far, mid, near, deep, ground, hero, hero2, mark, dark, light, pop`.
See the comment in `artkit.py` for what each means. The subject is usually `hero`, with `hero2` for
its secondary colour, `mark` for markings, `dark` for silhouettes and wheels, `light` for highlights.

- `overrides={...}`: natural colours that shouldn't change with the palette (golden giraffe, grey
  elephant, green turtle). Use sparingly. Hex values are fine here.
- `palettes=[...]`: limit to palettes that suit the scene. Underwater scenes use
  `["coastal", "dusk", "meadow"]`; most others can use all five.
- `checks=[("hero", "glow"), ...]`: pairs of roles that touch. A palette is only offered if each pair
  reads apart. Always check the subject against whatever is directly behind it.
- `fixes={"glow": ["#E07A5F", "near"]}`: if a check fails, try these replacements (palette roles or
  hex) in order. This is how the giraffe gets a terracotta sun instead of vanishing into an orange one.
- Every concept must end up with **at least 2** papercut palettes. The build flags any that don't.

## Line style

The same drawing renders as line art automatically: shapes become paper-filled outlines, `band`s
become single lines, `disc`s become solid spot colour. To make it look good:

- Mark one to three accent parts with `spot=True` (a tank, fins, stripes). That's the spot colour.
- Use `limb()` for arms, legs, poles and trunks: outlined tubes in line style.
- `marks()` (spots, eyes) render as solid ink.
- `d.raw(papercut_svg, line_svg)` exists for effects that only make sense in one style (light rays).
- Check the line versions in the preview. Overlapping shapes can get busy; drop minor background
  layers from line style with `line=False`.

## Animals

Activities in the "Animals" category (ids start with `animal-`) get **two** concepts, not three:

1. **Portrait**: the animal big and bold, filling the circle, with its most recognisable features
   exaggerated (the sloth bear's shaggy coat and pale snout, the shoebill's huge bill, the platypus's
   bill and flat tail). Side-on or front-on, whichever reads instantly.
2. **In its habitat**: the animal in a scene that says where tourists see it (grizzly catching a salmon
   at a waterfall, polar bear on an ice floe, leopard draped on a branch at Yala, puffin on a cliff).

Use `overrides` for natural colours (a lion is tawny in every palette) and `checks`/`fixes` so the
animal never blends into the sun or ground. Silhouette accuracy matters most: get the proportions,
ears, tails, horns and posture right. Look at the pilot giraffe and elephant and the finished
`concepts/wildlife.py` for the quality bar.

## Lessons from the first round

- **Ids must be unique across all modules.** Prefix every concept id with your activity's short name
  (`slothbear-portrait`, `onsen-bucket`). The build now flags ids already used by another module.
- **Sea and lake scenes:** leave `"golden"` out of `palettes`: its water reads as brown desert.
- The kit now clips line style to the circle and gives straight strokes a working shadow, so you
  don't need workarounds for either. Shapes inside `group()` transforms are fine too.
- Don't pass `fill`, `stroke` or `filter` through `extra=`: it duplicates attributes and makes invalid
  SVG. The build checks every file and flags this.
- Every concept needs **at least 2** papercut palettes after the clash check.
- Use your own file names for temporary files (`/tmp/<your_module>-*`). Other illustrators share
  the machine.
- Reuse helpers from finished modules by copying them into yours (don't import from another batch).

## Workflow

1. Write your module: `design/activity-art/concepts/<your_module>.py`, exporting `CONCEPTS`
   (a list of `Concept`). Concept ids: `<activity-short>-<idea>`, e.g. `surf-board-wave`, unique and
   lowercase. `activity` must be the exact id from `activities.json`.
2. Build it: `python3 design/activity-art/build.py <your_module>`
3. Look at it:
   - `node design/activity-art/preview.js <your_module> /tmp/<your_module>.png --big` (detail)
   - `node design/activity-art/preview.js <your_module> /tmp/<your_module>-all.png` (all palettes + line)
   - Open the PNGs with the Read tool and **actually look**. Is the subject instantly recognisable?
     Anything floating, misaligned, cut off by the circle, or the wrong way round? Does any palette
     clash? Does the line version read?
4. Fix and repeat until every concept would sit happily next to the pilot ones.

Only create or edit your own module file. Don't edit `artkit.py`, `_common.py`, `build.py`, other
modules, or anything outside `design/activity-art/concepts/`. Don't commit; the lead will.
