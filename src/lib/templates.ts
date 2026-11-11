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

export const TEMPLATES: TripTemplate[] = [
  {
    id: "asia",
    name: "Asia & Oz backpacking",
    emoji: "🎒",
    title: "The Big Trip",
    subtitle: "4 countries · 1 backpack",
    preset: "vintage",
    stickers: ["elephant-bath", "trek-tent", "scuba-turtle", "croc-eyes"],
    stops: [
      ["Colombo", 79.86, 6.93],
      ["Kathmandu", 85.32, 27.72, "plane"],
      ["Singapore", 103.82, 1.35, "plane"],
      ["Cairns", 145.77, -16.92, "plane"],
      ["Sydney", 151.21, -33.87, "plane"],
    ],
  },
  {
    id: "eastcoast",
    name: "East Coast Australia",
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
    id: "europe",
    name: "Europe by rail",
    emoji: "🚆",
    title: "Interrail Summer",
    subtitle: "8 cities · 1 pass",
    preset: "minimal",
    stickers: ["cafe-croissant", "castle-fairytale", "scenic-viaduct", "pizza-slice", "ruins-colosseum"],
    stops: [
      ["London", -0.13, 51.51],
      ["Paris", 2.35, 48.86, "train"],
      ["Amsterdam", 4.9, 52.37, "train"],
      ["Berlin", 13.4, 52.52, "train"],
      ["Prague", 14.42, 50.08, "train"],
      ["Vienna", 16.37, 48.21, "train"],
      ["Venice", 12.33, 45.44, "train"],
      ["Rome", 12.5, 41.9, "train"],
    ],
  },
  {
    id: "usa",
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
    id: "honeymoon",
    name: "Honeymoon",
    emoji: "💍",
    title: "Just Married",
    subtitle: "Our honeymoon",
    preset: "blush",
    stickers: ["proposal-ring", "honeymoon-champagne", "honeymoon-bungalow", "coco-straw", "sunset-palms"],
    stops: [
      ["Bali", 115.19, -8.65],
      ["Gili Islands", 116.04, -8.35, "boat"],
      ["Singapore", 103.82, 1.35, "plane"],
      ["Maldives", 73.51, 4.18, "plane"],
    ],
  },
];

export const templateStops = (t: TripTemplate): Omit<Stop, "id">[] =>
  t.stops.map(([name, lng, lat, mode]) => ({ name, lng, lat, showLabel: true, arriveBy: mode }));
