// Runs once when the Next.js server starts.
export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    // Web servers (which can scale out) leave rendering and the print queue to the worker.
    if ((process.env.MAPSIE_ROLE ?? "all") === "web") return;
    const { startScheduler } = await import("./lib/server/scheduler");
    startScheduler();
  }
}
