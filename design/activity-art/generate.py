"""Mapsie activity art: style exploration.

Draws three subjects (scuba diving, hot air balloon, safari) in four candidate
art styles, as plain vector SVG (200x200). Run:

    python3 design/activity-art/generate.py

Output: design/activity-art/samples/<style>/<subject>.svg
"""
from pathlib import Path

OUT = Path(__file__).parent / "samples"

# ---------------------------------------------------------------- shared shapes
ARCH = "M28 194 V96 A72 72 0 0 1 172 96 V194 Z"

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
TREE_CANOPY = "M116 124 Q138 104 166 108 Q190 111 192 124 Q160 130 116 124Z"
TREE_TOP = "M128 112 Q150 97 178 104 Q162 113 128 112Z"
TREE_TRUNK = "M152 184 L153 142 M153 142 L141 125 M153 142 L165 122"

DIVER_FISH = [(138, 52), (154, 44), (156, 62)]


def fish(x, y, s=1.0):
    """A little fish facing left at (x, y)."""
    return (f"M{x-7*s} {y} C{x-4*s} {y-4.5*s} {x+3*s} {y-4.5*s} {x+6*s} {y} "
            f"L{x+12*s} {y-4.5*s} L{x+12*s} {y+4.5*s} L{x+6*s} {y} "
            f"C{x+3*s} {y+4.5*s} {x-4*s} {y+4.5*s} {x-7*s} {y}Z")


def cloud(x, y, s=1.0):
    return (f"M{x} {y} a{8*s} {8*s} 0 0 1 {12*s} {-6*s} a{11*s} {11*s} 0 0 1 {20*s} {2*s} "
            f"a{8*s} {8*s} 0 0 1 {6*s} {14*s} H{x+2*s} a{6*s} {6*s} 0 0 1 {-2*s} {-10*s}Z")


def diver(body, accent, glass, hose, fin, stroke=None, sw=0):
    """Diver swimming left. Filled parts; if stroke is set, parts are outlined too."""
    st = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"' if stroke else ""
    limb = stroke or body
    return f"""
  <g transform="rotate(-8 100 100)">
    <path d="M84 86 Q60 78 47 99" fill="none" stroke="{hose}" stroke-width="2.6" stroke-linecap="round"/>
    <rect x="78" y="80" width="46" height="15" rx="7.5" fill="{accent}"{st}/>
    <path d="M128 97 L152 87 M130 107 L155 107" stroke="{limb}" stroke-width="{max(sw, 0) + 8}" stroke-linecap="round"/>
    {"" if not stroke else f'<path d="M128 97 L152 87 M130 107 L155 107" stroke="{body}" stroke-width="8" stroke-linecap="round"/>'}
    <ellipse cx="166" cy="81" rx="14" ry="5.5" transform="rotate(-24 166 81)" fill="{fin}"{st}/>
    <ellipse cx="169" cy="108" rx="14" ry="5.5" transform="rotate(4 169 108)" fill="{fin}"{st}/>
    <rect x="60" y="93" width="74" height="21" rx="10.5" fill="{body}"{st}/>
    <path d="M73 111 Q58 119 41 118" fill="none" stroke="{limb}" stroke-width="{max(sw, 0) + 7}" stroke-linecap="round"/>
    {"" if not stroke else f'<path d="M73 111 Q58 119 41 118" fill="none" stroke="{body}" stroke-width="7" stroke-linecap="round"/>'}
    <circle cx="54" cy="103" r="12" fill="{body}"{st}/>
    <rect x="40" y="97" width="15" height="11" rx="3.5" fill="{accent}"{st}/>
    <rect x="42.5" y="99.5" width="10" height="6" rx="2" fill="{glass}"/>
  </g>"""


def svg(inner, defs=""):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">\n<defs>{defs}</defs>{inner}\n</svg>\n'


GRAIN = """
<filter id="grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.12  0 0 0 0 0.1  0 0 0 0 0.08  0 0 0 -2.4 1.05" result="dots"/>
  <feComposite in="dots" in2="SourceGraphic" operator="in"/>
</filter>"""

