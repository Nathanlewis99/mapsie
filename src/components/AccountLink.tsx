"use client";
import Link from "next/link";
import { useEffect, useState } from "react";

/** "Sign in" or "My maps", depending on whether someone is signed in. */
export default function AccountLink({ className = "" }: { className?: string }) {
  const [signedIn, setSignedIn] = useState<boolean | null>(null);
  useEffect(() => {
    fetch("/api/auth/me").then((r) => r.json()).then((j) => setSignedIn(!!j.user)).catch(() => setSignedIn(false));
  }, []);
  if (signedIn === null) return null;
  return (
    <Link href={signedIn ? "/account" : "/signin"} className={`font-extrabold text-ink/70 hover:text-ink ${className}`}>
      {signedIn ? "My maps" : "Sign in"}
    </Link>
  );
}
