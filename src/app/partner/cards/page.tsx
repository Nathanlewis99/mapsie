import { notFound, redirect } from "next/navigation";
import QRCode from "qrcode";
import { listGiftCards } from "@/lib/server/db";
import { giftCardUrl } from "@/lib/server/giftcards";
import { currentPartner } from "@/lib/server/partnerAuth";
import { getSession } from "@/lib/server/auth";
import { adminMfaValid } from "@/lib/session";
import { getPartner } from "@/lib/server/partners";
import PrintButton from "@/app/gift/card/[id]/PrintButton";

export const dynamic = "force-dynamic";
export const metadata = { title: "Printable gift cards · Mapsie", robots: { index: false } };

const money = (n: number, c: string) => `${{ gbp: "£", usd: "$", aud: "A$" }[c] ?? ""}${Number.isInteger(n) ? n : n.toFixed(2)}`;

// A sheet of a batch's codes as cards to cut out: 8 per A4 page (A7 size, 105 × 74 mm), each with
// its code and a QR code that opens the card online. For shops' counters, finisher packs and gifts.
export default async function TradeCards({ searchParams }: { searchParams: Promise<{ p?: string; batch?: string }> }) {
  const q = await searchParams;
  // Partners see their own batches; an admin (signed in with 2FA) can open any.
  const admin = adminMfaValid(await getSession());
  const partner = admin ? await getPartner(q.p ?? "") : (await currentPartner(q.p))?.partner;
  if (!partner) redirect("/partner/signin");
  const cards = (await listGiftCards(5000)).filter((g) => g.partnerId === partner.id && g.tradeBatch === q.batch && g.code && g.status === "active").sort((a, b) => a.id.localeCompare(b.id, undefined, { numeric: true }));
  if (!cards.length) notFound();
  const withQr = await Promise.all(cards.map(async (g) => ({ g, qr: await QRCode.toString(giftCardUrl(g.id), { type: "svg", margin: 0, errorCorrectionLevel: "M", color: { dark: "#1f2430", light: "#00000000" } }) })));
  const pages: (typeof withQr)[] = [];
  for (let i = 0; i < withQr.length; i += 8) pages.push(withQr.slice(i, i + 8));
  return (
    <main className="bg-sand/40 print:bg-white min-h-dvh py-8 print:py-0">
      <style>{`@page{size:A4;margin:0}.sheet{width:210mm;height:297mm;display:grid;grid-template-columns:105mm 105mm;grid-template-rows:repeat(4,74.25mm);background:#fff;margin:0 auto 8mm;box-shadow:0 10px 30px rgba(0,0,0,.08)}@media print{.sheet{margin:0;box-shadow:none;page-break-after:always}}.card{border:0.2mm dashed #1f243022;padding:6mm 6mm 5mm 7mm;display:flex;gap:4mm}.qr svg{width:24mm;height:24mm}`}</style>
      <div className="max-w-[210mm] mx-auto mb-6 flex justify-between items-center px-2 print:hidden">
        <div>
          <h1 className="text-xl font-extrabold">{cards.length} unused gift cards for {partner.name}</h1>
          <p className="text-sm text-ink/60">Print on A4 card (300gsm works well), then cut along the dashed lines.</p>
        </div>
        <PrintButton />
      </div>
      {pages.map((page, i) => (
        <section key={i} className="sheet">
          {page.map(({ g, qr }) => (
            <div key={g.id} className="card">
              <div className="flex-1 flex flex-col min-w-0">
                <div className="font-display text-[19pt] font-extrabold leading-none">Mapsie<span className="text-coral">.</span></div>
                <div className="mt-[2.5mm] text-[9.5pt] font-bold leading-snug">A gift card for a map of your trip: every stop, your photos, printed and delivered.</div>
                <div className="mt-auto">
                  <div className="text-[18pt] font-extrabold leading-none">{money(g.amount, g.currency)}</div>
                  <div className="mt-[1.5mm] font-mono text-[11pt] font-bold tracking-wide">{g.code}</div>
                  <div className="text-[6.5pt] text-ink/60 mt-[1mm]">Design at mapsie.shop, enter the code at checkout. Valid until {g.expiresAt ? new Date(g.expiresAt).toLocaleDateString("en-GB", { month: "short", year: "numeric" }) : ""}.</div>
                </div>
              </div>
              <div className="flex flex-col items-center justify-end gap-[1mm]">
                <div className="qr" dangerouslySetInnerHTML={{ __html: qr }} />
                <div className="text-[6pt] text-ink/50 font-bold">Scan to start</div>
              </div>
            </div>
          ))}
        </section>
      ))}
    </main>
  );
}
