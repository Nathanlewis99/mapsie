import { promises as fs, existsSync, mkdirSync, readdirSync, readFileSync } from "fs";
import path from "path";
import type BetterSqlite from "better-sqlite3";
import type { Pool } from "pg";
import { nanoid } from "nanoid";
import type { Design } from "../types";
import type { ShippingId, RegionId } from "../products";

// Storage. With DATABASE_URL set, everything lives in Postgres, so any number of
// web servers can share it (this is what lets the site scale out). Without it,
// a local SQLite file under DATA_DIR is used (development, or a single server).
// Rendered print files live under DATA_DIR on the render worker's disk.
const ROOT = process.env.DATA_DIR ?? path.join(process.cwd(), "data");

export interface Address {
  name: string;
  line1: string;
  line2?: string;
  city: string;
  postcode: string;
  country: string; // ISO-2
}

// pending_payment -> paid -> rendering -> ready (print file done, waiting out the
// cancellation window) -> submitted (sent to the printer) -> shipped. Or cancelled / failed.
export type OrderStatus = "pending_payment" | "paid" | "rendering" | "ready" | "submitted" | "shipped" | "cancelled" | "failed";

export interface Order {
  id: string;
  designId: string;
  userId?: string;
  email: string;
  shipping: ShippingId;
  region: RegionId;
  currency: string;
  total: number;
  status: OrderStatus;
  address?: Address;
  renderFile?: string;
  renderInfo?: { width: number; height: number; dpi: number; mapDpi?: number };
  printProviderOrderId?: string;
  /** From the printer once dispatched. */
  shipments?: { carrier?: string; trackingNumber?: string; trackingUrl?: string; dispatchDate?: string }[];
  printStage?: string;
  paidAt?: string;
  /** Sent to the printer after this time; until then the customer can cancel. */
  holdUntil?: string;
  stripePaymentIntent?: string;
  cancelledAt?: string;
  refunded?: boolean;
  error?: string;
  /** Anonymous analytics visit that placed the order (for the funnel). */
  visitId?: string;
  /** Which customer emails have gone out, so none is sent twice. */
  emailsSent?: string[];
  createdAt: string;
}

export interface User {
  id: string;
  email: string;
  name: string | null;
  picture: string | null;
  googleSub: string | null;
  totpSecret: string | null;
  totpEnabled: boolean;
  createdAt: string;
  lastLoginAt: string | null;
}

export interface SavedDesign {
  id: string;
  userId: string;
  title: string;
  design: Design;
  createdAt: string;
  updatedAt: string;
}

// ---------------------------------------------------------------- connection
// The same SQL runs on both databases: "?" placeholders, ON CONFLICT upserts,
// lower() for case-insensitive email matching.
type Row = Record<string, unknown>;
interface Driver {
  kind: "pg" | "sqlite";
  all(sql: string, params?: unknown[]): Promise<Row[]>;
  run(sql: string, params?: unknown[]): Promise<number>; // rows changed
}

