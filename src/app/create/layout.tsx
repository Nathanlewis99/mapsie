import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Design Your Map | Mapsie Map Maker",
  description: "Make your own travel map: add your stops, pick a style, add stickers and photos, and see it framed on a wall. Free to design.",
  alternates: { canonical: "/create" },
};

export default function CreateLayout({ children }: { children: React.ReactNode }) {
  return children;
}
