// Photo rooms for the "On the wall" preview.
//
// Each room is a straight-on photo of a wall (no perspective) with an empty
// space where the poster hangs. Put the image in /public/rooms/ and describe it:
//   cx, cy     where the centre of the poster goes, as fractions of the image (0–1)
//   wallCm     how many centimetres of real wall the full image width shows
//              (e.g. a 140 cm sideboard spanning 50% of the image => wallCm = 280)
//   maxHeight  optional: the tallest the framed poster may be, as a fraction of image height
// The poster is drawn at true scale for its print size, so an A1 looks bigger than an A4.
export interface Room {
  id: string;
  label: string;
  src: string;
  width: number; // image size in px
  height: number;
  cx: number;
  cy: number;
  wallCm: number;
  maxHeight?: number;
}

export const ROOMS: Room[] = [];
