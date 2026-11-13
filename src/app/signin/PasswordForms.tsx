"use client";
import Link from "next/link";
import { useActionState, useState } from "react";
import { requestPasswordReset, resendVerification, resetPassword, signInWithPassword, signUpWithPassword, type FormState } from "./actions";

const input = "w-full rounded-2xl border-2 border-ink/10 bg-white px-4 py-3 outline-none focus:border-coral transition";
const primary = "w-full rounded-full bg-coral px-5 py-3 font-extrabold text-white shadow-lg shadow-coral/30 disabled:opacity-60";
const ErrorNote = ({ s }: { s: FormState }) =>
  s?.error ? <p role="alert" className="rounded-2xl bg-coral/10 px-4 py-3 text-sm font-bold text-coral-dark">{s.error}</p> : null;

function PasswordInput({ name, autoComplete, placeholder }: { name: string; autoComplete: string; placeholder: string }) {
  const [show, setShow] = useState(false);
  return (
    <div className="relative">
      <input name={name} type={show ? "text" : "password"} required autoComplete={autoComplete} placeholder={placeholder} className={`${input} pr-16`} />
      <button type="button" onClick={() => setShow(!show)} className="absolute right-4 top-1/2 -translate-y-1/2 text-xs font-bold text-ink/50 hover:text-ink">
        {show ? "Hide" : "Show"}
      </button>
    </div>
  );
}

/** Email and password: sign in, or create an account. */
export function PasswordForms({ next, startOn = "signin" }: { next: string; startOn?: "signin" | "signup" }) {
  const [mode, setMode] = useState(startOn);
  const [inState, signIn, signingIn] = useActionState(signInWithPassword, null);
  const [upState, signUp, signingUp] = useActionState(signUpWithPassword, null);
  const tab = (m: typeof mode, label: string) => (
    <button
      type="button"
      onClick={() => setMode(m)}
      aria-pressed={mode === m}
      className={`flex-1 rounded-full py-2 text-sm font-extrabold transition ${mode === m ? "bg-white shadow-sm" : "text-ink/50 hover:text-ink"}`}
    >
      {label}
    </button>
  );
  return (
    <div className="space-y-4">
      <div className="flex rounded-full bg-sand p-1">
        {tab("signin", "Sign in")}
        {tab("signup", "Create account")}
      </div>
      {mode === "signin" ? (
        <form action={signIn} className="space-y-3" key="in">
          <input type="hidden" name="next" value={next} />
          <input name="email" type="email" required autoComplete="email" placeholder="Email" defaultValue={inState?.email} className={input} />
          <PasswordInput name="password" autoComplete="current-password" placeholder="Password" />
          <ErrorNote s={inState} />
          <button disabled={signingIn} className={primary}>{signingIn ? "Signing in…" : "Sign in"}</button>
          <p className="text-center text-sm">
            <Link href="/signin/forgot" className="font-bold text-ink/60 underline hover:text-ink">Forgot password?</Link>
          </p>
        </form>
      ) : (
        <form action={signUp} className="space-y-3" key="up">
          <input type="hidden" name="next" value={next} />
          <input name="name" autoComplete="given-name" placeholder="First name (optional)" defaultValue={upState?.name} className={input} />
          <input name="email" type="email" required autoComplete="email" placeholder="Email" defaultValue={upState?.email} className={input} />
          <PasswordInput name="password" autoComplete="new-password" placeholder="Password (8+ characters)" />
          <ErrorNote s={upState} />
          <button disabled={signingUp} className={primary}>{signingUp ? "Creating your account…" : "Create account"}</button>
        </form>
      )}
    </div>
  );
}

export function ForgotForm() {
  const [s, send, sending] = useActionState(requestPasswordReset, null);
  if (s?.sent)
    return (
      <p className="rounded-2xl bg-sea/10 px-4 py-3 text-sm">
        If there&apos;s a Mapsie account for <b>{s.email}</b>, we&apos;ve emailed it a link to choose a new password. It works for an hour.
        Check your spam folder if it doesn&apos;t arrive in a few minutes.
      </p>
    );
  return (
    <form action={send} className="space-y-3">
      <input name="email" type="email" required autoComplete="email" placeholder="Email" defaultValue={s?.email} className={input} />
      <ErrorNote s={s} />
      <button disabled={sending} className={primary}>{sending ? "Sending…" : "Email me a link"}</button>
    </form>
  );
}

export function ResetForm({ token }: { token: string }) {
  const [s, save, saving] = useActionState(resetPassword, null);
  return (
    <form action={save} className="space-y-3">
      <input type="hidden" name="token" value={token} />
      <PasswordInput name="password" autoComplete="new-password" placeholder="New password (8+ characters)" />
      <ErrorNote s={s} />
      <button disabled={saving} className={primary}>{saving ? "Saving…" : "Save password and sign in"}</button>
    </form>
  );
}

export function ResendVerification() {
  const [s, resend, sending] = useActionState(resendVerification, null);
  if (s?.sent) return <span className="font-bold">Sent. Check your inbox.</span>;
  return (
    <form action={resend} className="inline">
      {s?.error ? <span className="font-bold">{s.error}</span> : <button disabled={sending} className="font-bold underline">{sending ? "Sending…" : "Send the link again"}</button>}
    </form>
  );
}
