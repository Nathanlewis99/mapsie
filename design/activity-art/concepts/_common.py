"""Shared shapes and helpers for concept modules. Import from here; don't edit it from a batch."""
from artkit import Concept, Drawing, cloud, fish, circle, ellipse, waves, hills  # noqa: F401 (re-exported)

BALLOON = "M100 34 C132 34 148 58 148 82 C148 106 124 120 112 132 L88 132 C76 120 52 106 52 82 C52 58 68 34 100 34Z"
GORE_MID = "M100 34 C86 56 84 104 92 132 L108 132 C116 104 114 56 100 34Z"
GORE_L = "M100 34 C74 44 64 94 80 125 L86 130 C76 104 80 58 100 34Z"
GORE_R = "M100 34 C126 44 136 94 120 125 L114 130 C124 104 120 58 100 34Z"
GIRAFFE = (
    "M48 142 C60 136 76 134 88 136 L104 82 L103 72 L106.5 72 L107.5 79 L110 73 L113 73 L112 80 "
    "L119 82 C126 84 127 89 122 91 L112 91 L101 110 L95 141 C95 146 94 150 92 152 "
    "L92 184 L87 184 L86.5 158 L81 158 L80 184 L75 184 L74.5 157 L60 157 "
    "L59 184 L54 184 L53.5 156 L48 155 L47 184 L42 184 L42 149 C42 146 44 143.5 48 142Z"
)
GIRAFFE_SPOTS = [(56, 146, 5, 3.5), (68, 142, 4.5, 3.5), (80, 145, 4.5, 3.5), (63, 150, 3.5, 2.5),
                 (90, 128, 3, 4), (94, 112, 2.8, 3.5), (98, 98, 2.4, 3)]
ACACIA_CANOPY = "M116 124 Q138 104 166 108 Q190 111 192 124 Q160 130 116 124Z"
ACACIA_TOP = "M128 112 Q150 97 178 104 Q162 113 128 112Z"
ACACIA_TRUNK = "M152 184 L153 142 M153 142 L141 125 M153 142 L165 122"


def rrect(x, y, w, h, r):
    return (f"M{x+r} {y} H{x+w-r} A{r} {r} 0 0 1 {x+w} {y+r} V{y+h-r} A{r} {r} 0 0 1 {x+w-r} {y+h} "
            f"H{x+r} A{r} {r} 0 0 1 {x} {y+h-r} V{y+r} A{r} {r} 0 0 1 {x+r} {y}Z")


def group(d: Drawing, transform: str, fn):
    d.raw(f'<g transform="{transform}">', f'<g transform="{transform}">')
    fn()
    d.raw("</g>", "</g>")


def balloon(d: Drawing, body="hero", stripes="hero2", centre="pop", basket="dark"):
    d.shape(body, BALLOON)
    d.shape(stripes, GORE_L, shadow=False, spot=True)
    d.shape(stripes, GORE_R, shadow=False, spot=True)
    d.shape(centre, GORE_MID, shadow=False)
    d.stroke(basket, "M90 133 L93 148 M110 133 L107 148", 1.8)
    d.shape(basket, rrect(88, 130, 24, 5, 2), shadow=False)
    d.shape(basket, rrect(91, 147, 18, 13, 2.5))


def bubbles(d: Drawing, pts):
    for x, y, r in pts:
        d.stroke("light", circle(x, y, r), 2)


def water(d: Drawing, bottom=True):
    d.band("sky2", waves(40, 5, 26))
    d.band("far", waves(64, 5, 28))
    d.band("mid", waves(90, 6, 30))
    d.band("near", waves(120, 6, 34))
    d.band("deep", waves(148, 5, 36), line=False)
    if bottom:
        d.band("ground", "M-30 172 Q40 158 80 170 T160 166 T230 168")


def acacia(d: Drawing, tx=0, ty=0, s=1.0):
    def draw():
        d.limb("dark", ACACIA_TRUNK, 5)
        d.shape("dark", ACACIA_CANOPY)
        d.shape("dark", ACACIA_TOP, shadow=False)
    group(d, f"translate({tx} {ty}) scale({s})", draw)
