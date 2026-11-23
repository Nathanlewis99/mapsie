"""Build public/geo/admin1.json for the overview map: state/province outlines with label points
(Natural Earth 1:50m admin-1, which covers the big federal countries, plus the UK's four nations
from the 1:50m map units) and country label points. Natural Earth is public domain.

  python3 scripts/build/admin1.py <dir with ne_50m_admin_1_states_provinces.geojson,
                                   ne_50m_admin_0_map_units.geojson, ne_50m_admin_0_countries.geojson>
"""
import json, sys, math

src = sys.argv[1]
def load(name):
    return json.load(open(f"{src}/{name}.geojson"))

def simplify(ring, tol=0.03):
    out = []
    for x, y in ring:
        p = [round(x, 2), round(y, 2)]
        if out and abs(p[0] - out[-1][0]) < tol and abs(p[1] - out[-1][1]) < tol:
            continue
        out.append(p)
    return out if len(out) >= 4 else None

def geom(g):
    polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
    out = []
    for poly in polys:
        rings = [r for r in (simplify(r) for r in poly) if r]
        if rings:
            out.append(rings)
    return out

def bbox_centre(polys):
    xs = [p[0] for poly in polys for p in poly[0]]
    ys = [p[1] for poly in polys for p in poly[0]]
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2

regions = []
for f in load("ne_50m_admin_1_states_provinces")["features"]:
    p = f["properties"]
    g = geom(f["geometry"])
    if not g:
        continue
    x, y = (p.get("longitude"), p.get("latitude")) if p.get("longitude") is not None else bbox_centre(g)
    regions.append({"n": p["name"], "c": p.get("admin"), "x": round(x, 2), "y": round(y, 2), "a": round(p.get("area_sqkm") or 0), "g": g})

for f in load("ne_50m_admin_0_map_units")["features"]:
    p = f["properties"]
    if p.get("ADM0_A3") != "GBR":
        continue
    g = geom(f["geometry"])
    names = {"N. Ireland": "Northern Ireland"}
    regions.append({"n": names.get(p["NAME"], p["NAME"]), "c": "United Kingdom", "x": round(p["LABEL_X"], 2), "y": round(p["LABEL_Y"], 2), "a": 0, "g": g})

countries = []
for f in load("ne_50m_admin_0_countries")["features"]:
    p = f["properties"]
    countries.append({"n": p["NAME"], "x": round(p["LABEL_X"], 2), "y": round(p["LABEL_Y"], 2), "r": p.get("LABELRANK", 5)})

json.dump({"regions": regions, "countries": countries}, open("public/geo/admin1.json", "w"), separators=(",", ":"))
print(len(regions), "regions,", len(countries), "countries")
