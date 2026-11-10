"use client";
import { use, useState } from "react";
import { useRouter } from "next/navigation";

// Stand-in for Stripe while no keys are configured.
export default function TestCheckout({ params }: { params: Promise<{ orderId: string }> }) {
  const { orderId } = use(params);
  const router = useRouter();
  const [a, setA] = useState({ name: "Test Traveller", line1: "1 Example Street", city: "London", postcode: "SW1A 1AA" });
  const [busy, setBusy] = useState(false);
  const field = (k: keyof typeof a, label: string) => (
    <label className="block">
      <span className="text-xs font-bold uppercase tracking-wider text-ink/50">{label}</span>
      <input value={a[k]} onChange={(e) => setA({ ...a, [k]: e.target.value })} className="mt-1 w-full rounded-2xl border-2 border-ink/10 bg-white px-4 py-3 font-semibold outline-none focus:border-coral" />
    </label>
  );
  return (
    <main className="max-w-md mx-auto px-6 py-14 space-y-4">
      <div className="rounded-2xl bg-sea/15 text-ink px-4 py-3 text-sm font-bold">🧪 Test checkout: Stripe isn&apos;t connected yet, so no real payment is taken.</div>
      <h1 className="font-display text-3xl font-extrabold">Delivery address</h1>
      {field("name", "Full name")}
      {field("line1", "Address")}
      {field("city", "Town / city")}
      {field("postcode", "Postcode")}
      <button
        disabled={busy}
        onClick={async () => {
          setBusy(true);
          await fetch(`/api/orders/${orderId}/mock-pay`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(a) });
          router.push(`/order/${orderId}`);
        }}
        className="w-full rounded-full bg-coral py-4 text-lg font-extrabold text-white disabled:opacity-50"
      >
        {busy ? "Placing order…" : "Place test order"}
      </button>
    </main>
  );
}
