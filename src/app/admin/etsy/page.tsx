import Link from "next/link";
import Logo from "@/components/Logo";
import { listOrders } from "@/lib/server/db";
import { ALL_SKUS, etsyConfigured, etsyConnection, etsyDesignUrl, etsyRedirectUri } from "@/lib/server/etsy";
import { FRAMES, getProduct } from "@/lib/products";
import { publicUrl } from "@/lib/server/urls";

export const dynamic = "force-dynamic";
export const metadata = { title: "Etsy · Mapsie admin" };

const NOTES: Record<string, string> = {
  cancelled: "Connection cancelled on Etsy.",
  expired: "That took too long. Try connecting again.",
  failed: "Etsy didn't accept the connection. Check the keys and the callback URL, then try again (details on the Errors page).",
};

export default async function EtsyAdmin({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const q = await searchParams;
  const conn = await etsyConnection();
  const orders = (await listOrders()).filter((o) => o.source === "etsy");
  const waiting = orders.filter((o) => o.status === "awaiting_design");
  const box = "rounded-3xl bg-white p-6 shadow-sm space-y-3";
  const btn = "rounded-full px-4 py-2 text-sm font-extrabold";
  return (
    <main className="max-w-5xl mx-auto px-6 py-10 space-y-6">
      <div>
        <Link href="/" className="font-display text-2xl font-extrabold"><Logo /></Link>
        <div className="flex items-baseline gap-4 mt-2">
          <h1 className="text-3xl font-extrabold">Etsy</h1>
          <Link href="/admin" className="text-sm font-bold text-coral-dark">← All orders</Link>
        </div>
      </div>

      {q.connected && <p className="rounded-2xl bg-sea/10 px-4 py-3 text-sm font-bold text-sea">Connected to {q.connected}. New paid orders will appear here within 5 minutes.</p>}
      {q.error && <p className="rounded-2xl bg-coral/10 px-4 py-3 text-sm font-bold text-coral-dark">{NOTES[q.error] ?? q.error}</p>}
      {q.synced && <p className="rounded-2xl bg-sea/10 px-4 py-3 text-sm font-bold text-sea">Checked Etsy: {q.synced} new print{q.synced === "1" ? "" : "s"}.</p>}
      {q.resent && <p className="rounded-2xl bg-sea/10 px-4 py-3 text-sm font-bold text-sea">Design link sent again.</p>}

      <section className={box}>
        <h2 className="text-xl font-extrabold">Connection</h2>
        {!etsyConfigured() ? (
          <div className="text-sm space-y-2">
            <p>Add these on Render, to <b>both</b> services (mapsie and mapsie-worker), then redeploy:</p>
            <ul className="list-disc pl-5">
              <li><code>ETSY_API_KEY</code>: your app&apos;s keystring</li>
              <li><code>ETSY_SHARED_SECRET</code>: your app&apos;s shared secret</li>
            </ul>
            <p>In your Etsy app settings, the callback URL must be <code>{etsyRedirectUri()}</code>.</p>
          </div>
        ) : conn?.shopId ? (
          <div className="flex flex-wrap items-center gap-3 text-sm">
            <span>Connected to <b>{conn.shopName}</b> since {new Date(conn.connectedAt).toLocaleDateString("en-GB")}.</span>
            <form action="/api/admin/etsy" method="post"><input type="hidden" name="action" value="sync" /><button className={`${btn} bg-coral text-white`}>Check for new orders now</button></form>
            <form action="/api/admin/etsy" method="post"><input type="hidden" name="action" value="disconnect" /><button className={`${btn} border-2 border-ink/15`}>Disconnect</button></form>
          </div>
        ) : (
          <div className="text-sm space-y-2">
            <p>Keys are set. Connect your shop so Mapsie can read new orders and add tracking to them.</p>
            <p className="text-ink/60">Callback URL to put in your Etsy app: <code>{etsyRedirectUri()}</code></p>
            <a href="/api/admin/etsy/connect" className={`${btn} inline-block bg-coral text-white`}>Connect Etsy shop</a>
          </div>
        )}
      </section>

      <section className={box}>
        <h2 className="text-xl font-extrabold">Setting up the listing</h2>
        <ol className="list-decimal pl-5 text-sm space-y-1.5">
          <li>Create a listing, e.g. “Custom travel map poster, personalised with your trip”. Mark it as made to order, and add Prodigi as your production partner.</li>
          <li>Add variations for <b>Size</b> and <b>Frame</b> (choose the ones you want to sell) and give each combination its SKU from the table below. That&apos;s how Mapsie knows what was bought.</li>
          <li>
            In Shop Manager → Settings → Info &amp; appearance, set the automatic <b>order confirmation message</b> to something like:
            <blockquote className="mt-1 rounded-xl bg-sand/60 px-3 py-2 italic">
              Thank you! Now design your map: go to {publicUrl().replace(/^https?:\/\//, "")}/etsy and enter your order number and postcode. It takes about 5 minutes,
              you&apos;ll see a preview before it&apos;s printed, and there&apos;s nothing more to pay.
            </blockquote>
          </li>
          <li>Set processing time to allow for the design step (e.g. 3–7 days). Express shipping on Etsy is sent express by Prodigi if its name includes “Express”.</li>
        </ol>
        <details className="text-sm">
          <summary className="font-bold cursor-pointer">SKUs for every size and frame ({ALL_SKUS.length})</summary>
          <table className="mt-2 w-full">
            <thead className="text-left text-xs uppercase tracking-wider text-ink/50"><tr><th className="py-1">SKU</th><th>Size</th><th>Frame</th></tr></thead>
            <tbody>
              {ALL_SKUS.map((s) => (
                <tr key={s.sku} className="border-t border-ink/5"><td className="py-1 font-mono text-xs">{s.sku}</td><td>{s.product}</td><td>{s.frame}</td></tr>
              ))}
            </tbody>
          </table>
        </details>
      </section>

      <section className={box}>
        <h2 className="text-xl font-extrabold">Etsy orders <span className="text-ink/40 text-base">({waiting.length} waiting for a design)</span></h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-left text-xs uppercase tracking-wider text-ink/50">
              <tr>{["Etsy order", "Bought", "Print", "Buyer", "Status", ""].map((h) => <th key={h} className="px-2 py-2">{h}</th>)}</tr>
            </thead>
            <tbody>
              {orders.map((o) => (
                <tr key={o.id} className="border-t border-ink/5 align-top">
                  <td className="px-2 py-2">
                    <a className="font-bold underline" href={`https://www.etsy.com/your/orders/sold?order_id=${o.etsy?.receiptId}`} target="_blank" rel="noreferrer">{o.etsy?.receiptId}</a>
                    {o.etsy && o.etsy.of > 1 && <div className="text-ink/40">print {o.etsy.unit} of {o.etsy.of}</div>}
                  </td>
                  <td className="px-2 py-2 whitespace-nowrap">{new Date(o.createdAt).toLocaleDateString("en-GB")}</td>
                  <td className="px-2 py-2">
                    {o.print ? `${getProduct(o.print.productId).label}, ${FRAMES.find((f) => f.id === o.print!.frame)?.label}` : "?"}
                    {o.etsy && !o.etsy.matched && <div className="text-xs font-bold text-coral-dark">Guessed: check SKU ({o.etsy.choices || "no options"})</div>}
                  </td>
                  <td className="px-2 py-2">{o.address?.name}<div className="text-ink/40">{o.email || "no email from Etsy"}</div></td>
                  <td className="px-2 py-2">
                    <span className="rounded-full bg-sand px-2.5 py-1 text-xs font-bold">{o.status.replace(/_/g, " ")}</span>
                    {o.emailsSent?.some((k) => k.startsWith("etsy-")) && <div className="text-xs text-ink/40 mt-1">{o.emailsSent.filter((k) => k.startsWith("etsy-")).join(", ").replace(/etsy-/g, "")}</div>}
                  </td>
                  <td className="px-2 py-2 space-y-1 text-xs">
                    {o.status === "awaiting_design" ? (
                      <>
                        <a className="block font-bold text-coral-dark underline" href={etsyDesignUrl(o.id)} target="_blank" rel="noreferrer">Design link</a>
                        {o.email && (
                          <form action="/api/admin/etsy" method="post">
                            <input type="hidden" name="action" value="resend" />
                            <input type="hidden" name="orderId" value={o.id} />
                            <button className="font-bold underline">Email it again</button>
                          </form>
                        )}
                      </>
                    ) : (
                      <Link className="font-bold underline" href={`/order/${o.id}`}>Order page</Link>
                    )}
                  </td>
                </tr>
              ))}
              {!orders.length && <tr><td colSpan={6} className="px-2 py-8 text-center text-ink/40">No Etsy orders yet.</td></tr>}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-ink/50">
          Buyers can also find their order at {publicUrl().replace(/^https?:\/\//, "")}/etsy with their order number and postcode. If Etsy doesn&apos;t share a buyer&apos;s email,
          copy the design link and send it to them in an Etsy message.
        </p>
      </section>
    </main>
  );
}