# ================================================================ 1. MID-CENTURY POSTER
# Flat geometric shapes, a warm limited palette and fine grain, framed in an arch.
MC = dict(cream="#F4E9D4", teal="#1F6F78", deep="#154A52", light="#7FB7B0", mustard="#E9A23B",
          coral="#E4572E", navy="#1D2D44", sand="#E8C88E", sky="#F6D7A7")


def midcentury(subject):
    c = MC
    if subject == "scuba":
        scene = f"""
  <rect x="0" y="0" width="200" height="200" fill="{c['teal']}"/>
  <rect x="0" y="0" width="200" height="70" fill="#2E8C93"/>
  <path d="M0 70 Q25 64 50 70 T100 70 T150 70 T200 70 V82 H0Z" fill="#2A7F86"/>
  <g fill="{c['cream']}" opacity="0.1"><path d="M70 20 L96 20 L130 194 L104 194Z"/><path d="M120 20 L134 20 L170 194 L156 194Z"/></g>
  <path d="M28 168 Q60 152 92 164 T150 160 T200 162 V200 H0 V170Z" fill="{c['sand']}"/>
  <path d="M28 182 Q70 170 112 180 T200 178 V200 H0Z" fill="{c['mustard']}"/>
  <path d="M52 172 V146 M52 156 L42 142 M52 152 L63 138 M42 142 L38 134 M63 138 L68 131" stroke="{c['coral']}" stroke-width="5" stroke-linecap="round" fill="none"/>
  <path d="M150 170 Q144 158 150 148 Q156 138 150 128 M160 172 Q154 160 160 150" stroke="{c['deep']}" stroke-width="4.5" stroke-linecap="round" fill="none"/>
  {''.join(f'<path d="{fish(x, y)}" fill="{c["mustard"]}"/>' for x, y in DIVER_FISH)}
  <g fill="none" stroke="{c['cream']}" stroke-width="2"><circle cx="36" cy="84" r="3"/><circle cx="31" cy="70" r="4.5"/><circle cx="38" cy="56" r="2.5"/><circle cx="33" cy="45" r="3.5"/></g>
  {diver(c['navy'], c['mustard'], '#9ADCD6', c['coral'], c['coral'])}"""
    elif subject == "balloon":
        scene = f"""
  <rect width="200" height="200" fill="{c['sky']}"/>
  <rect y="0" width="200" height="60" fill="#F3C98B"/>
  <circle cx="138" cy="72" r="30" fill="{c['coral']}" opacity="0.9"/>
  <path d="{cloud(40, 118, 1.1)}" fill="{c['cream']}"/>
  <path d="{cloud(132, 104, 0.8)}" fill="{c['cream']}"/>
  <g transform="translate(36 52) scale(.3)"><path d="{BALLOON}" fill="{c['teal']}"/><path d="{GORE_MID}" fill="{c['cream']}"/><rect x="91" y="146" width="18" height="14" rx="2" fill="{c['navy']}"/></g>
  <path d="M0 166 Q50 140 100 158 T200 150 V200 H0Z" fill="{c['light']}"/>
  <path d="M138 178 L144 148 Q149 138 154 148 L160 178Z M160 178 L164 156 Q168 149 172 156 L176 178Z" fill="{c['sand']}"/>
  <path d="M0 184 Q60 164 120 180 T200 176 V200 H0Z" fill="{c['teal']}"/>
  <path d="{BALLOON}" fill="{c['coral']}"/>
  <path d="{GORE_L}" fill="{c['mustard']}"/><path d="{GORE_R}" fill="{c['mustard']}"/>
  <path d="{GORE_MID}" fill="{c['cream']}"/>
  <rect x="88" y="131" width="24" height="6" rx="2" fill="{c['navy']}"/>
  <path d="M90 137 L93 148 M110 137 L107 148" stroke="{c['navy']}" stroke-width="1.8"/>
  <rect x="91" y="147" width="18" height="13" rx="2" fill="#8B5A2B"/>
  <path d="M60 48 q5 -5 10 0 q5 -5 10 0" fill="none" stroke="{c['navy']}" stroke-width="2" stroke-linecap="round"/>"""
    else:  # safari
        scene = f"""
  <rect width="200" height="200" fill="#F2A541"/>
  <rect y="0" width="200" height="70" fill="#EE8F3A"/>
  <circle cx="100" cy="128" r="46" fill="{c['coral']}"/>
  <circle cx="100" cy="128" r="46" fill="none" stroke="#F6C36B" stroke-width="2" stroke-dasharray="2 6" opacity=".6"/>
  <path d="M0 176 Q100 166 200 176 V200 H0Z" fill="#B5652D"/>
  <path d="{TREE_TRUNK}" stroke="{c['navy']}" stroke-width="5" stroke-linecap="round" fill="none"/>
  <path d="{TREE_CANOPY}" fill="{c['navy']}"/><path d="{TREE_TOP}" fill="{c['navy']}"/>
  <path d="M44 144 Q36 152 38 162" stroke="{c['navy']}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <path d="{GIRAFFE}" fill="{c['navy']}"/>
  {''.join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#B5652D"/>' for x, y, rx, ry in GIRAFFE_SPOTS)}
  <path d="M0 186 Q100 178 200 186 V200 H0Z" fill="{c['navy']}"/>
  <path d="M110 186 l3 -9 l2 9 M118 186 l2 -7 l3 7 M30 187 l2 -8 l3 8" stroke="{c['navy']}" stroke-width="2" fill="none"/>"""
    return svg(f"""
<g clip-path="url(#arch)">{scene}
  <rect width="200" height="200" filter="url(#grain)" fill="#000"/>
</g>
<path d="{ARCH}" fill="none" stroke="{c['navy']}" stroke-width="5"/>""",
               f'<clipPath id="arch"><path d="{ARCH}"/></clipPath>' + GRAIN)


