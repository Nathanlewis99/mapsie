// Google Ads change approved by the owner on 21 Nov 2026: both campaigns were losing
// ~90% of their searches on ad rank at 80–90p a click, so raise the most we'll pay per
// click (daily budgets unchanged: £7 UK, £5 US).
// Run as a Render job:  npx -y tsx@4.20.3 scripts/gads/2026-11-21-bids.ts [--check]
import { gadsConfig, gadsMutate, gadsSearch } from "../../src/lib/server/googleAds";

const check = process.argv.includes("--check");
const cid = gadsConfig().customerId;
const CAPS: Record<string, number> = { "24493494206": 1_300_000, "24531925900": 1_400_000 }; // UK £1.30, US £1.40 (~$1.75)

(async () => {
  const ops = Object.entries(CAPS).map(([id, micros]) => ({ update: { resourceName: `customers/${cid}/campaigns/${id}`, targetSpend: { cpcBidCeilingMicros: micros } }, updateMask: "target_spend.cpc_bid_ceiling_micros" }));
  await gadsMutate("campaigns", ops, check);
  console.log(`GADS ${check ? "checked" : "changed"} ${ops.length} campaigns`);
  for (const r of await gadsSearch("SELECT campaign.name, campaign.target_spend.cpc_bid_ceiling_micros, campaign_budget.amount_micros FROM campaign WHERE campaign.status = 'ENABLED'")) console.log("GADS campaign", JSON.stringify(r));
  process.exit(0);
})().catch((e) => {
  console.log("GADS ERROR", String(e?.message ?? e).slice(0, 2000));
  process.exit(1);
});
