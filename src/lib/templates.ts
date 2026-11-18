import type { Stop, TravelMode } from "./types";

// Quick-start trips. Coordinates are rounded city centres.
type T = [name: string, lng: number, lat: number, mode?: TravelMode];

export interface TripTemplate {
  id: string;
  name: string;
  emoji: string;
  title: string;
  subtitle: string;
  preset: string;
  stickers: string[]; // Mapsie Originals concept ids
  stops: T[];
}

// Popular real-world routes people actually take, to start from and then edit.
export const TEMPLATES: TripTemplate[] = [
  {
    id: "se-asia",
    name: "South East Asia backpacking",
    emoji: "🎒",
    title: "Backpacking South East Asia",
    subtitle: "Thailand · Laos · Vietnam · Cambodia",
    preset: "tropical",
    stickers: ["tuktuk-temple", "longtail-karsts", "elephant-bath", "lantern-river", "temple-stupa"],
    stops: [
      ["Bangkok", 100.5, 13.76],
      ["Chiang Mai", 98.99, 18.79, "train"],
      ["Luang Prabang", 102.13, 19.89, "boat"],
      ["Hanoi", 105.83, 21.03, "plane"],
      ["Ha Long Bay", 107.08, 20.91, "bus"],
      ["Hoi An", 108.34, 15.88, "train"],
      ["Ho Chi Minh City", 106.63, 10.82, "bus"],
      ["Siem Reap", 103.86, 13.36, "bus"],
      ["Koh Phangan", 100.01, 9.73, "plane"],
    ],
  },
  {
    id: "east-coast",
    name: "Australia East Coast",
    emoji: "🦘",
    title: "East Coast Road Trip",
    subtitle: "Sydney to Cairns",
    preset: "tropical",
    stickers: ["surf-boards", "koala-tree", "scuba-diver", "croc-sign", "road-campervan"],
    stops: [
      ["Sydney", 151.21, -33.87],
      ["Byron Bay", 153.61, -28.64, "car"],
      ["Brisbane", 153.03, -27.47, "car"],
      ["Noosa", 153.09, -26.39, "car"],
      ["K'gari", 153.13, -25.25, "boat"],
      ["Airlie Beach", 148.72, -20.27, "car"],
      ["Cairns", 145.77, -16.92, "car"],
    ],
  },
  {
    id: "route-66",
    name: "Route 66",
    emoji: "🛣️",
    title: "Route 66",
    subtitle: "Chicago to Santa Monica",
    preset: "vintage",
    stickers: ["moto-open-road", "lm-grandcanyon-sunset", "lm-monumentvalley-road", "road-campervan"],
    stops: [
      ["Chicago", -87.63, 41.88],
      ["St. Louis", -90.2, 38.63, "car"],
      ["Tulsa", -95.99, 36.15, "car"],
      ["Amarillo", -101.83, 35.22, "car"],
      ["Santa Fe", -105.94, 35.69, "car"],
      ["Flagstaff", -111.65, 35.2, "car"],
      ["Grand Canyon", -112.11, 36.05, "car"],
      ["Las Vegas", -115.14, 36.17, "car"],
      ["Santa Monica", -118.49, 34.02, "car"],
    ],
  },
  {
    id: "south-america",
    name: "South America backpacking",
    emoji: "🦙",
    title: "South America",
    subtitle: "Peru to Patagonia",
    preset: "explorer",
    stickers: ["lm-machupicchu-terraces", "trek-llama", "condor-andes", "lm-iguazu-toucan"],
    stops: [
      ["Lima", -77.04, -12.05],
      ["Cusco", -71.97, -13.53, "bus"],
      ["Machu Picchu", -72.55, -13.16, "train"],
      ["Lake Titicaca", -70.02, -15.84, "bus"],
      ["La Paz", -68.12, -16.49, "bus"],
      ["Salar de Uyuni", -67.49, -20.13, "car"],
      ["Torres del Paine", -73.0, -51.0, "plane"],
      ["Buenos Aires", -58.38, -34.6, "plane"],
      ["Iguazu Falls", -54.44, -25.7, "bus"],
      ["Rio de Janeiro", -43.17, -22.91, "plane"],
    ],
  },
  {
    id: "interrail",
    name: "Europe Interrail",
    emoji: "🚆",
    title: "Interrail Summer",
    subtitle: "8 cities · 1 rail pass",
    preset: "vintage",
    stickers: ["castle-fairytale", "basic-beer", "gondola-gondolier", "ruins-colosseum", "bridge-stone"],
    stops: [
      ["Amsterdam", 4.9, 52.37],
      ["Berlin", 13.4, 52.52, "train"],
      ["Prague", 14.42, 50.08, "train"],
      ["Vienna", 16.37, 48.21, "train"],
      ["Budapest", 19.04, 47.5, "train"],
      ["Venice", 12.32, 45.44, "train"],
      ["Florence", 11.26, 43.77, "train"],
      ["Rome", 12.5, 41.9, "train"],
    ],
  },
  {
    id: "us-west",
    name: "US West Coast",
    emoji: "🌵",
    title: "Westward",
    subtitle: "A Californian road trip",
    preset: "blush",
    stickers: ["road-convertible", "surf-van", "themepark-ferris", "sunset-dunes"],
    stops: [
      ["San Francisco", -122.42, 37.77],
      ["Yosemite", -119.54, 37.75, "car"],
      ["Las Vegas", -115.14, 36.17, "car"],
      ["Grand Canyon", -112.11, 36.06, "car"],
      ["Los Angeles", -118.24, 34.05, "car"],
      ["San Diego", -117.16, 32.72, "car"],
    ],
  },
  {
    id: "new-zealand",
    name: "New Zealand road trip",
    emoji: "🏔️",
    title: "Aotearoa",
    subtitle: "A New Zealand road trip",
    preset: "terrain",
    stickers: ["bungee-bridge", "kayak-fjord", "glacier-valley", "road-campervan", "basic-mountain"],
    stops: [
      ["Auckland", 174.76, -36.85],
      ["Rotorua", 176.25, -38.14, "car"],
      ["Taupō", 176.07, -38.69, "car"],
      ["Wellington", 174.78, -41.29, "car"],
      ["Picton", 174.0, -41.29, "boat"],
      ["Kaikōura", 173.68, -42.4, "car"],
      ["Franz Josef", 170.18, -43.39, "car"],
      ["Wānaka", 169.13, -44.7, "car"],
      ["Queenstown", 168.66, -45.03, "car"],
      ["Milford Sound", 167.93, -44.67, "car"],
    ],
  },
  {
    id: "japan",
    name: "Japan Golden Route",
    emoji: "🗻",
    title: "Japan",
    subtitle: "Tokyo to Hiroshima by bullet train",
    preset: "minimal",
    stickers: ["sakura-fuji", "train-bullet", "temple-torii", "ramen-bowl", "sushi-nigiri"],
    stops: [
      ["Tokyo", 139.69, 35.69],
      ["Hakone", 139.02, 35.23, "train"],
      ["Kyoto", 135.77, 35.01, "train"],
      ["Nara", 135.8, 34.69, "train"],
      ["Osaka", 135.5, 34.69, "train"],
      ["Hiroshima", 132.46, 34.39, "train"],
      ["Miyajima", 132.32, 34.3, "boat"],
    ],
  },
];

export const templateStops = (t: TripTemplate): Omit<Stop, "id">[] =>
  t.stops.map(([name, lng, lat, mode]) => ({ name, lng, lat, showLabel: true, arriveBy: mode }));
