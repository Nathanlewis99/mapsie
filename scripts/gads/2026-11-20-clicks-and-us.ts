// Google Ads changes approved by the owner on 20 Nov 2026:
//  1. UK campaign: bid for clicks (max £0.80 a click) until there are conversions to learn from,
//     and add broader phrase keywords that people actually search for.
//  2. A separate US search campaign (£5/day): US spellings, $ prices, the US Christmas date,
//     and links that open the site in US dollars (?region=US).
// Run as a Render job:  npx -y tsx@4.20.3 scripts/gads/2026-11-20-clicks-and-us.ts [--check]
// --check asks Google to validate everything without changing anything. All-or-nothing.
import { gadsConfig, gadsMutateAll, gadsSearch } from "../../src/lib/server/googleAds";

const check = process.argv.includes("--check");
const cid = gadsConfig().customerId;
const UK_CAMPAIGN = `customers/${cid}/campaigns/24493494206`;
const UK_CUSTOM_GROUP = `customers/${cid}/adGroups/207946135571`;
const tmp = (kind: string, n: number) => `customers/${cid}/${kind}/-${n}`;

const UK_NEW_KEYWORDS = ["personalised map print", "custom map print", "travel map print", "personalised travel gift", "map gift", "travel poster personalised", "personalised map"];

const NEGATIVES: [string, "BROAD" | "PHRASE"][] = [
  ["jobs", "BROAD"], ["cheap", "BROAD"], ["template", "BROAD"], ["diy", "BROAD"], ["vector", "BROAD"], ["download free", "BROAD"], ["svg", "BROAD"],
  ["free download", "PHRASE"], ["free template", "PHRASE"], ["free printable", "PHRASE"], ["scratch map", "BROAD"], ["printable map", "PHRASE"],
];

const US = "?region=US";
const GROUPS: { name: string; url: string; keywords: string[]; headlines: string[]; descriptions: string[] }[] = [
  {
    name: "honeymoon map gift",
    url: `https://mapsie.shop/maps/honeymoon-map-print${US}`,
    keywords: ["honeymoon gift", "anniversary map gift", "wedding map print", "honeymoon map print", "personalized honeymoon gift"],
    headlines: ["Honeymoon Map Prints", "Your Honeymoon, Framed", "Personalized Anniversary Gift", "Add Your Wedding Date", "Pin Your Honeymoon Photos", "Every Stop of Your Trip", "Prints From $45", "Free Shipping", "Framed and Ready to Hang", "A Gift With Your Story", "Design It in Minutes", "Printed in the USA", "Order by Dec 12 for Christmas", "Paper or Cotton Anniversary", "Mapsie Honeymoon Maps"],
    descriptions: [
      "Turn your honeymoon into a map print: every stop, the route and your own photos.",
      "Add your names, wedding date and a message. Framed in wood, shipped free.",
      "A personal wedding or anniversary gift. Preview it on a wall before you order.",
      "Matte art or cotton rag paper for paper and cotton anniversaries. From $45.",
    ],
  },
  {
    name: "travel map gift card",
    url: `https://mapsie.shop/gift${US}`,
    keywords: ["travel map gift", "travel gift card", "gift for travelers", "last minute travel gift", "map gift card"],
    headlines: ["Travel Map Gift Cards", "They Design Their Own Map", "Emailed Instantly", "Send on Christmas Morning", "Gift Cards From $10", "Any Amount From $10", "Printable Gift Card", "Leftover Balance Kept", "Gift for Travel Lovers", "Valid for 2 Years", "No Need to Know the Trip", "Last-Minute Gift Sorted", "Custom Map Print Gift", "Add a Personal Message", "Mapsie Gift Cards"],
    descriptions: [
      "Don't know the trip details? They design a map of their favorite trip themselves.",
      "Emailed to you or straight to them, even on Christmas morning. Printable card too.",
      "Choose an amount to cover a print, a framed print or a digital file. From $10.",
      "Any balance they don't use is kept as a new code for their next map. Valid 2 years.",
    ],
  },
  {
    name: "road trip map poster",
    url: `https://mapsie.shop/maps/road-trip-map-poster${US}`,
    keywords: ["custom road trip map", "route 66 map print", "road trip map poster", "road trip map print"],
    headlines: ["Road Trip Map Posters", "Follows the Roads You Drove", "Your Route, Every Detour", "Custom Road Trip Print", "Route 66, PCH & More", "Add Every Stop", "Prints From $45", "Free Shipping", "Framed or Unframed", "Camper & Motorcycle Icons", "Add Your Trip Photos", "Design Yours in Minutes", "Vintage Road-Atlas Styles", "Order by Dec 12 for Christmas", "Mapsie Road Trip Maps"],
    descriptions: [
      "Most map prints draw straight lines. Mapsie follows the real roads you drove.",
      "Add as many stops as you like, mark each leg, add stickers and your own photos.",
      "Vintage, Explorer and 10 more styles. Printed at 300 dpi and shipped free.",
      "The perfect gift for road trippers. Order by December 12 for US Christmas delivery.",
    ],
  },
  {
    name: "custom travel map print",
    url: `https://mapsie.shop/${US}`,
    keywords: ["personalized travel map", "personalized trip map", "custom travel map print", "travel map poster custom", "personalized map print", "custom map print", "travel map print", "personalized travel gift", "map gift", "personalized map"],
    headlines: ["Custom Travel Map Prints", "Map Your Trip, Every Stop", "Your Route, Drawn for Real", "Prints From $45", "Free Shipping", "Framed or Unframed", "Add Your Own Trip Photos", "Design Yours in Minutes", "Printed in the USA", "12 Map Styles to Choose", "Flights, Trains & Road Trips", "See It on Your Wall First", "Personalized Travel Map", "Order by Dec 12 for Christmas", "Mapsie Custom Map Prints"],
    descriptions: [
      "Add your stops and Mapsie draws the route, on the real roads. Printed at 300 dpi.",
      "Stickers, your own photos and 12 styles. Framed in wood with Perspex, ready to hang.",
      "Free to design and preview on a wall before you buy. Prints from $45, free shipping.",
      "A gift they'll actually hang up. Order by December 12 for US delivery by Christmas.",
    ],
  },
];

