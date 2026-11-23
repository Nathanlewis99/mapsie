// The Reels: one per trip (plus hook variants for ads). Hooks were scored with the ig-reel skill's
// hookscore.py; captions live in scripts/social/posts.json when they're scheduled.
export interface ReelConfig {
  id: string;
  slug: string; // design/video/public/maps/<slug>{-base,-full}.jpg, <slug>.json and rooms/<slug>.jpg
  hook: string;
  accent: string; // the design's route colour, so the drawn line matches the finished poster
  routeWidth: number; // design.route.width
  roomLine: string;
  price: string;
}

export const REELS: ReelConfig[] = [
  { id: "NC500", slug: "touring-nc500", hook: "You drove 516 miles of the NC500. Where's the proof?", accent: "#2b4f86", routeWidth: 0.7, roomLine: "Framed, and on your wall in days", price: "Prints from £34 · free UK delivery" },
  { id: "NC500Ad", slug: "touring-nc500", hook: "Nobody prints their holiday photos. Print the route instead.", accent: "#2b4f86", routeWidth: 0.7, roomLine: "Your trip, framed and delivered", price: "Prints from £34 · free UK delivery" },
  { id: "Route66", slug: "route-66", hook: "Every mile of Route 66. On your wall.", accent: "#b5452b", routeWidth: 0.55, roomLine: "Printed and framed, ready to hang", price: "Prints from $45 · free US shipping" },
  { id: "Interrail", slug: "interrail-europe", hook: "8 cities, 1 rail pass, 1 map on your wall", accent: "#d0507a", routeWidth: 0.5, roomLine: "Every train, every stop, framed", price: "Prints from £34 · free UK delivery" },
];
