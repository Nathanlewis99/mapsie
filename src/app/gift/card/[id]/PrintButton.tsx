"use client";
export default function PrintButton() {
  return <button onClick={() => window.print()} className="rounded-full bg-ink text-white px-5 py-2.5 font-extrabold">🖨️ Print card</button>;
}
