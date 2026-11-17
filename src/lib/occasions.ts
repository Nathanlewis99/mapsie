// Landing pages for the trips and occasions people search for (/maps/<slug>). Each
// starts the designer from a matching quick-start trip, or with "Describe your trip"
// filled in.
export interface Occasion {
  slug: string;
  nav: string; // short name for links
  metaTitle: string; // under ~60 characters
  description: string; // under ~155 characters
  h1: string;
  intro: string[];
  ideasTitle: string;
  ideas: string[];
  example: string; // EXAMPLES slug
  start: { template: string } | { describe: string };
  startLabel: string;
  gift?: boolean;
}

export const OCCASIONS: Occasion[] = [
  {
    slug: "honeymoon-map-print",
    nav: "Honeymoon maps",
    metaTitle: "Honeymoon Map Print, Personalised · Mapsie",
    description: "Turn your honeymoon into a personalised map print: every stop, the route you took, your photos and your wedding date. Framed and delivered.",
    h1: "A honeymoon map print, made from your trip",
    intro: [
      "Your honeymoon deserves more than a folder of photos on a phone. Add the places you stayed, and Mapsie draws the route between them: the flight out, the train along the coast, the boat to the island.",
      "Add stickers of the things you did, pin your own photos where they were taken, and put your names and wedding date in the title. Then choose a style that suits your home, from soft blush to classic vintage.",
    ],
    ideasTitle: "Ideas for your honeymoon map",
    ideas: [
      "Your names and wedding date as the title, with “Just married” or a favourite line underneath",
      "Photos from your favourite moments, placed right where they happened",
      "A heart sticker on the place you got engaged, or where you'll go back to",
      "The Blush style for something soft and romantic, or Vintage for a timeless look",
    ],
    example: "sri-lanka",
    start: { template: "honeymoon" },
    startLabel: "Start with a honeymoon map",
    gift: true,
  },
  {
    slug: "road-trip-map-poster",
    nav: "Road trip maps",
    metaTitle: "Road Trip Map Poster, Custom Route Print · Mapsie",
    description: "Make a custom road trip map poster that follows the real roads you drove, with every stop, stickers and photos. Printed, framed and delivered.",
    h1: "A road trip map poster that follows the roads you drove",
    intro: [
      "Most map prints draw a straight line between stops. Mapsie follows the actual roads, so your print shows the coast road, the mountain pass and every detour you took.",
      "Add as many stops as you like, mark the car, campervan or motorbike legs, and drop in stickers for the diners, national parks and beaches along the way. Route 66, the Pacific Coast Highway, the NC500 or the Great Ocean Road: if you drove it, you can print it.",
    ],
    ideasTitle: "Ideas for your road trip map",
    ideas: [
      "The trip's mileage or number of days in the subtitle",
      "Campervan, car or motorbike icons on each leg",
      "Stickers for the national parks, diners and viewpoints you stopped at",
      "The Vintage or Explorer style for a classic road-atlas feel",
    ],
    example: "route-66",
    start: { template: "usa" },
    startLabel: "Start with a road trip",
  },
  {
    slug: "backpacking-travel-map",
    nav: "Backpacking & gap year maps",
    metaTitle: "Backpacking & Gap Year Travel Map Print · Mapsie",
    description: "A personalised travel map of your backpacking trip or gap year: every country, flight, bus and boat, with stickers and photos. Printed and delivered.",
    h1: "Your backpacking trip or gap year, on one map",
    intro: [
      "Months on the road, a dozen countries and more night buses than you'd like to remember. A Mapsie print puts it all on one map: the flights arcing between continents, the buses and boats in between, and every stop along the way.",
      "Light up the countries you visited, add stickers for the scuba dives, temples and treks, and pin your own photos where they were taken. It's the souvenir that doesn't fit in a backpack, delivered to your door when you're home.",
    ],
    ideasTitle: "Ideas for your backpacking map",
    ideas: [
      "“Three months · five countries · one backpack” style subtitles",
      "Different lines for flights, buses, boats and trains",
      "Every country you visited highlighted",
      "The Explorer or Tropical style for a sense of adventure",
    ],
    example: "southeast-asia",
    start: { template: "asia" },
    startLabel: "Start with a backpacking trip",
  },
  {
    slug: "interrail-map-print",
    nav: "Interrail maps",
    metaTitle: "Interrail Map Print, Your Rail Journey · Mapsie",
    description: "Make a personalised Interrail map print of your rail journey across Europe: every city, every train, stickers and photos. Printed and delivered.",
    h1: "An Interrail map of your journey across Europe",
    intro: [
      "Paris to Prague, Berlin to Budapest, an overnight train you'll never forget: an Interrail trip is made of the journeys between cities as much as the cities themselves.",
      "Add your stops in order and mark each leg as a train. Mapsie draws the rail lines, labels every city, and lets you add stickers for the landmarks you saw. Add the summer and the number of countries to the title, and it's ready to hang.",
    ],
    ideasTitle: "Ideas for your Interrail map",
    ideas: [
      "“Summer 2025 · 8 cities · 1 rail pass” as the subtitle",
      "Landmark stickers like the Eiffel Tower, Charles Bridge or Colosseum",
      "A note on the station where you nearly missed the train",
      "The Vintage style for a classic railway-poster look",
    ],
    example: "interrail-europe",
    start: { template: "europe" },
    startLabel: "Start with a rail trip",
  },
  {
    slug: "anniversary-map-gift",
    nav: "Anniversary gifts",
    metaTitle: "Anniversary Map Gift: Places You've Been · Mapsie",
    description: "A personalised anniversary gift: a map of the places you've been together, from your first date to your latest adventure. Framed and delivered.",
    h1: "An anniversary gift of the places you've been together",
    intro: [
      "Where you met, your first holiday, the city where you got engaged, the place you live now. A Mapsie print turns your story together into a map, with a stop for every chapter.",
      "Add a note to each place, your own photos and the date you met, then choose a frame. It's ready to hang the day it arrives, and it's a gift that really couldn't be anyone else's.",
    ],
    ideasTitle: "Ideas for an anniversary map",
    ideas: [
      "Your story in order: where you met, first trip, engagement, wedding, home",
      "A short note on each stop, like “our first date” or “where you said yes”",
      "Your photos from each place",
      "Paper (1st) or cotton (2nd) anniversary? Choose matte art or cotton rag paper",
    ],
    example: "your-photos",
    start: { describe: "Our story together: we met in London, had our first holiday in Barcelona, got engaged in Paris and now live in Bristol" },
    startLabel: "Describe your story",
    gift: true,
  },
  {
    slug: "christmas-travel-map-gift",
    nav: "Christmas gifts",
    metaTitle: "Personalised Travel Map Christmas Gift · Mapsie",
    description: "A personalised Christmas gift for travellers: a custom map print of their favourite trip, framed and delivered, or a digital file in minutes.",
    h1: "A Christmas gift for the traveller who has everything",
    intro: [
      "Socks and candles are easy to forget. A map of their favourite trip, with the route, stickers of what they did and their own photos, goes on the wall and stays there.",
      "Design it in a few minutes, choose a frame, and we'll print it near them and deliver it. Left it late? The digital file is emailed within minutes, ready to print or give as a card.",
    ],
    ideasTitle: "Gift ideas",
    ideas: [
      "Their gap year, honeymoon or a family road trip",
      "Every country they've ever visited, lit up on one map",
      "Their hometown or a favourite city, with the places that matter",
      "Too late for delivery? Give the digital file and print it later",
    ],
    example: "africa-safari",
    start: { describe: "" },
    startLabel: "Design their map",
    gift: true,
  },
];

export const getOccasion = (slug: string) => OCCASIONS.find((o) => o.slug === slug);

/** Where each occasion's main button goes in the designer. */
export const occasionStartUrl = (o: Occasion) =>
  "template" in o.start ? `/create?template=${o.start.template}` : o.start.describe ? `/create?describe=${encodeURIComponent(o.start.describe)}` : "/create?new=1";
