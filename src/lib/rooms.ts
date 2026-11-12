// Photo rooms for the "On the wall" preview.
//
// Each room is a straight-on photo of a wall (no perspective) with an empty
// space where the poster hangs. Put the image in /public/rooms/ and describe it:
//   cx         where the centre of the poster goes across the image (0–1)
//   by         where the poster's bottom edge sits (0–1 down the image), so bigger
//              prints rise higher up the wall, like a real picture hung above furniture.
//              (Or cy: where its centre goes, for rooms without furniture below.)
//   wallCm     how many centimetres of real wall the full image width shows
//              (e.g. a 140 cm sideboard spanning 50% of the image => wallCm = 280)
//   maxHeight  optional: the tallest the framed poster may be, as a fraction of image height
// The poster is drawn at true scale for its print size, so an A1 looks bigger than an A4.
import roomFiles from "./room-files.json";

/** Which room images are actually in /public/rooms (kept up to date by hand). */
const ROOM_FILES: string[] = roomFiles;

export interface Room {
  id: string;
  label: string;
  src: string;
  width: number; // image size in px
  height: number;
  cx: number;
  cy?: number;
  by?: number;
  wallCm: number;
  maxHeight?: number;
}

// Measured from the furniture in each image (both are 2000 x 1116 px):
//  bedroom: the 160 cm headboard spans x 497–1533 (1036 px), top at y 787; poster ~25 cm above it.
//  living:  the 160 cm sideboard spans x 557–1443 (886 px), top at y 787; poster ~25 cm above it.
// Add an entry once its image is in /public/rooms/.
const AVAILABLE: Room[] = [
  { id: "bedroom-sage", label: "Sage bedroom", src: "/rooms/bedroom-sage.jpg", width: 2000, height: 1116, cx: 0.5075, by: 0.56, wallCm: 309, maxHeight: 0.55 },
  { id: "living-oak", label: "Living room", src: "/rooms/living-oak.jpg", width: 2000, height: 1116, cx: 0.5, by: 0.58, wallCm: 361, maxHeight: 0.56 },
];

export const ROOMS: Room[] = AVAILABLE.filter((r) => ROOM_FILES.includes(r.src));
