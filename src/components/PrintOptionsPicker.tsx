"use client";
import { FRAMES, GLAZES, MOUNTS, PAPERS, PRODUCTS, getProduct, money, type PrintOptions, type RegionId } from "@/lib/products";

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
  const framed = value.frame !== "none";
  const fp = p.framePrice[region];
  // Prodigi's A-size frames only use Matte art.
  const shownPaper = framed ? "ema" : value.paper;
  return (
    <div className="space-y-5">
      {showSizes && (
        <div>
          <Heading>Print size</Heading>
          <div className="space-y-2">
            {PRODUCTS.map((x) => (
              <button key={x.id} onClick={() => onChange({ productId: x.id })} className={`flex w-full items-center justify-between px-4 py-3 ${card(value.productId === x.id)}`}>
                <span className="font-bold text-left">
                  {x.label}
                  {sizeNote?.(x.id) && (
                    <span className={`block text-[11px] font-extrabold ${sizeNote(x.id) === "Recommended" ? "text-sea" : "text-coral-dark"}`}>{sizeNote(x.id)}</span>
                  )}
                </span>
                <span className="text-sm text-ink/50">{x.widthCm} × {x.heightCm} cm</span>
                <span className="font-extrabold">{money(region, x.price[region])}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      <div>
        <Heading>Frame</Heading>
        <div className="grid grid-cols-3 sm:grid-cols-5 gap-2">
          {FRAMES.map((f) => (
            <button key={f.id} onClick={() => onChange({ frame: f.id })} className={`p-2 text-center ${card(value.frame === f.id)}`}>
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
                disabled={framed && x.id !== "ema"}
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
    </div>
  );
}