const SCHEMA = `
  CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    name TEXT,
    picture TEXT,
    google_sub TEXT UNIQUE,
    totp_secret TEXT,
    totp_enabled INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    last_login_at TEXT
  );
  CREATE UNIQUE INDEX IF NOT EXISTS users_email ON users(lower(email));
  -- Frozen snapshots: what was ordered or shared. Never edited after creation.
  CREATE TABLE IF NOT EXISTS designs (
    id TEXT PRIMARY KEY,
    json TEXT NOT NULL,
    created_at TEXT NOT NULL
  );
  -- A signed-in customer's own designs, which they can keep editing.
  CREATE TABLE IF NOT EXISTS saved_designs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
  );
  CREATE INDEX IF NOT EXISTS saved_designs_user ON saved_designs(user_id, updated_at);
  CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
    email TEXT NOT NULL,
    status TEXT NOT NULL,
    design_id TEXT,
    json TEXT NOT NULL,
    created_at TEXT NOT NULL
  );
  CREATE INDEX IF NOT EXISTS orders_user ON orders(user_id, created_at);
  CREATE INDEX IF NOT EXISTS orders_status ON orders(status);
  -- Road geometry per leg, so a route is only ever fetched once.
  CREATE TABLE IF NOT EXISTS route_cache (
    key TEXT PRIMARY KEY,
    json TEXT NOT NULL,
    created_at TEXT NOT NULL
  );
  -- Errors from the server and from customers' browsers, grouped by fingerprint.
  CREATE TABLE IF NOT EXISTS errors (
    fingerprint TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    scope TEXT NOT NULL,
    message TEXT NOT NULL,
    stack TEXT,
    context TEXT,
    count INTEGER NOT NULL DEFAULT 1,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    resolved INTEGER NOT NULL DEFAULT 0
  );
  -- Anonymous product analytics: one row per funnel step per visit. No personal data.
  CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    visit_id TEXT NOT NULL,
    name TEXT NOT NULL,
    props TEXT,
    at TEXT NOT NULL
  );
  CREATE INDEX IF NOT EXISTS events_name_at ON events(name, at);
  -- Small key/value store for settings and cached figures (e.g. Prodigi costs).
  CREATE TABLE IF NOT EXISTS kv (
    key TEXT PRIMARY KEY,
    json TEXT NOT NULL,
    updated_at TEXT NOT NULL
  );
`;

let driverPromise: Promise<Driver> | null = null;
const conn = () => (driverPromise ??= connect());

async function connect(): Promise<Driver> {
  const url = process.env.DATABASE_URL;
  if (url) {
    const { Pool } = await import("pg");
    const pool: Pool = new Pool({
      connectionString: url,
      max: Number(process.env.DB_POOL ?? 10),
      // Render's internal database URL needs no TLS; set PGSSL=1 for an external URL.
      ssl: process.env.PGSSL === "1" ? { rejectUnauthorized: false } : undefined,
    });
    const pg = (sql: string) => {
      let n = 0;
      return sql.replace(/\?/g, () => `$${++n}`);
    };
    const d: Driver = {
      kind: "pg",
      all: async (sql, params = []) => (await pool.query(pg(sql), params)).rows,
      run: async (sql, params = []) => (await pool.query(pg(sql), params)).rowCount ?? 0,
    };
    await pool.query(SCHEMA);
    await importSqliteIntoPostgres(d);
    return d;
  }
  const { default: Database } = await import("better-sqlite3");
  mkdirSync(ROOT, { recursive: true });
  const db: BetterSqlite.Database = new Database(path.join(ROOT, "mapsie.db"));
  db.pragma("journal_mode = WAL");
  db.pragma("foreign_keys = ON");
  // Databases from before design_id existed.
  const cols = db.prepare("SELECT name FROM pragma_table_info('orders')").all() as { name: string }[];
  if (cols.length && !cols.some((c) => c.name === "design_id")) {
    db.exec("ALTER TABLE orders ADD COLUMN design_id TEXT");
    db.exec("UPDATE orders SET design_id = json_extract(json, '$.designId')");
  }
  // Older databases had a NOCASE unique constraint on users.email instead of the lower() index.
  try {
    db.exec(SCHEMA);
  } catch (e) {
    if (!/already exists|UNIQUE/.test(String(e))) throw e;
  }
  const d: Driver = {
    kind: "sqlite",
    all: async (sql, params = []) => db.prepare(sql).all(...params) as Row[],
    run: async (sql, params = []) => db.prepare(sql).run(...params).changes,
  };
  importLegacyJson(db);
  return d;
}

/**
 * Moving to Postgres: copy everything from the SQLite file on this machine's
 * disk (if there is one) the first time, so no designs, accounts or orders are lost.
 */
