// Google Ads from the command line, run as a Render one-off job (where the keys are):
//   npx -y tsx@4.20.3 scripts/google-ads.ts status
//   npx -y tsx@4.20.3 scripts/google-ads.ts search "SELECT campaign.name FROM campaign"
//   npx -y tsx@4.20.3 scripts/google-ads.ts mutate campaigns '[{"update":{...},"updateMask":"status"}]' [--check]
// Changes are only made after the owner has approved them; --check validates without changing anything.
// Output lines start with GADS so they're easy to find in the logs.
import { gadsMutate, gadsSearch, gadsStatus } from "../src/lib/server/googleAds";

const out = (label: string, v: unknown) => console.log(`GADS ${label} ${JSON.stringify(v)}`);

(async () => {
  const [cmd, a, b, flag] = process.argv.slice(2);
  if (cmd === "status") {
    const s = await gadsStatus();
    for (const c of s.campaigns) out("campaign", c);
    for (const ad of s.ads) out("ad", ad);
  } else if (cmd === "search" && a) {
    for (const r of await gadsSearch(a)) out("row", r);
  } else if (cmd === "mutate" && a && b) {
    out(flag === "--check" ? "checked" : "changed", await gadsMutate(a, JSON.parse(b), flag === "--check"));
  } else {
    console.log("GADS usage: status | search <GAQL> | mutate <resource> <operations JSON> [--check]");
  }
  process.exit(0);
})().catch((e) => {
  console.log("GADS ERROR", String(e?.message ?? e).slice(0, 1500));
  process.exit(1);
});