# ================================================================ 2. LINE + SPOT COLOUR
# One confident pen line plus a single spot colour. Prints in any theme's ink.
INK, SPOT = "#1D2D44", "#E4572E"


def monoline(subject):
    L = f'fill="none" stroke="{INK}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"'
    if subject == "scuba":
        art = f"""
  <circle cx="104" cy="104" r="70" fill="{SPOT}" opacity=".16"/>
  <path d="M22 60 Q40 52 58 60 T94 60 T130 60 T166 60 T186 58" {L}/>
  <path d="M30 172 Q54 162 76 170 M120 172 Q146 160 176 170" {L}/>
  <path d="M60 172 V150 M60 158 L52 146 M60 155 L68 143" {L}/>
  {''.join(f'<path d="{fish(x, y + 6)}" {L}/>' for x, y in DIVER_FISH)}
  <g {L}><circle cx="36" cy="88" r="3"/><circle cx="31" cy="76" r="4.5"/><circle cx="38" cy="64" r="2.5"/></g>
  <g transform="rotate(-8 100 100)" {L}>
    <path d="M84 86 Q60 78 47 99"/>
    <rect x="78" y="80" width="46" height="15" rx="7.5" fill="{SPOT}"/>
    <rect x="60" y="93" width="74" height="21" rx="10.5" fill="#fff"/>
    <path d="M128 97 L152 87 M130 107 L155 107" stroke-width="11"/>
    <path d="M128 97 L152 87 M130 107 L155 107" stroke="#fff" stroke-width="4"/>
    <ellipse cx="166" cy="81" rx="14" ry="5.5" transform="rotate(-24 166 81)" fill="{SPOT}"/>
    <ellipse cx="169" cy="108" rx="14" ry="5.5" transform="rotate(4 169 108)" fill="{SPOT}"/>
    <path d="M96 95 V112 M110 94 V111"/>
    <path d="M73 111 Q58 119 41 118" stroke-width="10"/>
    <path d="M73 111 Q58 119 41 118" stroke="#fff" stroke-width="3.5"/>
    <circle cx="54" cy="103" r="12" fill="#fff"/>
    <rect x="40" y="97" width="15" height="11" rx="3.5" fill="#fff"/>
    <path d="M44 103 H51"/>
  </g>"""
    elif subject == "balloon":
        art = f"""
  <circle cx="100" cy="92" r="70" fill="{SPOT}" opacity=".16"/>
  <circle cx="150" cy="48" r="13" fill="{SPOT}"/>
  <path d="{cloud(26, 122, 1.0)}" {L}/>
  <path d="{cloud(142, 112, 0.75)}" {L}/>
  <path d="{BALLOON}" {L} fill="#fff"/>
  <path d="{GORE_MID}" fill="{SPOT}" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>
  <path d="M100 34 C74 44 64 94 86 132 M100 34 C126 44 136 94 114 132" {L}/>
  <path d="M88 132 H112 M90 133 L93 148 M110 133 L107 148" {L}/>
  <rect x="91" y="148" width="18" height="13" rx="2.5" {L} fill="#fff"/>
  <path d="M95 154 H105" {L}/>
  <path d="M28 182 Q70 166 104 178 T184 172" {L}/>
  <path d="M40 64 q5 -5 10 0 q5 -5 10 0" {L}/>"""
    else:
        art = f"""
  <circle cx="104" cy="118" r="44" fill="{SPOT}"/>
  <path d="{TREE_TRUNK}" {L}/>
  <path d="{TREE_CANOPY}" {L} fill="#fff"/><path d="{TREE_TOP}" {L} fill="#fff"/>
  <path d="M44 144 Q36 152 38 162" {L}/>
  <path d="{GIRAFFE}" {L} fill="#fff"/>
  {''.join(f'<ellipse cx="{x}" cy="{y}" rx="{rx*0.8}" ry="{ry*0.8}" fill="{INK}"/>' for x, y, rx, ry in GIRAFFE_SPOTS)}
  <path d="M18 186 Q100 176 186 186" {L}/>
  <path d="M120 186 l3 -9 l2 9 M128 186 l2 -7 l3 7 M24 187 l2 -8 l3 8" {L}/>"""
    return svg(art)