async function importSqliteIntoPostgres(pg: Driver) {
  const file = path.join(ROOT, "mapsie.db");
  if (!existsSync(file)) return;
  const [{ n }] = (await pg.all("SELECT (SELECT count(*) FROM orders) + (SELECT count(*) FROM designs) + (SELECT count(*) FROM users) AS n")) as { n: string }[];
  if (Number(n) > 0) return;
  const { default: Database } = await import("better-sqlite3");
  const old = new Database(file, { readonly: true });
  const tables: [string, string[]][] = [
    ["users", ["id", "email", "name", "picture", "google_sub", "totp_secret", "totp_enabled", "created_at", "last_login_at"]],
    ["designs", ["id", "json", "created_at"]],
    ["saved_designs", ["id", "user_id", "title", "json", "created_at", "updated_at"]],
    ["orders", ["id", "user_id", "email", "status", "json", "created_at"]],
    ["route_cache", ["key", "json", "created_at"]],
  ];
  let total = 0;
  for (const [t, cols] of tables) {
    let rows: Row[] = [];
    try {
      rows = old.prepare(`SELECT ${cols.join(", ")} FROM ${t}`).all() as Row[];
    } catch {
      continue;
    }
    const extra = t === "orders" ? ", design_id" : "";
    for (const r of rows) {
      const vals = cols.map((c) => r[c]);
      if (t === "orders") vals.push(JSON.parse(String(r.json)).designId ?? null);
      await pg.run(`INSERT INTO ${t} (${cols.join(", ")}${extra}) VALUES (${[...cols, ...(extra ? ["x"] : [])].map(() => "?").join(", ")}) ON CONFLICT DO NOTHING`, vals);
    }
    total += rows.length;
  }
  old.close();
  console.log(`[db] copied ${total} rows from SQLite into Postgres`);
}

/** One-off: bring in designs and orders saved as JSON files by earlier versions. */
function importLegacyJson(d: BetterSqlite.Database) {
  const read = (kind: string) => {
    const dir = path.join(ROOT, kind);
    if (!existsSync(dir)) return [];
    return readdirSync(dir)
      .filter((f) => f.endsWith(".json"))
      .flatMap((f) => {
        try {
          return [JSON.parse(readFileSync(path.join(dir, f), "utf8"))];
        } catch {
          return [];
        }
      });
  };
  const designCount = (d.prepare("SELECT count(*) n FROM designs").get() as { n: number }).n;
  const orderCount = (d.prepare("SELECT count(*) n FROM orders").get() as { n: number }).n;
  if (designCount === 0) {
    const ins = d.prepare("INSERT OR IGNORE INTO designs (id, json, created_at) VALUES (?, ?, ?)");
    for (const x of read("designs")) ins.run(x.id, JSON.stringify(x), new Date().toISOString());
  }
  if (orderCount === 0) {
    const ins = d.prepare("INSERT OR IGNORE INTO orders (id, user_id, email, status, design_id, json, created_at) VALUES (?, NULL, ?, ?, ?, ?, ?)");
    for (const o of read("orders")) ins.run(o.id, o.email ?? "", o.status ?? "failed", o.designId ?? null, JSON.stringify(o), o.createdAt ?? new Date().toISOString());
  }
}

const all = async (sql: string, params?: unknown[]) => (await conn()).all(sql, params);
const one = async (sql: string, params?: unknown[]) => (await all(sql, params))[0];
const run = async (sql: string, params?: unknown[]) => (await conn()).run(sql, params);
const now = () => new Date().toISOString();

/** For health checks. */
export async function dbKind() {
  return (await conn()).kind;
}

// ---------------------------------------------------------------- design snapshots
export async function saveDesign(d: Design) {
  await run("INSERT INTO designs (id, json, created_at) VALUES (?, ?, ?) ON CONFLICT (id) DO UPDATE SET json = excluded.json", [d.id, JSON.stringify(d), now()]);
}
export async function getDesign(id: string): Promise<Design | null> {
  const row = await one("SELECT json FROM designs WHERE id = ?", [id]);
  return row ? JSON.parse(String(row.json)) : null;
}

