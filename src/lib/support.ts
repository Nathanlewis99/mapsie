// Reasons a customer can choose on the support form, with what we tell them up front.
// Shared by the form (browser) and the server. Wording follows the refund policy.
export type SupportReason = "not_arrived" | "damaged" | "quality" | "wrong" | "unhappy" | "change" | "address" | "other";

export const REASONS: { id: SupportReason; label: string; hint: string; photos: "required" | "optional" | "none" }[] = [
  {
    id: "not_arrived",
    label: "My order hasn't arrived",
    hint: "Prints are made to order, then delivered: usually 3–5 working days for standard delivery after printing. If it's past that, tell us and we'll chase the courier. If it's lost, we'll send a free reprint or refund you.",
    photos: "none",
  },
  {
    id: "damaged",
    label: "It arrived damaged",
    hint: "Sorry about that! Please add a photo of the damage (and the packaging, if it was damaged in transit). We'll send a free reprint or a full refund, your choice. Please keep the print until we've sorted it.",
    photos: "required",
  },
  {
    id: "quality",
    label: "There's a problem with the print quality",
    hint: "For example streaks, smudges, missing areas or a misaligned print. Please add a clear photo. If it's a printing fault, we'll reprint it free or refund you.",
    photos: "required",
  },
  {
    id: "wrong",
    label: "It's not what I designed or ordered",
    hint: "Wrong design, size, frame or orientation, or something missing compared with your final preview. Please add a photo and we'll put it right.",
    photos: "required",
  },
  {
    id: "unhappy",
    label: "I'm not happy with it",
    hint: "Tell us what's wrong and we'll do our best to help. Because every print is personalised, we can't offer refunds for a change of mind or for mistakes in the submitted design, but faulty or damaged prints are always put right.",
    photos: "optional",
  },
  {
    id: "change",
    label: "Change or cancel my order",
    hint: "You can cancel (or, for Etsy orders, change your design) within 1 hour of ordering, from your order page. After that it's with our printer and can't be changed, but tell us and we'll check.",
    photos: "none",
  },
  {
    id: "address",
    label: "Delivery address problem",
    hint: "If your order hasn't gone to print yet we may be able to change the address. Tell us the correct one below.",
    photos: "none",
  },
  { id: "other", label: "Something else", hint: "Ask us anything: we usually reply within one working day.", photos: "optional" },
];
export const reasonFor = (id: string) => REASONS.find((r) => r.id === id) ?? REASONS[REASONS.length - 1];

export const MAX_PHOTOS = 4;
/** Photos are shrunk in the browser to this many pixels on the long side before upload. */
export const PHOTO_MAX_PX = 1800;
/** After shrinking, about 1 MB as base64 is plenty for a 1800 px JPEG. */
export const PHOTO_MAX_CHARS = 1_600_000;
