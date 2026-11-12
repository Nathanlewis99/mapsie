import type { Metadata } from "next";
import "@fontsource-variable/nunito";
import "@fontsource-variable/playfair-display";
import "@fontsource-variable/caveat";
import "@fontsource-variable/montserrat";
import "@fontsource/pacifico";
import "@fontsource/bebas-neue";
import "@fontsource-variable/cormorant-garamond";
import "@fontsource-variable/josefin-sans";
import "@fontsource/abril-fatface";
import "@fontsource/courier-prime";
import "@fontsource/courier-prime/700.css";
import "@fontsource/great-vibes";
import "@fontsource/permanent-marker";
import "@fontsource/amatic-sc";
import "@fontsource/amatic-sc/700.css";
import "@fontsource/indie-flower";
import "@fontsource/patrick-hand";
import "@fontsource/kalam";
import "@fontsource/kalam/700.css";
import "@fontsource-variable/dancing-script";
import "@fontsource/satisfy";
import "@fontsource/lobster";
import "@fontsource/righteous";
import "@fontsource-variable/fredoka";
import "@fontsource/special-elite";
import "@fontsource/rock-salt";
import "./globals.css";
import ErrorReporter from "@/components/ErrorReporter";
import Analytics from "@/components/Analytics";

export const metadata: Metadata = {
  title: "Mapsie — turn your trip into a print",
  description: "Design a custom map print of your journey: stops, routes, stickers and your style. Printed and delivered to your door.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <ErrorReporter />
        <Analytics />
        {children}
      </body>
    </html>
  );
}