// Google's limits: headlines ≤ 30, descriptions ≤ 90, keywords ≤ 80 characters.
for (const g of GROUPS) {
  for (const h of g.headlines) if (h.length > 30) throw new Error(`headline too long (${h.length}): ${h}`);
  for (const d of g.descriptions) if (d.length > 90) throw new Error(`description too long (${d.length}): ${d}`);
  if (g.headlines.length !== 15 || g.descriptions.length !== 4) throw new Error(`${g.name}: need 15 headlines and 4 descriptions`);
}

const ops: unknown[] = [];
// 1. UK: maximise clicks with a £0.80 cap, plus broader phrase keywords.
ops.push({ campaignOperation: { update: { resourceName: UK_CAMPAIGN, targetSpend: { cpcBidCeilingMicros: 800_000 } }, updateMask: "target_spend.cpc_bid_ceiling_micros" } });
for (const text of UK_NEW_KEYWORDS) ops.push({ adGroupCriterionOperation: { create: { adGroup: UK_CUSTOM_GROUP, status: "ENABLED", keyword: { text, matchType: "PHRASE" } } } });

// 2. US campaign.
const budget = tmp("campaignBudgets", 1);
const campaign = tmp("campaigns", 2);
ops.push({ campaignBudgetOperation: { create: { resourceName: budget, name: "Mapsie US search (£5/day)", amountMicros: 5_000_000, deliveryMethod: "STANDARD", explicitlyShared: false } } });
ops.push({
  campaignOperation: {
    create: {
      resourceName: campaign,
      name: "Mapsie – Search – US – High intent",
      status: "ENABLED",
      advertisingChannelType: "SEARCH",
      campaignBudget: budget,
      targetSpend: { cpcBidCeilingMicros: 900_000 },
      networkSettings: { targetGoogleSearch: true, targetSearchNetwork: false, targetContentNetwork: false, targetPartnerSearchNetwork: false },
      geoTargetTypeSetting: { positiveGeoTargetType: "PRESENCE" },
      containsEuPoliticalAdvertising: "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING",
    },
  },
});
ops.push({ campaignCriterionOperation: { create: { campaign, location: { geoTargetConstant: "geoTargetConstants/2840" } } } }); // United States
ops.push({ campaignCriterionOperation: { create: { campaign, language: { languageConstant: "languageConstants/1000" } } } }); // English
for (const [text, matchType] of NEGATIVES) ops.push({ campaignCriterionOperation: { create: { campaign, negative: true, keyword: { text, matchType } } } });
GROUPS.forEach((g, i) => {
  const group = tmp("adGroups", 10 + i);
  ops.push({ adGroupOperation: { create: { resourceName: group, campaign, name: g.name, status: "ENABLED", type: "SEARCH_STANDARD" } } });
  for (const text of g.keywords) ops.push({ adGroupCriterionOperation: { create: { adGroup: group, status: "ENABLED", keyword: { text, matchType: "PHRASE" } } } });
  ops.push({
    adGroupAdOperation: {
      create: {
        adGroup: group,
        status: "ENABLED",
        ad: { finalUrls: [g.url], responsiveSearchAd: { headlines: g.headlines.map((text) => ({ text })), descriptions: g.descriptions.map((text) => ({ text })) } },
      },
    },
  });
});

(async () => {
  const r = await gadsMutateAll(ops, check);
  console.log(`GADS ${check ? "checked" : "changed"} ${ops.length} operations`, check ? "" : JSON.stringify(r).slice(0, 1500));
  if (!check) {
    for (const row of await gadsSearch("SELECT campaign.name, campaign.status, campaign.bidding_strategy_type, campaign_budget.amount_micros FROM campaign WHERE campaign.status != 'REMOVED'")) console.log("GADS campaign", JSON.stringify(row));
  }
  process.exit(0);
})().catch((e) => {
  console.log("GADS ERROR", String(e?.message ?? e).slice(0, 3000));
  process.exit(1);
});