// ---------------------------------------------------------------- orders
export async function saveOrder(o: Order) {
  await run(
    `INSERT INTO orders (id, user_id, email, status, design_id, json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)
     ON CONFLICT (id) DO UPDATE SET user_id = excluded.user_id, email = excluded.email, status = excluded.status, design_id = excluded.design_id, json = excluded.json`,
    [o.id, o.userId ?? null, o.email, o.status, o.designId, JSON.stringify(o), o.createdAt],
  );
}
export async function getOrder(id: string): Promise<Order | null> {
  const row = await one("SELECT json FROM orders WHERE id = ?", [id]);
  return row ? JSON.parse(String(row.json)) : null;
}
export async function updateOrder(id: string, patch: Partial<Order>) {
  const o = await getOrder(id);
  if (!o) throw new Error("order not found");
  const n = { ...o, ...patch };
  await saveOrder(n);
  return n;
}
/**
 * Move an order from one status to another only if it's still in the first one.
 * With several servers this is how exactly one of them picks up each job.
 */
export async function claimOrder(id: string, from: OrderStatus, to: OrderStatus): Promise<Order | null> {
  const changed = await run("UPDATE orders SET status = ? WHERE id = ? AND status = ?", [to, id, from]);
  if (!changed) return null;
  return updateOrder(id, { status: to });
}
export async function listOrders(): Promise<Order[]> {
  const rows = await all("SELECT json FROM orders ORDER BY created_at DESC");
  return rows.map((r) => JSON.parse(String(r.json)));
}
export async function listOrdersByStatus(status: OrderStatus): Promise<Order[]> {
  const rows = await all("SELECT json FROM orders WHERE status = ? ORDER BY created_at", [status]);
  return rows.map((r) => JSON.parse(String(r.json)));
}
/** A customer's orders: placed while signed in, or (once verified by Google) with their email. */
export async function listOrdersForUser(user: User): Promise<Order[]> {
  const rows = await all("SELECT json FROM orders WHERE user_id = ? OR (user_id IS NULL AND lower(email) = lower(?)) ORDER BY created_at DESC", [user.id, user.email]);
  return rows.map((r) => JSON.parse(String(r.json)) as Order).filter((o) => o.status !== "pending_payment");
}

export const rendersDir = async () => {
  const d = path.join(ROOT, "renders");
  await fs.mkdir(d, { recursive: true });
  return d;
};

// ---------------------------------------------------------------- users
const toUser = (r: Row): User => ({
  id: String(r.id), email: String(r.email), name: (r.name as string) ?? null, picture: (r.picture as string) ?? null,
  googleSub: (r.google_sub as string) ?? null, totpSecret: (r.totp_secret as string) ?? null, totpEnabled: !!Number(r.totp_enabled),
  createdAt: String(r.created_at), lastLoginAt: (r.last_login_at as string) ?? null,
});

export async function getUser(id: string): Promise<User | null> {
  const r = await one("SELECT * FROM users WHERE id = ?", [id]);
  return r ? toUser(r) : null;
}

/** Create or update a user after a successful Google sign-in. */
export async function upsertGoogleUser(p: { sub: string; email: string; name?: string; picture?: string }): Promise<User> {
  const existing = (await one("SELECT * FROM users WHERE google_sub = ?", [p.sub])) ?? (await one("SELECT * FROM users WHERE lower(email) = lower(?)", [p.email]));
  if (existing) {
    await run("UPDATE users SET google_sub = ?, email = ?, name = ?, picture = ?, last_login_at = ? WHERE id = ?", [
      p.sub, p.email, p.name ?? existing.name ?? null, p.picture ?? existing.picture ?? null, now(), existing.id,
    ]);
    return (await getUser(String(existing.id)))!;
  }
  const id = `usr_${nanoid(14)}`;
  await run("INSERT INTO users (id, email, name, picture, google_sub, created_at, last_login_at) VALUES (?, ?, ?, ?, ?, ?, ?)", [
    id, p.email, p.name ?? null, p.picture ?? null, p.sub, now(), now(),
  ]);
  return (await getUser(id))!;
}

