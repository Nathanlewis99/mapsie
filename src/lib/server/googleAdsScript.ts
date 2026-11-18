// The Google Ads Script shown on /admin/channels (with the import key filled in).
export const GOOGLE_ADS_SCRIPT = String.raw`// Mapsie: send daily Google Ads spend and conversions to mapsie.shop/admin/channels.
// In Google Ads: Tools → Bulk actions → Scripts → + → paste this, set MAPSIE_KEY to the
// key shown on mapsie.shop/admin/channels, Authorise, Run once, then schedule it Daily.
var MAPSIE_KEY = "PASTE-KEY-FROM-ADMIN";
var URL = "https://mapsie.shop/api/ads/spend";

function main() {
  var currency = AdsApp.currentAccount().getCurrencyCode();
  var rows = [];
  var report = AdsApp.search(
    "SELECT segments.date, metrics.cost_micros, metrics.impressions, metrics.clicks, metrics.conversions, metrics.conversions_value " +
    "FROM customer WHERE segments.date DURING LAST_30_DAYS"
  );
  while (report.hasNext()) {
    var r = report.next();
    rows.push({
      day: r.segments.date,
      cost: Number(r.metrics.costMicros) / 1e6,
      currency: currency,
      impressions: Number(r.metrics.impressions),
      clicks: Number(r.metrics.clicks),
      conversions: Number(r.metrics.conversions),
      value: Number(r.metrics.conversionsValue),
    });
  }
  var res = UrlFetchApp.fetch(URL, {
    method: "post",
    contentType: "application/json",
    headers: { "x-mapsie-key": MAPSIE_KEY },
    payload: JSON.stringify({ channel: "google_ads", rows: rows }),
    muteHttpExceptions: true,
  });
  Logger.log("Mapsie: " + res.getResponseCode() + " " + res.getContentText() + " (" + rows.length + " days)");
}
`;
