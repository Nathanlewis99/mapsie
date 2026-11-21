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
import "@fontsource/rye";
import "@fontsource/im-fell-english-sc";
import "@fontsource/unifrakturcook/700.css";
import "./globals.css";
import ErrorReporter from "@/components/ErrorReporter";
import Analytics from "@/components/Analytics";
import ConsentManager from "@/components/ConsentManager";

const DESCRIPTION = "Design a custom map print of your journey: stops, routes, stickers and your style. Printed and delivered to your door.";
export const metadata: Metadata = {
  metadataBase: new URL(process.env.APP_URL ?? "https://mapsie.shop"),
  title: "Mapsie — turn your trip into a print",
  description: DESCRIPTION,
  // The preview shown when someone shares a link (WhatsApp, Instagram, Facebook, X, iMessage).
  openGraph: {
    type: "website",
    siteName: "Mapsie",
    title: "Mapsie — turn your trip into a print",
    description: DESCRIPTION,
    url: "/",
    locale: "en_GB",
    images: [{ url: "/og.jpg", width: 1200, height: 630, alt: "Custom travel map prints made with Mapsie" }],
  },
  twitter: { card: "summary_large_image", title: "Mapsie — turn your trip into a print", description: DESCRIPTION, images: ["/og.jpg"] },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <ErrorReporter />
        <Analytics />
        {children}
        <ConsentManager />
      </body>
    </html>
  );
}
