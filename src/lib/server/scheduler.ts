import { promises as fs } from "fs";
import path from "path";
import { deleteOldErrors, deleteOldEvents, deleteUnorderedDesigns, listOrdersByStatus, listOrdersDueForPrint, rendersDir, updateOrder } from "./db";
import { processPaidOrders, sendToPrint } from "./fulfil";
import { getCosts, refreshCosts } from "./prodigiCosts";
import { logError } from "./log";

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
}
