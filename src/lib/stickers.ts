// Starter sticker pack: Twemoji artwork (CC-BY 4.0, credit shown in the footer).
const s = (name: string) => `/stickers/${name}.svg`;

export const STICKER_PACKS: { name: string; items: string[] }[] = [
  {
    name: "Adventures",
    items: ["diving-mask", "swimmer", "surfer", "canoe", "climber", "hiking-boot", "snowboarder", "yoga", "backpack", "tent", "camping", "camera", "compass", "sunglasses"].map(s),
  },
  {
    name: "Wildlife",
    items: ["crocodile", "kangaroo", "koala", "elephant", "tiger", "monkey", "turtle", "whale", "shark", "dolphin", "tropical-fish", "parrot"].map(s),
  },
  {
    name: "Places",
    items: ["palm-tree", "beach", "island", "snowy-mountain", "mountain", "volcano", "sunrise", "temple", "mosque", "castle", "tower", "world-map"].map(s),
  },
  {
    name: "Getting around",
    items: ["airplane", "departure", "sailboat", "ship", "train", "bus", "campervan", "car", "scooter", "bicycle"].map(s),
  },
  {
    name: "Food & fun",
    items: ["beer", "cocktail", "coconut", "coffee", "ramen", "sushi", "curry", "ice-cream", "sun", "rainbow", "heart", "star", "pin", "flag"].map(s),
  },
];
