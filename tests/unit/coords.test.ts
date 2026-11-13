import { describe, expect, it } from "vitest";
import { parseCoords } from "../../src/lib/geo";

const near = (r: { lat: number; lng: number } | null, lat: number, lng: number) => {
  expect(r).not.toBeNull();
  expect(r!.lat).toBeCloseTo(lat, 3);
  expect(r!.lng).toBeCloseTo(lng, 3);
};

describe("parseCoords", () => {
  it("reads decimal pairs", () => {
    near(parseCoords("5.9643, 80.7076"), 5.9643, 80.7076);
    near(parseCoords("5.9643 80.7076"), 5.9643, 80.7076);
    near(parseCoords("-33.8568, 151.2153"), -33.8568, 151.2153);
    near(parseCoords("lat 51.5 lng -0.12"), 51.5, -0.12);
  });
  it("reads hemispheres and degrees, minutes, seconds", () => {
    near(parseCoords("5.9643 N, 80.7076 E"), 5.9643, 80.7076);
    near(parseCoords("33.8568° S, 151.2153° E"), -33.8568, 151.2153);
    near(parseCoords(`5°57'51.4"N 80°42'27.4"E`), 5.96428, 80.70761);
    near(parseCoords(`40°41′21″N 74°2′40″W`), 40.68917, -74.04444);
    near(parseCoords("N 5 57.857 E 80 42.457"), 5.96428, 80.70762);
  });
  it("reads map links", () => {
    near(parseCoords("https://www.google.com/maps/place/Hiriketiya/@5.9643,80.7076,15z"), 5.9643, 80.7076);
    near(parseCoords("https://maps.google.com/?q=5.9643,80.7076"), 5.9643, 80.7076);
    near(parseCoords("https://www.openstreetmap.org/#map=16/5.9643/80.7076"), 5.9643, 80.7076);
  });
  it("ignores place names and impossible values", () => {
    expect(parseCoords("Hiriketiya beach")).toBeNull();
    expect(parseCoords("Route 66")).toBeNull();
    expect(parseCoords("95, 80")).toBeNull();
    expect(parseCoords("2026")).toBeNull();
  });
});
