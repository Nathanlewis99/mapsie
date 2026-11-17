// Search-engine content shared by the homepage, occasion pages and structured data.
import { COMPANY } from "./company";
import { DIGITAL_PRICE, FRAMES, PAPERS, PRODUCTS, SHIPPING, itemPrice } from "./products";

export const SITE = "https://mapsie.shop";

/** Real designs made in Mapsie, photographed as finished prints. */
export const EXAMPLES = [
  { slug: "southeast-asia", title: "Backpacking South East Asia", alt: "Framed travel map print of a backpacking route through Thailand, Laos, Vietnam and Cambodia with illustrated stickers, in a natural wood frame" },
  { slug: "sri-lanka", title: "Sri Lanka by tuk-tuk and train", alt: "Custom Sri Lanka map print with the Kandy to Ella train route, tuk-tuk legs and trip photos, in a black frame with a white mount" },
  { slug: "route-66", title: "Route 66 road trip", alt: "Vintage-style Route 66 road trip map poster from Chicago to Santa Monica, following the real roads" },
  { slug: "interrail-europe", title: "Interrailing Europe", alt: "Interrail map print of a rail journey across Europe through Paris, Munich, Prague and Vienna, in a natural wood frame" },
  { slug: "africa-safari", title: "Out of Africa safari", alt: "Dark midnight-style map print of a safari from Cape Town to Zanzibar with illustrated wildlife stickers" },
  { slug: "south-america", title: "South America adventure", alt: "Unframed South America travel map print on textured etching paper, from Peru to Patagonia" },
  { slug: "london", title: "A London pub crawl", alt: "Minimal London city map print of a pub crawl with beer stickers and a cheers note" },
  { slug: "your-photos", title: "Your own trip photos", alt: "Travel map print with the customer's own trip photos placed on the map as polaroids" },
] as const;

const gbp = (n: number) => `£${n}`;
const cheapest = Math.min(...PRODUCTS.map((p) => p.price.GB));
const framedFrom = Math.min(...PRODUCTS.map((p) => itemPrice({ productId: p.id, frame: "black", paper: "ema", mount: "none", glaze: "perspex" } as never, "GB")));
export const PRICE_RANGE = {
  low: Math.min(cheapest, DIGITAL_PRICE.GB),
  high: Math.max(...PRODUCTS.map((p) => itemPrice({ productId: p.id, frame: "black", paper: "ema", mount: "white", glaze: "perspex" } as never, "GB"))),
};

export const FAQ: { q: string; a: string }[] = [
  {
    q: "What sizes do your map prints come in?",
    a: `${PRODUCTS.map((p) => p.label).join(", ")}. Prints start at ${gbp(cheapest)} and framed prints at ${gbp(framedFrom)}, with free standard delivery. You can preview your map on a wall at real size before you order.`,
  },
  {
    q: "Can I get my map framed?",
    a: `Yes. Choose from ${FRAMES.filter((f) => f.id !== "none").length} wooden frame finishes, including black, white, natural oak, gold and silver, with an optional white mount. Frames come with shatterproof Perspex, ready to hang. Unframed prints come in a sturdy tube, on ${PAPERS.map((p) => p.label.toLowerCase()).join(", ").replace(/, ([^,]*)$/, " or $1")} paper.`,
  },
  {
    q: "How long does delivery take?",
    a: `Every print is made to order in a print lab near you (UK, US or Australia). Standard delivery is free and takes ${SHIPPING[0].detail}, plus 1 to 3 days to print (framed prints take a little longer). Express delivery is ${SHIPPING[1].detail}.`,
  },
  {
    q: "Can I add my own photos to the map?",
    a: "Yes. Upload photos from your trip and place them anywhere on the map, as polaroids, stamps, circles or hearts, with your own borders and filters.",
  },
  {
    q: "Is there a digital version?",
    a: `Yes. A full-resolution 300 dpi file of your map is ${gbp(DIGITAL_PRICE.GB)}, emailed within minutes, so you can print it anywhere. It's also a good last-minute gift.`,
  },
  {
    q: "Does it make a good gift?",
    a: "It's one of the most personal gifts you can give: a honeymoon, a first trip together, a gap year or a family road trip, with the dates and a message in the title. You can email yourself the design to finish later, and send it straight to them.",
  },
  {
    q: "Can I see exactly what I'll get before I pay?",
    a: "Yes. What you see in the designer is exactly what's printed, at 300 dpi. You'll see a final preview at checkout, and you have an hour after ordering to change your mind before it goes to print.",
  },
];

/** Structured data for the homepage: who we are, what we sell, and the FAQ. */
export function homeJsonLd() {
  return [
    {
      "@context": "https://schema.org",
      "@type": "Organization",
      name: COMPANY.brand,
      legalName: COMPANY.legalName,
      url: SITE,
      logo: `${SITE}/apple-icon.png`,
      email: COMPANY.supportEmail,
    },
    {
      "@context": "https://schema.org",
      "@type": "Product",
      name: "Custom travel map print",
      description: "A personalised map print of your trip: your stops, the route between them, stickers and photos, in your choice of style. Printed to order and delivered, framed or unframed.",
      brand: { "@type": "Brand", name: COMPANY.brand },
      image: EXAMPLES.slice(0, 4).map((e) => `${SITE}/examples/${e.slug}.webp`),
      offers: {
        "@type": "AggregateOffer",
        priceCurrency: "GBP",
        lowPrice: PRICE_RANGE.low,
        highPrice: PRICE_RANGE.high,
        availability: "https://schema.org/InStock",
        url: `${SITE}/create`,
      },
    },
    faqJsonLd(FAQ),
  ];
}

export const faqJsonLd = (items: { q: string; a: string }[]) => ({
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: items.map((f) => ({ "@type": "Question", name: f.q, acceptedAnswer: { "@type": "Answer", text: f.a } })),
});
