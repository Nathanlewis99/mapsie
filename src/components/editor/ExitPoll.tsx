"use client";
import { useState } from "react";
import { trackEach } from "@/lib/track";

/** One question, once: what's stopping them? Answers go to our anonymous stats (see the admin funnel). */
interface Answer { id: string; label: string; ask?: string }
const ANSWERS: Answer[] = [
  { id: "browsing", label: "👀 Just looking for now" },
  { id: "price", label: "💷 It costs more than I expected" },
  { id: "look", label: "🎨 I can't get it looking how I want", ask: "What would you like it to look like?" },
  { id: "ux", label: "😕 The designer is confusing or fiddly to use", ask: "What was confusing or hard to do?" },
  { id: "later", label: "📅 I'll order later, closer to the date" },
  { id: "other", label: "✏️ Something else", ask: "What's stopping you?" },
];

export default function ExitPoll({ onClose, context }: { onClose: () => void; context: Record<string, string | number | boolean> }) {
  const [pick, setPick] = useState<Answer | null>(null);
  const [note, setNote] = useState("");
  const [done, setDone] = useState(false);

  const send = (a: Answer, text = "") => {
    trackEach("exit_poll", { answer: a.id, ...(text.trim() ? { note: text.trim().slice(0, 300) } : {}), ...context });
    setDone(true);
    setTimeout(onClose, 1800);
  };
  const choose = (a: Answer) => (a.ask ? setPick(a) : send(a));

  return (
    <div className="fixed inset-x-0 bottom-0 z-50 sm:inset-auto sm:bottom-6 sm:right-6 sm:max-w-sm">
      <div className="relative rounded-t-3xl sm:rounded-3xl bg-white p-5 pb-6 shadow-2xl border border-ink/10 space-y-3">
        <button type="button" onClick={() => (trackEach("exit_poll", { answer: "closed", ...context }), onClose())} aria-label="Close" className="absolute right-3 top-3 grid h-9 w-9 place-items-center rounded-full text-xl text-ink/50 hover:bg-sand">×</button>
        {done ? (
          <div className="py-4 text-center font-extrabold">Thank you! That really helps us. 💛</div>
        ) : pick ? (
          <form onSubmit={(e) => (e.preventDefault(), send(pick, note))} className="space-y-3 pr-6">
            <div className="font-extrabold">{pick.ask}</div>
            <textarea value={note} onChange={(e) => setNote(e.target.value)} rows={3} maxLength={300} autoFocus placeholder="Optional, but it helps us fix it" className="w-full rounded-2xl border-2 border-ink/10 px-3 py-2 text-sm outline-none focus:border-coral" />
            <div className="flex gap-2">
              <button type="submit" className="rounded-full bg-coral px-4 py-2 font-extrabold text-white">Send</button>
              <button type="button" onClick={() => send(pick)} className="rounded-full px-3 py-2 font-bold text-ink/50">Skip</button>
            </div>
          </form>
        ) : (
          <>
            <div className="pr-8">
              <div className="font-display text-lg font-extrabold">Quick question: what&apos;s stopping you ordering today?</div>
              <p className="text-xs text-ink/50 mt-1">One tap, anonymous. It helps us make Mapsie better.</p>
            </div>
            <div className="grid gap-1.5">
              {ANSWERS.map((a) => (
                <button key={a.id} onClick={() => choose(a)} className="rounded-2xl border-2 border-ink/10 px-3 py-2 text-left text-sm font-bold hover:border-coral">
                  {a.label}
                </button>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
