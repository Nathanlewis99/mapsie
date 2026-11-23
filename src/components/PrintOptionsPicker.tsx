"use client";
import { useState } from "react";
import { DIGITAL_PRICE, FRAMES, GLAZES, MOUNTS, PAPERS, PRODUCTS, getProduct, money, type PrintOptions, type RegionId } from "@/lib/products";

const Heading = ({ children }: { children: React.ReactNode }) => <div className="text-xs font-bold uppercase tracking-wider text-ink/50 mb-2">{children}</div>;
const card = (on: boolean) => `rounded-2xl border-2 bg-white transition ${on ? "border-coral" : "border-ink/10 hover:border-ink/30"}`;

/** Size, paper, frame, mount and glazing. Used in the editor and again at checkout. */
export default function PrintOptionsPicker({
  value,
  onChange,
  region,
  showSizes = true,
  sizeNote,
}: {
  sizeNote?: (productId: string) => string | undefined;
  value: Required<PrintOptions>;
  onChange: (patch: Partial<PrintOptions>) => void;
  region: RegionId;
  showSizes?: boolean;
}) {
  const p = getProduct(value.productId);
  const [moreOpen, setMoreOpen] = useState(false);
  // Choosing a size also drops options Prodigi doesn't make at that size (frames, some papers).
  const pickSize = (id: string) => {
    const x = getProduct(id);
    onChange({ productId: id, ...(x.unframed && value.frame !== "none" ? { frame: "none" as const } : {}), ...(x.papers && !x.papers.includes(value.paper) ? { paper: "ema" as const } : {}) });
  };
  const sizeRow = (x: (typeof PRODUCTS)[number]) => (
    <button key={x.id} onClick={() => (pickSize(x.id), setMoreOpen(false))} className={`flex w-full items-center justify-between gap-3 px-4 py-3 ${card(value.productId === x.id)}`}>
      <span className="font-bold text-left">
        {x.label}
        {sizeNote?.(x.id) && <span className={`block text-[11px] font-extrabold ${sizeNote(x.id) === "Recommended" ? "text-sea" : "text-coral-dark"}`}>{sizeNote(x.id)}</span>}
        {x.unframed && !digital && <span className="block text-[11px] font-bold text-ink/45">Poster only (no frame)</span>}
      </span>
      <span className="text-sm text-ink/50">{x.widthCm} × {x.heightCm} cm</span>
      <span className="font-extrabold">{money(region, digital ? DIGITAL_PRICE[region] : x.price[region])}</span>
    </button>
  );
  const framed = value.frame !== "none";
  const fp = p.framePrice[region];
  // Prodigi's A-size frames only use Matte art.
  const shownPaper = framed ? "ema" : value.paper;
  const digital = value.format === "digital";
  return (
    <div className="space-y-5">
      <div>
        <Heading>Format</Heading>
        <div className="grid grid-cols-2 gap-2">
          {[
            { id: "print" as const, label: "Printed poster", note: "Printed, framed if you like, and delivered" },
            { id: "digital" as const, label: "Digital file", note: `300 dpi PNG to print yourself · ${money(region, DIGITAL_PRICE[region])}` },
          ].map((f) => (
            <button key={f.id} onClick={() => onChange({ format: f.id })} className={`px-4 py-3 text-left ${card((value.format ?? "print") === f.id)}`}>
              <span className="font-bold block">{f.label}</span>
              <span className="text-[11px] text-ink/50 block">{f.note}</span>
            </button>
          ))}
        </div>
      </div>
      {showSizes && (
        <div>
          <Heading>Print size</Heading>
          <div className="space-y-2">
            {PRODUCTS.filter((x) => !x.more || x.id === value.productId).map(sizeRow)}
            <button onClick={() => setMoreOpen(true)} className="w-full rounded-2xl border-2 border-dashed border-ink/15 px-4 py-2.5 text-sm font-extrabold text-ink/70 hover:border-coral">
              More sizes, up to 100 × 150 cm →
            </button>
          </div>
          {moreOpen && (
            <div className="fixed inset-0 z-50 grid place-items-center bg-ink/40 p-4" onClick={() => setMoreOpen(false)} role="dialog" aria-label="All print sizes">
              <div className="w-full max-w-lg max-h-[85dvh] overflow-y-auto rounded-3xl bg-cream p-5 shadow-2xl" onClick={(e) => e.stopPropagation()}>
                <div className="flex items-center justify-between">
                  <h3 className="font-display text-2xl font-extrabold">All sizes</h3>
                  <button onClick={() => setMoreOpen(false)} className="w-9 h-9 rounded-full hover:bg-ink/5 text-xl" aria-label="Close">×</button>
                </div>
                <p className="text-sm text-ink/60 mt-1">Big statement prints are printed on matte art or German etching paper and rolled in a tube. 60 × 90 cm can also be framed.</p>
                <div className="mt-4 space-y-2">{PRODUCTS.map(sizeRow)}</div>
              </div>
            </div>
          )}
        </div>
      )}

      {!digital && <>
      <div>
        <Heading>Frame</Heading>
        <div className="grid grid-cols-3 sm:grid-cols-5 gap-2">
          {FRAMES.map((f) => (
            <button key={f.id} onClick={() => onChange({ frame: f.id })} disabled={p.unframed && f.id !== "none"} className={`p-2 text-center disabled:opacity-35 disabled:cursor-not-allowed ${card(value.frame === f.id)}`}>
              <div
                className="mx-auto w-9 h-11 rounded-sm"
                style={f.id === "none" ? { boxShadow: "inset 0 0 0 1px #0002", background: "#f1e8da" } : { background: f.finish ?? f.color, padding: 4 }}
              >
                {f.id !== "none" && <div className="w-full h-full bg-sand rounded-[1px]" />}
              </div>
              <div className="text-[11px] font-bold mt-1 leading-tight">{f.label}</div>
              <div className="text-[11px] text-ink/50">{f.id === "none" ? "Rolled in a tube" : `+${money(region, fp)}`}</div>
            </button>
          ))}
        </div>
        {framed && (
          <p className="text-xs text-ink/50 mt-2">
            Classic wooden frame with clear Perspex, ready to hang. Framed prints use our Matte art paper ({PAPERS[0].spec}): {PAPERS[0].detail.split(".")[0].toLowerCase()}.
          </p>
        )}
      </div>

        <div>
          <Heading>Paper</Heading>
          {framed && <p className="text-xs text-ink/50 -mt-1 mb-2">Framed prints come on Matte art. Choose “No frame” to pick another paper.</p>}
          <div className="space-y-2">
            {PAPERS.map((x) => (
              <button
                key={x.id}
                onClick={() => onChange({ paper: x.id })}
                disabled={(framed && x.id !== "ema") || (!!p.papers && !p.papers.includes(x.id))}
                className={`flex w-full items-center justify-between gap-3 px-4 py-2.5 text-left disabled:opacity-40 disabled:cursor-not-allowed ${card(shownPaper === x.id)}`}
              >
                <span>
                  <span className="font-bold block">{x.label}</span>
                  <span className="text-[11px] font-bold text-ink/45 block">{x.spec}</span>
                  {shownPaper === x.id ? (
                    <>
                      <span className="text-xs text-ink/70 block mt-1">{x.detail}</span>
                      <span className="text-xs font-bold text-sea block mt-1">Best for: {x.bestFor}</span>
                    </>
                  ) : (
                    <span className="text-xs text-ink/50 block">{x.bestFor}</span>
                  )}
                </span>
                <span className="font-extrabold text-sm shrink-0">{x.extra ? `+${money(region, Math.round(p.price[region] * x.extra))}` : "Included"}</span>
              </button>
            ))}
          </div>
        </div>
      {framed && (
        <>
          <div>
            <Heading>Mount</Heading>
            <div className="grid grid-cols-4 gap-2">
              {MOUNTS.map((m) => (
                <button key={m.id} onClick={() => onChange({ mount: m.id })} className={`p-2 text-center ${card(value.mount === m.id)}`}>
                  <div className="mx-auto w-9 h-11 rounded-sm" style={{ background: "#1b1b1b", padding: 3 }}>
                    <div className="w-full h-full rounded-[1px]" style={{ background: m.id === "none" ? "#f1e8da" : m.color, padding: m.id === "none" ? 0 : 5 }}>
                      {m.id !== "none" && <div className="w-full h-full bg-sea/40" />}
                    </div>
                  </div>
                  <div className="text-[11px] font-bold mt-1 leading-tight">{m.label}</div>
                  <div className="text-[11px] text-ink/50">{m.id === "none" ? "—" : `+${money(region, Math.round(fp * 0.2))}`}</div>
                </button>
              ))}
            </div>
            {value.mount !== "none" && <p className="text-xs text-ink/50 mt-2">A card border inside the frame. Your map is printed a little smaller to sit in the window.</p>}
          </div>
          {GLAZES.length > 1 && <div>
            <Heading>Glazing</Heading>
            <div className="space-y-2">
              {GLAZES.map((g) => (
                <button key={g.id} onClick={() => onChange({ glaze: g.id })} className={`flex w-full items-center justify-between gap-3 px-4 py-2.5 text-left ${card(value.glaze === g.id)}`}>
                  <span>
                    <span className="font-bold block">{g.label}</span>
                    <span className="text-xs text-ink/50">{g.detail}</span>
                  </span>
                  <span className="font-extrabold text-sm shrink-0">{g.extra ? `+${money(region, Math.round(fp * g.extra))}` : "Included"}</span>
                </button>
              ))}
            </div>
          </div>}
        </>
      )}
      </>}
    </div>
  );
}
