import type { Metadata } from "next";
import { Nunito } from "next/font/google";
import { fontVariables } from "@/lib/fonts";
import "./globals.css";

const ui = Nunito({ subsets: ["latin"], weight: ["400", "600", "700", "800"], variable: "--f-ui" });

export const metadata: Metadata = {
  title: "Mapsie — turn your trip into a print",
  description: "Design a custom map print of your journey: stops, routes, stickers and your style. Printed and delivered to your door.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${ui.variable} ${fontVariables} antialiased`}>{children}</body>
    </html>
  );
}
