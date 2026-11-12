import type { FeatureCollection, LineString } from "geojson";

// Hand-drawn cartographic extras: ocean currents, shipping lanes and the
// lat/long grid. Coordinates are [lng, lat]. Lines that cross the Pacific
// carry on past ±180 so they don't wrap the wrong way round the globe.
// Point order is the direction of flow (arrows follow it).

type Line = { name: string; kind?: string; coords: [number, number][] };

const fc = (lines: Line[]): FeatureCollection<LineString> => ({
  type: "FeatureCollection",
  features: lines.map((l) => ({ type: "Feature", properties: { name: l.name, kind: l.kind ?? "" }, geometry: { type: "LineString", coordinates: l.coords } })),
});

const CURRENTS: Line[] = [
  // warm
  { name: "Gulf Stream", kind: "warm", coords: [[-80.5, 25.5], [-80, 28], [-79, 31], [-75.5, 35], [-72, 37.5], [-65, 39.5], [-55, 41], [-45, 43]] },
  { name: "North Atlantic Drift", kind: "warm", coords: [[-43, 44], [-35, 47], [-25, 51], [-15, 55], [-8, 58.5], [0, 62], [8, 66], [14, 70]] },
  { name: "Kuroshio", kind: "warm", coords: [[123, 22], [125, 25.5], [129, 29], [133, 32.5], [138, 34.5], [142, 36.5], [148, 38.5], [155, 40]] },
  { name: "North Pacific Current", kind: "warm", coords: [[158, 41], [170, 42.5], [185, 43.5], [200, 43.5], [215, 43], [225, 44]] },
  { name: "Brazil Current", kind: "warm", coords: [[-35, -8], [-37, -14], [-39, -20], [-42, -24], [-46, -28], [-50, -34], [-53, -38]] },
  { name: "Agulhas Current", kind: "warm", coords: [[41, -14], [39, -20], [35.5, -26], [32, -30], [28, -33.5], [23, -36], [19, -38]] },
  { name: "East Australian Current", kind: "warm", coords: [[154, -15], [154.5, -22], [154, -28], [153.8, -32], [153.5, -36], [155, -40]] },
  { name: "North Equatorial Current", kind: "warm", coords: [[-18, 15], [-30, 14], [-45, 14], [-58, 15]] },
  { name: "South Equatorial Current", kind: "warm", coords: [[8, -2], [-5, -3], [-20, -4], [-33, -5]] },
  { name: "North Equatorial Current", kind: "warm", coords: [[-110, 13], [-140, 13], [-170, 14], [-200, 15], [-225, 16]] },
  { name: "South Equatorial Current", kind: "warm", coords: [[-85, -3], [-110, -4], [-140, -6], [-170, -8], [-195, -11]] },
  { name: "South Equatorial Current", kind: "warm", coords: [[110, -12], [95, -13], [80, -14], [65, -15], [52, -14]] },
  // cold
  { name: "California Current", kind: "cold", coords: [[-130, 48], [-127, 42], [-123, 36], [-119, 30], [-115, 24]] },
  { name: "Humboldt Current", kind: "cold", coords: [[-76, -45], [-75, -38], [-73.5, -30], [-73, -22], [-77, -14], [-82, -6]] },
  { name: "Benguela Current", kind: "cold", coords: [[16, -34], [14, -28], [12, -22], [10, -16], [8, -10]] },
  { name: "Canary Current", kind: "cold", coords: [[-12, 42], [-13, 36], [-15, 30], [-17.5, 24], [-19, 18]] },
  { name: "Labrador Current", kind: "cold", coords: [[-60, 62], [-57, 57], [-53, 52], [-51, 47], [-50, 44]] },
  { name: "Oyashio", kind: "cold", coords: [[160, 53], [154, 48], [148, 44], [145, 40.5]] },
  { name: "West Australian Current", kind: "cold", coords: [[112, -36], [111, -30], [110.5, -25], [110, -20]] },
  { name: "East Greenland Current", kind: "cold", coords: [[-12, 79], [-18, 73], [-27, 67], [-36, 63], [-43, 60]] },
  { name: "Falkland Current", kind: "cold", coords: [[-66, -56], [-61, -51], [-57.5, -45], [-56, -39]] },
  { name: "Antarctic Circumpolar Current", kind: "cold", coords: [[-180, -60], [-150, -61], [-120, -60], [-90, -59], [-70, -59], [-55, -55], [-35, -51], [-10, -49], [20, -47], [50, -47], [80, -48], [110, -50], [140, -53], [165, -57], [180, -60]] },
];

