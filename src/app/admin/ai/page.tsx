import Link from "next/link";
import Logo from "@/components/Logo";
import { AI_MODELS, aiConfigured, liveModel } from "@/lib/server/aiDesign";
import Compare from "./Compare";

export const dynamic = "force-dynamic";
export const metadata = { title: "Create with AI · Admin" };

export default function AiAdmin() {
  return (
    <main className="max-w-6xl mx-auto px-6 py-10 space-y-6">
      <div>
        <Link href="/" className="font-display text-2xl font-extrabold"><Logo /></Link>
        <div className="flex items-baseline gap-4 mt-2">
          <h1 className="text-3xl font-extrabold">Create with AI</h1>
          <Link href="/admin" className="text-sm font-bold text-coral-dark">← All orders</Link>
        </div>
        <p className="text-sm text-ink/60 mt-2">
          Customers get <b>{AI_MODELS[liveModel()].label}</b> (set <code>AI_MODEL</code> on Render to <code>claude-sonnet-5-5</code> or <code>claude-opus-5-5</code> to change it).
          {!aiConfigured() && <b className="text-coral-dark"> ANTHROPIC_API_KEY isn&apos;t set, so nothing will run yet.</b>}
        </p>
      </div>
      <Compare />
    </main>
  );
}
