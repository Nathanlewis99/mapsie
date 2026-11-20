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
  } else if (cmd === "diagnose") {
    // Everything the morning check needs, read-only.
    const q: Record<string, string> = {
      campaign: "SELECT campaign.name, campaign.status, campaign.primary_status, campaign.primary_status_reasons, campaign.bidding_strategy_type, campaign.start_date, campaign.end_date, campaign.network_settings.target_search_network, campaign.network_settings.target_content_network, campaign.geo_target_type_setting.positive_geo_target_type FROM campaign WHERE campaign.status != 'REMOVED'",
      yesterday: "SELECT ad_group.name, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM ad_group WHERE segments.date DURING YESTERDAY",
      week: "SELECT segments.date, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM campaign WHERE segments.date DURING LAST_7_DAYS",
      keyword: "SELECT ad_group.name, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, ad_group_criterion.primary_status, ad_group_criterion.primary_status_reasons, ad_group_criterion.quality_info.quality_score, ad_group_criterion.position_estimates.first_page_cpc_micros FROM keyword_view WHERE ad_group_criterion.status = 'ENABLED'",
      conversion: "SELECT conversion_action.name, conversion_action.status, conversion_action.primary_for_goal, conversion_action.type, conversion_action.category FROM conversion_action WHERE conversion_action.status != 'REMOVED'",
      billing: "SELECT billing_setup.status FROM billing_setup",
      geo: "SELECT campaign_criterion.location.geo_target_constant, campaign_criterion.negative FROM campaign_criterion WHERE campaign_criterion.type = 'LOCATION'",
      account: "SELECT customer.descriptive_name, customer.currency_code, customer.time_zone, customer.status FROM customer",
    };
    for (const [label, query] of Object.entries(q)) {
      try {
        for (const r of await gadsSearch(query)) out(label, r);
      } catch (e) {
        out(`${label}-error`, String((e as Error).message).slice(0, 500));
      }
    }
  } else if (cmd === "search" && a) {
    for (const r of await gadsSearch(a)) out("row", r);
  } else if (cmd === "mutate" && a && b) {
    out(flag === "--check" ? "checked" : "changed", await gadsMutate(a, JSON.parse(b), flag === "--check"));
  } else {
    console.log("GADS usage: status | diagnose | search <GAQL> | mutate <resource> <operations JSON> [--check]");
  }
  process.exit(0);
})().catch((e) => {
  console.log("GADS ERROR", String(e?.message ?? e).slice(0, 1500));
  process.exit(1);
});