const LANES: Line[] = [
  { name: "Europe – Asia via Suez", coords: [[4, 52], [1.5, 51], [-5, 49], [-9.5, 44], [-9.8, 37.5], [-6.5, 36], [-5.4, 35.95], [-1, 36.6], [5, 37.6], [10.5, 37.8], [12.5, 37], [20, 34], [27, 32.6], [32.3, 31.4], [32.55, 30.2], [32.6, 29.8], [33.4, 28], [35, 26], [38, 21.5], [41.5, 16], [43.4, 12.7], [45.5, 12], [52, 13], [60, 11], [72, 7], [80.5, 5.6], [88, 5.8], [95, 6], [98, 5], [101, 2.6], [103.8, 1.2], [104.6, 1.6], [107, 4], [110, 8], [113, 15], [114.5, 22]] },
  { name: "Hong Kong – Shanghai – Tokyo", coords: [[114.5, 22], [118.5, 24], [122.5, 29.5], [123, 31], [127, 32], [131, 33], [135, 33.3], [139.8, 34.9]] },
  { name: "Transatlantic", coords: [[-5, 49], [-20, 48.5], [-35, 47], [-50, 43.5], [-62, 41.5], [-70, 40.6], [-74, 40.4]] },
  { name: "Panama route", coords: [[-74, 40.4], [-74.5, 35], [-73.5, 27], [-74.5, 21], [-77, 15], [-79.6, 9.4], [-79.6, 8.8], [-83, 7], [-92, 11], [-105, 17], [-114, 25], [-118.2, 33.7]] },
  { name: "Transpacific", coords: [[-122.5, 37.7], [-135, 42], [-150, 46], [-165, 48], [-180, 48], [-195, 46], [-210, 41], [-220.2, 35]] },
  { name: "Cape of Good Hope route", coords: [[-9.8, 37.5], [-14, 30], [-18, 20], [-17, 10], [-8, 0], [2, -12], [12, -26], [18.4, -35], [25, -36.2], [40, -32], [55, -22], [68, -8], [76, 2], [80.5, 5.6]] },
  { name: "Singapore – Sydney", coords: [[104.6, 1.6], [107, -2.5], [112, -6], [116, -8.8], [120, -12], [116, -20], [113.5, -28], [115, -35.2], [125, -36], [135, -37], [145, -39.7], [150.5, -37.5], [151.4, -33.9]] },
  { name: "Gulf – Asia", coords: [[50.5, 26.5], [55, 26.2], [56.6, 26.4], [58, 24], [62, 20], [70, 12], [76, 7.5], [80.5, 5.6]] },
  { name: "Cape Horn", coords: [[-53, -38], [-58, -46], [-63, -54], [-67, -56.3], [-73, -54], [-76, -46], [-73.5, -36]] },
];

export const currents = fc(CURRENTS);
export const shippingLanes = fc(LANES);

const meridian = (lng: number): [number, number][] => [[lng, -85], [lng, 85]];
const parallel = (lat: number): [number, number][] => Array.from({ length: 13 }, (_, i) => [-540 + i * 90, lat] as [number, number]);

/** Lat/long grid every 15°, drawn across three world copies so it never ends at the antimeridian. */
export const graticule = fc([
  ...Array.from({ length: 72 }, (_, i) => ({ name: "", coords: meridian(-540 + i * 15) })),
  ...[-75, -60, -45, -30, -15, 0, 15, 30, 45, 60, 75].map((lat) => ({ name: "", coords: parallel(lat) })),
]);

/** Equator, tropics and polar circles. */
export const specialLatitudes = fc([
  { name: "Arctic Circle", coords: parallel(66.56) },
  { name: "Tropic of Cancer", coords: parallel(23.44) },
  { name: "Equator", coords: parallel(0) },
  { name: "Tropic of Capricorn", coords: parallel(-23.44) },
  { name: "Antarctic Circle", coords: parallel(-66.56) },
]);
