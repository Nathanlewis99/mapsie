// The steps of the buying funnel, in order. Shared by the browser tracker and the admin page.
export const FUNNEL = [
  { id: "visit", label: "Visited the site" },
  { id: "editor_open", label: "Opened the editor" },
  { id: "stop_added", label: "Added a stop" },
  { id: "customised", label: "Changed the style, text or stickers" },
  { id: "order_click", label: "Pressed Order" },
  { id: "checkout_view", label: "Saw checkout" },
  { id: "pay_click", label: "Pressed Pay" },
  { id: "paid", label: "Paid" },
] as const;

export type FunnelStep = (typeof FUNNEL)[number]["id"];
/** Other events worth counting. */
export const EXTRA_EVENTS = [
  "search", "saved_design", "shared", "signed_in", "order_cancelled", "wall_preview", "lock_framing", "ai_create", "ai_mic",
  // Why people leave: the start card, the save-your-map offer, and how long they stayed and how far they got.
  "start_card", "save_offer_shown", "save_offer_saved", "save_offer_closed", "fullscreen", "leave", "checkout_leave",
] as const;
export type TrackEvent = FunnelStep | (typeof EXTRA_EVENTS)[number];
