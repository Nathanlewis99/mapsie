// Sticker library: Twemoji artwork (CC-BY 4.0, credit shown in the footer).
const s = (name: string) => `/stickers/${name}.svg`;

export const STICKER_PACKS: { name: string; items: string[] }[] = [
  {
    name: "Adventures",
    items: ["diving-mask", "swimmer", "surfer", "canoe", "climber", "hiking-boot", "skier", "snowboarder", "parachute", "yoga", "backpack", "tent", "camping", "camera", "camera-flash", "compass", "sunglasses", "motorbike"].map(s),
  },
  {
    name: "Wildlife",
    items: ["crocodile", "kangaroo", "koala", "elephant", "tiger", "lion", "giraffe", "zebra", "panda", "monkey", "penguin", "flamingo", "camel", "parrot", "turtle", "whale", "shark", "dolphin", "octopus", "crab", "tropical-fish"].map(s),
  },
  {
    name: "Places",
    items: ["palm-tree", "beach", "island", "desert", "cactus", "hibiscus", "snowy-mountain", "mountain", "volcano", "sunrise", "temple", "shrine", "mosque", "castle", "classical-building", "tower", "statue-of-liberty", "moai", "ferris-wheel", "world-map"].map(s),
  },
  {
    name: "Getting around",
    items: ["airplane", "departure", "helicopter", "sailboat", "ship", "train", "bus", "campervan", "car", "scooter", "bicycle", "walking"].map(s),
  },
  {
    name: "Food & drink",
    items: ["beer", "wine", "cocktail", "cheers", "coconut", "coffee", "ramen", "sushi", "curry", "pizza", "taco", "croissant", "ice-cream"].map(s),
  },
  {
    name: "Moments",
    items: ["heart", "ring", "wedding", "party", "star", "sun", "rainbow", "pin", "flag"].map(s),
  },
];
