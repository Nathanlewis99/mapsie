// Runs once when the Next.js server starts.
export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    // Web servers (which can scale out) leave rendering and the print queue to the worker.
    if ((process.env.MAPSIE_ROLE ?? "all") === "web") return;
    const { startScheduler } = await import("./lib/server/scheduler");
    startScheduler();
  }
}

// Any uncaught error while handling a request or rendering a page.
export async function onRequestError(
  err: unknown,
  request: { path: string; method: string },
  context: { routerKind: string; routePath: string; routeType: string },
) {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    const { logError } = await import("./lib/server/log");
    await logError(`request.${context.routeType}`, err, { path: request.path, method: request.method, route: context.routePath });
  }
}
