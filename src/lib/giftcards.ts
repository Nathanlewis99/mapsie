// Gift card amounts per country, chosen to match what they buy (shipping is free).
import { DIGITAL_PRICE, itemPrice, type RegionId } from "./products";

const framedA3 = (r: RegionId) => itemPrice({ productId: "a3", frame: "black", paper: "ema", mount: "none", glaze: "perspex" } as never, r);
const framedA2 = (r: RegionId) => itemPrice({ productId: "a2", frame: "black", paper: "ema", mount: "white", glaze: "perspex" } as never, r);
const printA3 = (r: RegionId) => itemPrice({ productId: "a3", frame: "none", paper: "ema", mount: "none", glaze: "perspex" } as never, r);

export function giftAmounts(r: RegionId): { amount: number; covers: string }[] {
  return [
    { amount: DIGITAL_PRICE[r], covers: "a digital file of their map" },
    { amount: printA3(r), covers: "an A3 print, delivered" },
    { amount: framedA3(r), covers: "a framed A3 print, delivered" },
    { amount: framedA2(r), covers: "a framed A2 print with a mount" },
  ];
}
export const GIFT_MIN = 10;
export const GIFT_MAX = 250;
/** How long a gift card lasts. */
export const GIFT_VALID_YEARS = 2;