# ================================================================ 3. ADVENTURE BADGE
# National-park style patch: scene in a circle, title round the rim.
BG = dict(navy="#22333B", cream="#F2E8CF", forest="#2F5D50", rust="#C8553D", gold="#E0A458", sky="#A9CBB7", sand="#E7D7B1")
TITLES = {"scuba": "SCUBA DIVING", "balloon": "HOT AIR BALLOON", "safari": "ON SAFARI"}


def badge(subject):
    c = BG
    if subject == "scuba":
        scene = f"""
  <rect width="200" height="200" fill="#3E7C7A"/>
  <rect width="200" height="70" fill="#5C9A92"/>
  <path d="M0 70 Q25 64 50 70 T100 70 T150 70 T200 70 V80 H0Z" fill="#4F8D86"/>
  <path d="M0 166 Q60 152 100 164 T200 160 V200 H0Z" fill="{c['sand']}"/>
  <path d="M52 172 V148 M52 158 L43 145 M52 154 L62 141" stroke="{c['rust']}" stroke-width="5" stroke-linecap="round" fill="none"/>
  {''.join(f'<path d="{fish(x, y)}" fill="{c["gold"]}"/>' for x, y in DIVER_FISH)}
  <g fill="none" stroke="{c['cream']}" stroke-width="2"><circle cx="36" cy="84" r="3"/><circle cx="31" cy="70" r="4.5"/><circle cx="38" cy="56" r="2.5"/></g>
  {diver(c['navy'], c['gold'], '#CFE7DF', c['rust'], c['rust'])}"""
    elif subject == "balloon":
        scene = f"""
  <rect width="200" height="200" fill="{c['sky']}"/>
  <circle cx="140" cy="70" r="26" fill="{c['gold']}"/>
  <path d="{cloud(34, 116, 1.0)}" fill="{c['cream']}"/>
  <path d="M0 162 L40 128 L70 150 L104 116 L150 158 L176 140 L200 160 V200 H0Z" fill="{c['forest']}"/>
  <path d="M104 116 L116 127 L108 126 L102 131 L94 125Z M40 128 L48 135 L38 135Z" fill="{c['cream']}"/>
  <path d="M0 178 Q60 164 120 176 T200 172 V200 H0Z" fill="{c['navy']}"/>
  <path d="{BALLOON}" fill="{c['rust']}"/><path d="{GORE_L}" fill="{c['gold']}"/><path d="{GORE_R}" fill="{c['gold']}"/><path d="{GORE_MID}" fill="{c['cream']}"/>
  <rect x="88" y="131" width="24" height="6" rx="2" fill="{c['navy']}"/>
  <path d="M90 137 L93 148 M110 137 L107 148" stroke="{c['navy']}" stroke-width="1.8"/>
  <rect x="91" y="147" width="18" height="13" rx="2" fill="{c['navy']}"/>"""
    else:
        scene = f"""
  <rect width="200" height="200" fill="{c['gold']}"/>
  <circle cx="100" cy="126" r="44" fill="{c['cream']}" opacity=".85"/>
  <path d="M0 178 Q100 168 200 178 V200 H0Z" fill="{c['rust']}"/>
  <path d="{TREE_TRUNK}" stroke="{c['navy']}" stroke-width="5" stroke-linecap="round" fill="none"/>
  <path d="{TREE_CANOPY}" fill="{c['navy']}"/><path d="{TREE_TOP}" fill="{c['navy']}"/>
  <path d="M44 144 Q36 152 38 162" stroke="{c['navy']}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <path d="{GIRAFFE}" fill="{c['navy']}"/>
  {''.join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{c["gold"]}"/>' for x, y, rx, ry in GIRAFFE_SPOTS)}
  <path d="M0 188 Q100 180 200 188 V200 H0Z" fill="{c['navy']}"/>"""
    title = TITLES[subject]
    star = "M0 -5 L1.5 -1.5 L5 -1.5 L2.2 0.8 L3.2 4.5 L0 2.3 L-3.2 4.5 L-2.2 0.8 L-5 -1.5 L-1.5 -1.5Z"
    return svg(f"""
<circle cx="100" cy="100" r="96" fill="{c['navy']}"/>
<circle cx="100" cy="100" r="89" fill="none" stroke="{c['cream']}" stroke-width="1.6" stroke-dasharray="3 3"/>
<g clip-path="url(#disc)"><g transform="translate(100 108) scale(.6) translate(-100 -112)">{scene}</g></g>
<circle cx="100" cy="104" r="64" fill="none" stroke="{c['cream']}" stroke-width="3"/>
<text font-family="'Arial Black','Helvetica Neue',Arial,sans-serif" font-weight="900" font-size="15" letter-spacing="2.5" fill="{c['cream']}" text-anchor="middle">
  <textPath href="#rim" startOffset="50%">{title}</textPath></text>
<g fill="{c['gold']}"><path d="{star}" transform="translate(27 118)"/><path d="{star}" transform="translate(173 118)"/></g>
<text x="100" y="181" font-family="'Arial Black',Arial,sans-serif" font-weight="900" font-size="8" letter-spacing="2" fill="{c['gold']}" text-anchor="middle">★ MAPSIE ★</text>""",
               f'<clipPath id="disc"><circle cx="100" cy="104" r="64"/></clipPath>'
               f'<path id="rim" d="M22 104 A78 78 0 0 1 178 104"/>')


