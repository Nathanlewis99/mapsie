import { promises as fs } from "fs";
import path from "path";
import { deleteOldErrors, deleteOldDesignEmails, deleteOldEvents, deleteUnorderedDesigns, listOrdersByStatus, listOrdersDueForPrint, rendersDir, updateOrder } from "./db";
import { processPaidOrders, ROLE, sendToPrint } from "./fulfil";
import { alertAdmin } from "./email";
import { publicUrl } from "./urls";
import { getCosts, refreshCosts } from "./prodigiCosts";
import { logError } from "./log";
import { etsyJob } from "./etsy";

// Background jobs, started once when the server boots (see src/instrumentation.ts).
// State lives in the database, so nothing is lost if the server restarts.
let started = false;

async function sendDueOrders() {
  for (const o of await listOrdersDueForPrint(new Date().toISOString())) await sendToPrint(o.id);
}

/** Retention promised in the privacy policy. */
async function cleanUp() {
  const day = 24 * 3600_000;
  const designs = await deleteUnorderedDesigns(new Date(Date.now() - 90 * day).toISOString());
  await deleteOldEvents(new Date(Date.now() - 400 * day).toISOString()); // analytics: about 13 months
  await deleteOldErrors(new Date(Date.now() - 365 * day).toISOString());
  await deleteOldDesignEmails(new Date(Date.now() - 365 * day).toISOString()); // "email me my design": 12 months
  const dir = await rendersDir();
  let files = 0;
  for (const f of await fs.readdir(dir)) {
    const st = await fs.stat(path.join(dir, f));
    if (Date.now() - st.mtimeMs > 365 * day) {
      await fs.unlink(path.join(dir, f));
      files++;
    }
  }
  if (designs || files) console.log(`[cleanup] removed ${designs} unordered designs, ${files} old print files`);
}

/** A render interrupted by a restart: put it back in the queue. Only one worker runs, so this is safe. */
async function requeueInterrupted() {
  for (const o of await listOrdersByStatus("rendering")) await updateOrder(o.id, { status: "paid" });
}

/**
 * Uptime: the worker checks the public site every 5 minutes and emails us after 3 failures
 * in a row (about 15 minutes down), then again when it's back. If Render itself is down the
 * worker is too, so an outside monitor on /api/health is still worth having.
 */
let failures = 0;
let alerted = false;
async function checkSite() {
  let ok = false;
  try {
    const r = await fetch(`${publicUrl()}/api/health`, { signal: AbortSignal.timeout(15_000), cache: "no-store" });
    ok = r.ok && (await r.json()).ok === true;
  } catch {}
  if (ok) {
    if (alerted) await alertAdmin("mapsie.shop is back up", `The site answered its health check again at ${new Date().toISOString()}.`);
    failures = 0;
    alerted = false;
    return;
  }
  failures++;
  if (failures >= 3 && !alerted) {
    alerted = true;
    await alertAdmin("mapsie.shop looks down", `${publicUrl()}/api/health has failed ${failures} checks in a row (5 minutes apart). Check the Render dashboard.`);
  }
}

/**
 * The one reminder people asked for when they emailed themselves their design: a day
 * later, unless they've ordered or unsubscribed. Only the latest request per address.
 */
async function sendDesignReminders() {
  const { listDueReminders, markReminded, isOptedOut, orderedSince, getDesign } = await import("./db");
  const { sendDesignReminderEmail } = await import("./email");
  const day = 24 * 3600_000;
  const due = await listDueReminders(new Date(Date.now() - 7 * day).toISOString(), new Date(Date.now() - day).toISOString());
  const latest = new Map<string, (typeof due)[number]>();
  for (const r of due) latest.set(r.email, r); // oldest first, so the last wins
  for (const r of due) if (latest.get(r.email) !== r) await markReminded(r.id);
  for (const r of latest.values()) {
    await markReminded(r.id); // first, so a failure never means two emails
    if ((await isOptedOut(r.email)) || (await orderedSince(r.email, r.createdAt))) continue;
    const d = await getDesign(r.designId);
    if (d) await sendDesignReminderEmail(r, d.title ?? "");
  }
}

/** Runs on the worker (or the single server): renders, sends due orders, tidies up. */
export function startScheduler() {
  if (started) return;
  started = true;
  const safe = (fn: () => Promise<unknown>, name: string) => () => fn().catch((e) => logError(`job.${name}`, e));
  setTimeout(safe(async () => { await requeueInterrupted(); await processPaidOrders(); }, "render-queue"), 3_000);
  setInterval(safe(processPaidOrders, "render-queue"), 5_000);
  setInterval(safe(sendDueOrders, "print-queue"), 60_000);
  setInterval(safe(cleanUp, "cleanup"), 6 * 3600_000);
  // Prodigi's prices, once a day (also spots their promotions: see prodigiCosts.ts).
  setInterval(safe(refreshCosts, "costs"), 24 * 3600_000);
  setTimeout(safe(async () => { if (!(await getCosts())) await refreshCosts(); }, "costs"), 120_000);
  setTimeout(safe(sendDueOrders, "print-queue"), 5_000);
  setTimeout(safe(cleanUp, "cleanup"), 60_000);
  // Etsy: new orders and design reminders (does nothing until a shop is connected).
  setInterval(safe(etsyJob, "etsy"), 5 * 60_000);
  if (ROLE === "worker") setInterval(safe(checkSite, "uptime"), 5 * 60_000);
  setInterval(safe(sendDesignReminders, "design-reminders"), 30 * 60_000);
  // Review requests a few days after delivery.
  setInterval(safe(async () => (await import("./reviews")).sendReviewRequests(), "review-requests"), 3 * 3600_000);
  // Gift cards scheduled for a date (e.g. Christmas morning).
  setInterval(safe(async () => (await import("./giftcards")).sendDueGiftCards(), "gift-cards"), 15 * 60_000);
  setTimeout(safe(etsyJob, "etsy"), 30_000);
}
