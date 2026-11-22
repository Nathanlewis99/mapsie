import { NextResponse } from "next/server";
import { nanoid } from "nanoid";
import { searchPlaces } from "@/lib/server/geocode";
import { createPartnerCode, getPartner, invoiceTradeBatch, issueTradeCodes, savePartner } from "@/lib/server/partners";
import { logError } from "@/lib/server/log";
import { publicUrl } from "@/lib/server/urls";
import { PARTNER_KINDS, parseStopList, slugify, type Partner, type PartnerKind, type PartnerTrip } from "@/lib/partners";
import { PRESETS } from "@/lib/themes";
import { REGIONS, type RegionId } from "@/lib/products";

// Admin only (middleware). One form endpoint for the partner pages: `do` says what to change.
export async function POST(req: Request) {
  const f = await req.formData();
  const get = (k: string, max = 200) => String(f.get(k) ?? "").trim().slice(0, max);
  const num = (k: string) => Number(get(k));
  const back = (id?: string, msg?: string) =>
    NextResponse.redirect(`${publicUrl()}/admin/partners${id ? `?p=${id}` : ""}${msg ? `${id ? "&" : "?"}msg=${encodeURIComponent(msg)}` : ""}`, { status: 303 });
  const action = get("do");
  try {
    if (action === "save") {
      const id = get("id") ? get("id") : slugify(get("name"));
      const existing = await getPartner(id);
      const kind = (PARTNER_KINDS.some((k) => k.id === get("kind")) ? get("kind") : "travel") as PartnerKind;
      const region = REGIONS.some((r) => r.id === get("region")) ? (get("region") as RegionId) : undefined;
      const commissionPct = Math.min(50, Math.max(0, num("commissionPct") || 0));
      const p: Partner = {
        ...(existing ?? { trips: [], payouts: [], createdAt: new Date().toISOString() }),
        id,
        name: get("name", 80) || existing?.name || id,
        kind,
        active: f.get("active") === "on",
        contactEmail: get("contactEmail", 120) || undefined,
        welcome: get("welcome", 160) || undefined,
        commissionPct,
        region,
        notes: get("notes", 2000) || undefined,
      };
      await savePartner(p);
      return back(p.id, existing ? "Saved" : "Partner added");
    }

    const p = await getPartner(get("id"));
    if (!p) return back(undefined, "Partner not found");

    if (action === "addTrip") {
      const list = parseStopList(get("stops", 3000));
      if (list.length < 2) return back(p.id, "Add at least two stops, separated by ; (e.g. Land's End; Bristol (car); John o' Groats (car))");
      const stops: PartnerTrip["stops"] = [];
      const missing: string[] = [];
      for (const s of list) {
        const hit = (await searchPlaces(s.name, true))[0];
        if (!hit) missing.push(s.name);
        else stops.push([s.name, Math.round(hit.lng * 1e4) / 1e4, Math.round(hit.lat * 1e4) / 1e4, ...(s.mode ? [s.mode] : [])] as PartnerTrip["stops"][number]);
      }
      if (missing.length) return back(p.id, `Couldn't find: ${missing.join(", ")}. Try adding the region or country.`);
      const name = get("tripName", 80) || `${list[0].name} to ${list[list.length - 1].name}`;
      const trip: PartnerTrip = {
        id: slugify(name) || nanoid(6),
        name,
        emoji: get("emoji", 8) || "🗺️",
        title: get("title", 80) || name,
        subtitle: get("subtitle", 120),
        preset: PRESETS.some((x) => x.id === get("preset")) ? get("preset") : "vintage",
        stickers: [],
        stops,
        ...(get("askName") || get("askDetail") ? { ask: { ...(get("askName") ? { name: get("askName", 60) } : {}), ...(get("askDetail") ? { detail: get("askDetail", 60) } : {}) } } : {}),
      };
      await savePartner({ ...p, trips: [...p.trips.filter((t) => t.id !== trip.id), trip] });
      return back(p.id, `Route “${name}” added`);
    }
    if (action === "removeTrip") {
      await savePartner({ ...p, trips: p.trips.filter((t) => t.id !== get("trip")) });
      return back(p.id, "Route removed");
    }
    if (action === "code") {
      const code = get("code", 30).toUpperCase().replace(/[^A-Z0-9]/g, "");
      const pct = num("pct");
      if (code.length < 4 || !(pct >= 1 && pct <= 50)) return back(p.id, "A code of 4+ letters/numbers and 1–50% off");
      if (p.promoId) return back(p.id, "This partner already has a code: deactivate it in Stripe first if you want a new one");
      await createPartnerCode(p, code, pct);
      return back(p.id, `Code ${code} created in Stripe`);
    }
    if (action === "trade") {
      const region = (REGIONS.some((r) => r.id === get("region")) ? get("region") : "GB") as RegionId;
      const { batch, cards } = await issueTradeCodes(p, Math.floor(num("count")), num("value"), region);
      return back(p.id, `${cards.length} codes made (batch ${batch}). Download them below, then send the invoice.`);
    }
    if (action === "invoice") {
      const r = await invoiceTradeBatch(p, get("batch", 40));
      return back(p.id, `Invoice for ${r.total} ${r.currency.toUpperCase()} sent by Stripe to ${p.contactEmail}`);
    }
    if (action === "payout") {
      const amount = num("amount");
      if (!(amount > 0)) return back(p.id, "Enter the amount paid");
      const currency = ["gbp", "usd", "aud"].includes(get("currency")) ? get("currency") : "gbp";
      await savePartner({ ...p, payouts: [...(p.payouts ?? []), { at: new Date().toISOString(), amount, currency, note: get("note", 120) || undefined }] });
      return back(p.id, "Payment recorded");
    }
    return back(p.id, "Unknown action");
  } catch (e) {
    await logError("admin.partners", e, { action });
    return back(get("id") || undefined, `Error: ${String((e as Error)?.message ?? e).slice(0, 200)}`);
  }
}