# ================================================================ 4. PAPERCUT
# Layered paper with soft shadows between layers; feels tactile and premium.
def papercut(subject):
    sh = 'filter="url(#paper)"'
    if subject == "scuba":
        blues = ["#CDEFF2", "#9ADBE0", "#5FBCC6", "#358FA3", "#1F6582", "#143F5C"]
        bands = "".join(
            f'<path {sh} d="M0 {40 + i*24} Q30 {32 + i*24} 60 {40 + i*24} T120 {40 + i*24} T180 {40 + i*24} T240 {40 + i*24} V220 H0Z" fill="{b}"/>'
            for i, b in enumerate(blues))
        art = f"""
<g clip-path="url(#round)">
  <rect width="200" height="200" fill="#E8F8F8"/>
  {bands}
  <path {sh} d="M0 170 Q40 156 80 168 T160 164 T220 166 V220 H0Z" fill="#F2D49B"/>
  <path {sh} d="M48 172 V146 M48 156 L38 142 M48 152 L59 138" stroke="#FF7A5C" stroke-width="6" stroke-linecap="round" fill="none"/>
  <g {sh}>{''.join(f'<path d="{fish(x, y)}" fill="#FFC857"/>' for x, y in DIVER_FISH)}</g>
  <g {sh}>{diver('#0E2A3D', '#FFC857', '#BFF0EE', '#FF7A5C', '#FF7A5C')}</g>
  <g fill="#fff" opacity=".85"><circle cx="36" cy="84" r="3"/><circle cx="31" cy="70" r="4.5"/><circle cx="38" cy="56" r="2.5"/></g>
</g>"""
    elif subject == "balloon":
        art = f"""
<g clip-path="url(#round)">
  <rect width="200" height="200" fill="#FFE8D1"/>
  <circle {sh} cx="146" cy="64" r="26" fill="#FFB86B"/>
  <path {sh} d="{cloud(24, 98, 1.3)}" fill="#fff"/>
  <path {sh} d="{cloud(138, 112, 0.9)}" fill="#fff"/>
  <path {sh} d="M0 150 Q50 120 100 142 T200 132 V220 H0Z" fill="#F6B89A"/>
  <path {sh} d="M0 166 Q60 144 120 160 T200 154 V220 H0Z" fill="#E98A6C"/>
  <path {sh} d="M0 182 Q70 164 130 178 T200 172 V220 H0Z" fill="#B85C4A"/>
  <g {sh}><path d="{BALLOON}" fill="#3E7CB1"/><path d="{GORE_L}" fill="#FFD166"/><path d="{GORE_R}" fill="#FFD166"/><path d="{GORE_MID}" fill="#EF476F"/></g>
  <path d="M90 136 L93 148 M110 136 L107 148" stroke="#5A3E36" stroke-width="1.8"/>
  <rect {sh} x="91" y="147" width="18" height="13" rx="2" fill="#8B5A2B"/>
</g>"""
    else:
        art = f"""
<g clip-path="url(#round)">
  <rect width="200" height="200" fill="#FDE2D4"/>
  <circle {sh} cx="100" cy="118" r="50" fill="#F9B9A0"/>
  <circle {sh} cx="100" cy="118" r="34" fill="#F48C7F"/>
  <path {sh} d="M0 160 Q60 146 120 156 T200 150 V220 H0Z" fill="#E9B872"/>
  <g {sh}><path d="{TREE_TRUNK}" stroke="#3B2A20" stroke-width="5" stroke-linecap="round" fill="none"/><path d="{TREE_CANOPY}" fill="#4F6D3A"/><path d="{TREE_TOP}" fill="#6B8F4E"/></g>
  <g {sh}><path d="M44 144 Q36 152 38 162" stroke="#3B2A20" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <path d="{GIRAFFE}" fill="#F6C453"/>
  {''.join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#A0522D"/>' for x, y, rx, ry in GIRAFFE_SPOTS)}</g>
  <path {sh} d="M0 180 Q100 168 200 180 V220 H0Z" fill="#C98B4B"/>
  <path {sh} d="M0 190 Q100 184 200 190 V220 H0Z" fill="#8C5A2B"/>
</g>"""
    return svg(art + '<circle cx="100" cy="100" r="92" fill="none" stroke="#fff" stroke-width="4" opacity=".9"/>',
               '<clipPath id="round"><circle cx="100" cy="100" r="92"/></clipPath>'
               '<filter id="paper" x="-20%" y="-20%" width="140%" height="140%">'
               '<feDropShadow dx="0" dy="2.2" stdDeviation="2" flood-color="#3a2a1a" flood-opacity=".35"/></filter>')


STYLES = {"midcentury": midcentury, "line": monoline, "badge": badge, "papercut": papercut}
SUBJECTS = ["scuba", "balloon", "safari"]

if __name__ == "__main__":
    for name, fn in STYLES.items():
        d = OUT / name
        d.mkdir(parents=True, exist_ok=True)
        for s in SUBJECTS:
            (d / f"{s}.svg").write_text(fn(s))
    print("wrote", len(STYLES) * len(SUBJECTS), "svgs to", OUT)
