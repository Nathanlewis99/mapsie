import { NextResponse } from "next/server";
import { FRAMES, GLAZES, MOUNTS, PAPERS, PRODUCTS, prodigiItem } from "@/lib/products";
import { prodigiBase } from "@/lib/server/prodigi";

// Admin tool: checks every size / paper / frame / mount / glazing combination we
// sell against Prodigi's live catalogue, so a wrong SKU or attribute shows up
// here rather than as a failed customer order.
export async function GET() {
  const key = process.env.PRODIGI_API_KEY;
  if (!key) return NextResponse.json({ error: "PRODIGI_API_KEY is not set" }, { status: 400 });

  const catalogue = new Map<string, { ok: boolean; status: number; attributes?: Record<string, string[]>; printAreas?: unknown }>();
  const lookup = async (sku: string) => {
    if (!catalogue.has(sku)) {
      const r = await fetch(`${prodigiBase}/products/${sku}`, { headers: { "X-API-Key": key } });
      const j = r.ok ? await r.json() : null;
      catalogue.set(sku, { ok: r.ok, status: r.status, attributes: j?.product?.attributes, printAreas: j?.product?.variants?.[0]?.printAreaSizes });
    }
    return catalogue.get(sku)!;
  };

  const problems: string[] = [];
  let checked = 0;
  for (const p of PRODUCTS) {
    const combos = [
      ...PAPERS.map((paper) => ({ productId: p.id, frame: "none" as const, paper: paper.id })),
      ...FRAMES.filter((f) => f.id !== "none").flatMap((f) => MOUNTS.flatMap((m) => GLAZES.map((g) => ({ productId: p.id, frame: f.id, mount: m.id, glaze: g.id })))),
    ];
    for (const c of combos) {
      checked++;
      const item = prodigiItem(c);
      const info = await lookup(item.sku);
      if (!info.ok) {
        problems.push(`${item.sku}: not found (${info.status})`);
        continue;
      }
      for (const [name, val] of Object.entries(item.attributes)) {
        const allowed = info.attributes?.[name];
        if (!allowed) problems.push(`${item.sku}: no attribute "${name}" (has ${Object.keys(info.attributes ?? {}).join(", ") || "none"})`);
        else if (!allowed.some((a) => a.toLowerCase() === val.toLowerCase())) problems.push(`${item.sku}: ${name}="${val}" not in [${allowed.join(", ")}]`);
      }
    }
  }
  return NextResponse.json({
    environment: prodigiBase.includes("sandbox") ? "sandbox" : "live",
    combinationsChecked: checked,
    problems: [...new Set(problems)],
    catalogue: Object.fromEntries(catalogue),
  });
}
