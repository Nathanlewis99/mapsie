"use client";
import dynamic from "next/dynamic";

// The editor lives entirely in the browser (map + saved design in local storage).
const Editor = dynamic(() => import("@/components/editor/Editor"), { ssr: false });

export default function CreatePage() {
  return <Editor />;
}
