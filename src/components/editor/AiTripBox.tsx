"use client";
import { useEffect, useRef, useState } from "react";
import type { TripTemplate } from "@/lib/templates";
import { track } from "@/lib/track";

// The browser's own speech recognition (Chrome, Edge, Safari). Not in every browser,
// so the mic button only shows where it works.
type Recognition = {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  start: () => void;
  stop: () => void;
  onresult: ((e: { resultIndex: number; results: ArrayLike<ArrayLike<{ transcript: string }> & { isFinal: boolean }> }) => void) | null;
  onend: (() => void) | null;
  onerror: ((e: { error: string }) => void) | null;
};
const speechApi = () =>
  typeof window === "undefined"
    ? null
    : ((window as unknown as { SpeechRecognition?: new () => Recognition; webkitSpeechRecognition?: new () => Recognition }).SpeechRecognition ??
      (window as unknown as { webkitSpeechRecognition?: new () => Recognition }).webkitSpeechRecognition ??
      null);

declare global {
  interface Window {
    turnstile?: {
      render: (el: HTMLElement, opts: Record<string, unknown>) => string;
      reset: (id: string) => void;
    };
  }
}

const EXAMPLES = [
  "Two weeks in Sri Lanka: Colombo, the train from Kandy to Ella, then tuk-tuks down to Mirissa and Galle",
  "Our honeymoon: Paris, then the train to Florence and Rome, flying home from Naples",
  "Route 66 road trip from Chicago to Santa Monica",
];