export async function setTotp(userId: string, secret: string | null, enabled: boolean) {
  await run("UPDATE users SET totp_secret = ?, totp_enabled = ? WHERE id = ?", [secret, enabled ? 1 : 0, userId]);
}

// ---------------------------------------------------------------- saved designs
const toSaved = (r: Row): SavedDesign => ({
  id: String(r.id), userId: String(r.user_id), title: String(r.title), design: JSON.parse(String(r.json)), createdAt: String(r.created_at), updatedAt: String(r.updated_at),
});

export async function listSavedDesigns(userId: string): Promise<SavedDesign[]> {
  return (await all("SELECT * FROM saved_designs WHERE user_id = ? ORDER BY updated_at DESC", [userId])).map(toSaved);
}
export async function getSavedDesign(userId: string, id: string): Promise<SavedDesign | null> {
  const r = await one("SELECT * FROM saved_designs WHERE id = ? AND user_id = ?", [id, userId]);
  return r ? toSaved(r) : null;
}
/** Create (no id) or update (id) one of a user's designs. Returns its id. */
export async function upsertSavedDesign(userId: string, design: Design, id?: string): Promise<string> {
  const title = (design.title || "Untitled map").slice(0, 80);
  if (id && (await one("SELECT 1 AS x FROM saved_designs WHERE id = ? AND user_id = ?", [id, userId]))) {
    await run("UPDATE saved_designs SET title = ?, json = ?, updated_at = ? WHERE id = ?", [title, JSON.stringify(design), now(), id]);
    return id;
  }
  const newId = `sd_${nanoid(12)}`;
  await run("INSERT INTO saved_designs (id, user_id, title, json, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)", [
    newId, userId, title, JSON.stringify(design), now(), now(),
  ]);
  return newId;
}
export async function deleteSavedDesign(userId: string, id: string) {
  await run("DELETE FROM saved_designs WHERE id = ? AND user_id = ?", [id, userId]);
}

// ---------------------------------------------------------------- route cache
export async function getCachedRoute(key: string): Promise<unknown | undefined> {
  const r = await one("SELECT json FROM route_cache WHERE key = ?", [key]);
  return r ? JSON.parse(String(r.json)) : undefined;
}
export async function putCachedRoute(key: string, value: unknown) {
  await run("INSERT INTO route_cache (key, json, created_at) VALUES (?, ?, ?) ON CONFLICT (key) DO UPDATE SET json = excluded.json", [key, JSON.stringify(value), now()]);
}

// ---------------------------------------------------------------- key/value
export async function getKv<T>(key: string): Promise<{ value: T; updatedAt: string } | null> {
  const r = await one("SELECT json, updated_at FROM kv WHERE key = ?", [key]);
  return r ? { value: JSON.parse(String(r.json)), updatedAt: String(r.updated_at) } : null;
}
export async function putKv(key: string, value: unknown) {
  await run("INSERT INTO kv (key, json, updated_at) VALUES (?, ?, ?) ON CONFLICT (key) DO UPDATE SET json = excluded.json, updated_at = excluded.updated_at", [
    key, JSON.stringify(value), now(),
  ]);
}

/** Orders whose cancellation window has ended and are ready to go to the printer. */
export async function listOrdersDueForPrint(nowIso: string): Promise<Order[]> {
  return (await listOrdersByStatus("ready")).filter((o) => !o.holdUntil || o.holdUntil <= nowIso);
}

/** Delete design snapshots older than the cutoff that no order uses. Returns how many. */
export async function deleteUnorderedDesigns(beforeIso: string): Promise<number> {
  return run("DELETE FROM designs WHERE created_at < ? AND id NOT IN (SELECT design_id FROM orders WHERE design_id IS NOT NULL)", [beforeIso]);
}

