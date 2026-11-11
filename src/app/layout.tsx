import type { Metadata } from "next";
import "@fontsource-variable/nunito";
import "@fontsource-variable/playfair-display";
import "@fontsource-variable/caveat";
import "@fontsource-variable/montserrat";
import "@fontsource/pacifico";
import "@fontsource/bebas-neue";
import "./globals.css";

export const metadata: Metadata = {
  title: "Mapsie — turn your trip into a print",
  description: "Design a custom map print of your journey: stops, routes, stickers and your style. Printed and delivered to your door.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
