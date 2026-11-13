"use client";
import { useActionState } from "react";
import { findEtsyOrder } from "./actions";

const input = "w-full rounded-2xl border-2 border-ink/10 bg-white px-4 py-3 outline-none focus:border-coral transition";

export default function LookupForm() {
  const [s, find, finding] = useActionState(findEtsyOrder, null);
  return (
    <form action={find} className="space-y-3">
      <input name="receipt" inputMode="numeric" required placeholder="Etsy order number, e.g. 3456789012" defaultValue={s?.receipt} className={input} />
      <input name="postcode" required autoComplete="postal-code" placeholder="Delivery postcode / ZIP" defaultValue={s?.postcode} className={input} />
      {s?.error && <p role="alert" className="rounded-2xl bg-coral/10 px-4 py-3 text-sm font-bold text-coral-dark">{s.error}</p>}
      <button disabled={finding} className="w-full rounded-full bg-coral px-5 py-3 font-extrabold text-white shadow-lg shadow-coral/30 disabled:opacity-60">
        {finding ? "Finding your order…" : "Design my map"}
      </button>
    </form>
  );
}