/** "Describe your trip" box: typed or spoken, Claude plans the map, the editor applies it. */
export default function AiTripBox({ onTrip, replacing }: { onTrip: (t: TripTemplate, reply: string) => void; replacing?: boolean }) {
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState("");
  const [err, setErr] = useState("");
  const [listening, setListening] = useState(false);
  const [canSpeak, setCanSpeak] = useState(false);
  const rec = useRef<Recognition | null>(null);
  const base = useRef("");

  useEffect(() => setCanSpeak(!!speechApi()), []);
  useEffect(() => () => rec.current?.stop(), []);

  // Is it switched on, and is there a bot check (Cloudflare Turnstile) to run?
  const [enabled, setEnabled] = useState<boolean | null>(null);
  const [siteKey, setSiteKey] = useState<string | null>(null);
  const checkBox = useRef<HTMLDivElement>(null);
  const widget = useRef<string | null>(null);
  const token = useRef<string>("");
  useEffect(() => {
    fetch("/api/ai/design")
      .then((r) => r.json())
      .then((j: { enabled: boolean; turnstileSiteKey: string | null }) => (setEnabled(j.enabled), setSiteKey(j.turnstileSiteKey)))
      .catch(() => setEnabled(true));
  }, []);
  useEffect(() => {
    if (!siteKey || !checkBox.current) return;
    const mount = () => {
      if (!window.turnstile || !checkBox.current || widget.current) return;
      // Invisible unless Cloudflare needs the visitor to tick a box.
      widget.current = window.turnstile.render(checkBox.current, {
        sitekey: siteKey,
        appearance: "interaction-only",
        callback: (t: string) => (token.current = t),
        "expired-callback": () => (token.current = ""),
      });
    };
    if (window.turnstile) return mount();
    let s = document.getElementById("cf-turnstile") as HTMLScriptElement | null;
    if (!s) {
      s = document.createElement("script");
      s.id = "cf-turnstile";
      s.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
      s.async = true;
      document.head.appendChild(s);
    }
    s.addEventListener("load", mount);
    return () => s?.removeEventListener("load", mount);
  }, [siteKey, enabled]);
  // Tokens work once: get a fresh one after each try.
  const freshCheck = () => {
    token.current = "";
    if (widget.current && window.turnstile) window.turnstile.reset(widget.current);
  };

  const toggleMic = () => {
    if (listening) return rec.current?.stop();
    const Api = speechApi();
    if (!Api) return;
    const r = new Api();
    r.lang = navigator.language || "en-GB";
    r.interimResults = true;
    r.continuous = true;
    base.current = text ? text.trimEnd() + " " : "";
    r.onresult = (e) => {
      let finals = "", interim = "";
      for (let i = 0; i < e.results.length; i++) {
        const t = e.results[i][0].transcript;
        if (e.results[i].isFinal) finals += t;
        else interim += t;
      }
      setText(base.current + finals + interim);
    };
    r.onerror = (e) => {
      if (e.error === "not-allowed") setErr("Allow the microphone to talk to me, or type instead.");
    };
    r.onend = () => setListening(false);
    rec.current = r;
    setErr("");
    setListening(true);
    track("ai_mic");
    r.start();
  };

  const go = async () => {
    rec.current?.stop();
    if (text.trim().length < 3) return setErr("Tell me about your trip first.");
    setBusy(true);
    setErr("");
    setNote("");
    track("ai_create");
    try {
      if (siteKey && !token.current) {
        // Give the invisible check a moment to finish.
        for (let i = 0; i < 20 && !token.current; i++) await new Promise((x) => setTimeout(x, 250));
      }
      const r = await fetch("/api/ai/design", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ prompt: text, turnstileToken: token.current || undefined }) });
      freshCheck();
      const j = (await r.json()) as { trip?: TripTemplate | null; reply?: string; error?: string };
      if (!r.ok) return setErr(j.error ?? "Something went wrong. Please try again.");
      if (!j.trip) return setNote(j.reply ?? "Tell me where you went and I'll map it.");
      setText("");
      onTrip(j.trip, `${j.reply ?? "Here's your map."} Change anything you like.`);
    } catch {
      setErr("Couldn't reach Mapsie. Check your connection and try again.");
    } finally {
      setBusy(false);
    }
  };

  if (enabled === false) return null;
  return (
    <div className="rounded-2xl bg-gradient-to-br from-coral/10 to-sea/10 border border-coral/20 p-3 space-y-2">
      <div className="text-sm font-extrabold">✨ Describe your trip</div>
      <div className="relative">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && (e.metaKey || e.ctrlKey) && go()}
          rows={3}
          maxLength={2000}
          placeholder={`e.g. ${EXAMPLES[0]}`}
          className="w-full rounded-xl border-2 border-ink/10 bg-white px-3 py-2 pr-11 text-sm outline-none focus:border-coral resize-none"
        />
        {canSpeak && (
          <button
            type="button"
            onClick={toggleMic}
            title={listening ? "Stop listening" : "Talk instead of typing"}
            aria-label={listening ? "Stop listening" : "Talk instead of typing"}
            className={`absolute right-2 top-2 grid h-8 w-8 place-items-center rounded-full ${listening ? "bg-coral text-white animate-pulse" : "bg-sand text-ink/70 hover:bg-coral/20"}`}
          >
            🎙️
          </button>
        )}
      </div>
      {listening && <div className="text-xs font-bold text-coral-dark">Listening… say where you went, in order. Tap 🎙️ when you&apos;re done.</div>}
      {replacing && <div className="text-xs text-ink/50">This replaces the stops on your map (you can undo).</div>}
      <button onClick={go} disabled={busy} className="w-full rounded-full bg-coral py-2.5 text-sm font-extrabold text-white disabled:opacity-60">
        {busy ? "Planning your map…" : "Create my map"}
      </button>
      {siteKey && <div ref={checkBox} />}
      {err && <div className="text-xs font-bold text-coral-dark">{err}</div>}
      {note && <div className="text-xs text-ink/70">{note}</div>}
      {!text && !busy && !note && (
        <div className="flex flex-wrap gap-1">
          {EXAMPLES.slice(1).map((x) => (
            <button key={x} onClick={() => setText(x)} className="rounded-full bg-white/70 border border-ink/10 px-2 py-0.5 text-[11px] text-ink/60 hover:border-coral text-left">
              {x.length > 48 ? x.slice(0, 46) + "…" : x}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