// ---------------------------------------------------------------- errors
export interface ErrorRow {
  fingerprint: string; source: string; scope: string; message: string; stack: string | null;
  context: string | null; count: number; firstSeen: string; lastSeen: string; resolved: boolean;
}
export async function recordError(e: { fingerprint: string; source: string; scope: string; message: string; stack?: string; context?: unknown }) {
  const t = now();
  await run(
    `INSERT INTO errors (fingerprint, source, scope, message, stack, context, count, first_seen, last_seen, resolved) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, 0)
     ON CONFLICT (fingerprint) DO UPDATE SET count = errors.count + 1, last_seen = excluded.last_seen, context = excluded.context, stack = excluded.stack, resolved = 0`,
    [e.fingerprint, e.source, e.scope, e.message.slice(0, 1000), e.stack?.slice(0, 4000) ?? null, e.context ? JSON.stringify(e.context).slice(0, 4000) : null, t, t],
  );
}
export async function listErrors(includeResolved = false): Promise<ErrorRow[]> {
  const rows = await all(`SELECT * FROM errors ${includeResolved ? "" : "WHERE resolved = 0"} ORDER BY last_seen DESC LIMIT 200`);
  return rows.map((r) => ({
    fingerprint: String(r.fingerprint), source: String(r.source), scope: String(r.scope), message: String(r.message),
    stack: (r.stack as string) ?? null, context: (r.context as string) ?? null, count: Number(r.count),
    firstSeen: String(r.first_seen), lastSeen: String(r.last_seen), resolved: !!Number(r.resolved),
  }));
}
export async function resolveError(fingerprint: string) {
  await run("UPDATE errors SET resolved = 1 WHERE fingerprint = ?", [fingerprint]);
}

// ---------------------------------------------------------------- analytics
export async function recordEvent(visitId: string, name: string, props?: Record<string, unknown>) {
  await run("INSERT INTO events (id, visit_id, name, props, at) VALUES (?, ?, ?, ?, ?)", [nanoid(14), visitId, name, props ? JSON.stringify(props) : null, now()]);
}
/** For each event name since a time: how many distinct visits did it. */
export async function eventCounts(sinceIso: string): Promise<Record<string, number>> {
  const rows = await all("SELECT name, count(DISTINCT visit_id) AS n FROM events WHERE at >= ? GROUP BY name", [sinceIso]);
  return Object.fromEntries(rows.map((r) => [String(r.name), Number(r.n)]));
}
/** Visits since a time with the steps each reached, plus the props of its first event. */
export async function visitSteps(sinceIso: string): Promise<{ visitId: string; steps: string[]; props: Record<string, unknown> }[]> {
  const rows = await all("SELECT visit_id, name, props FROM events WHERE at >= ? ORDER BY at", [sinceIso]);
  const map = new Map<string, { steps: Set<string>; props: Record<string, unknown> }>();
  for (const r of rows) {
    const id = String(r.visit_id);
    let v = map.get(id);
    if (!v) map.set(id, (v = { steps: new Set(), props: r.props ? JSON.parse(String(r.props)) : {} }));
    v.steps.add(String(r.name));
  }
  return [...map.entries()].map(([visitId, v]) => ({ visitId, steps: [...v.steps], props: v.props }));
}
export async function deleteOldEvents(beforeIso: string) {
  return run("DELETE FROM events WHERE at < ?", [beforeIso]);
}
export async function deleteOldErrors(beforeIso: string) {
  return run("DELETE FROM errors WHERE last_seen < ?", [beforeIso]);
}
/** Most searched terms since a time, with how often they found nothing. */
export async function topSearches(sinceIso: string, limit = 50): Promise<{ q: string; n: number; empty: number }[]> {
  const rows = await all("SELECT props FROM events WHERE name = 'search' AND at >= ?", [sinceIso]);
  const map = new Map<string, { n: number; empty: number }>();
  for (const r of rows) {
    const p = JSON.parse(String(r.props ?? "{}")) as { q?: string; results?: string };
    if (!p.q) continue;
    const e = map.get(p.q) ?? { n: 0, empty: 0 };
    e.n++;
    if (Number(p.results) === 0) e.empty++;
    map.set(p.q, e);
  }
  return [...map.entries()].map(([q, e]) => ({ q, ...e })).sort((a, b) => b.n - a.n).slice(0, limit);
}
