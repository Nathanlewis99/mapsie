"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

/** Re-check every few seconds until the payment webhook has made the card. */
export default function Refresh() {
  const router = useRouter();
  useEffect(() => {
    const t = setInterval(() => router.refresh(), 3000);
    return () => clearInterval(t);
  }, [router]);
  return <div className="mx-auto h-8 w-8 rounded-full border-4 border-coral/30 border-t-coral animate-spin" />;
}
