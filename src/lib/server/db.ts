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
  /** State, county or province (US, Australian and Canadian addresses need it). */
  state?: string;
  postcode: string;
  country: string; // ISO-2
}

// Etsy orders start at awaiting_design (paid on Etsy, the buyer hasn't designed it yet), then paid.
// pending_payment -> paid -> rendering -> ready (print file done, waiting out the
// cancellation window) -> submitted (sent to the printer) -> shipped. Or cancelled / failed.
export type OrderStatus = "pending_payment" | "awaiting_design" | "paid" | "rendering" | "ready" | "submitted" | "shipped" | "delivered" | "cancelled" | "failed";

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
  /** When the printer told us it had shipped (for timing the review request). */
  shippedAt?: string;
  /** Sent to the printer after this time; until then the customer can cancel. */
  holdUntil?: string;
  stripePaymentIntent?: string;
  cancelledAt?: string;
  refunded?: boolean;
  error?: string;
  /** Anonymous analytics visit that placed the order (for the funnel). */
  visitId?: string;
  /** Where the visit that placed the order came from (no personal data), and the channel it counts towards. */
  attribution?: import("../channels").AttributionIn;
  channel?: import("../channels").ChannelId;
  /** Cookie choices at checkout, and the ad identifiers we may use with them (see conversions.ts). */
  adConsent?: import("./conversions").AdConsent;
  /** Which customer emails have gone out, so none is sent twice. */
  emailsSent?: string[];
  /** A free replacement: the order it replaces, and the support ticket behind it. */
  reprintOf?: string;
  supportTicket?: string;
  /** A digital file (download link emailed) rather than a print. */
  digital?: boolean;
  /** Where it was bought: our checkout (default) or Etsy. */
  source?: "mapsie" | "etsy";
  /** Etsy orders: the size and frame that were paid for (the design must use them). */
  print?: { productId: string; frame: string; paper?: import("../types").PaperId; mount?: import("../types").MountId; format?: "print" | "digital" };
  etsy?: {
    receiptId: string;
    transactionId: string;
    unit: number; // which copy, when one Etsy order is for several prints
    of: number;
    title?: string;
    choices?: string; // the variations the buyer picked, as text
    matched: boolean; // false if we had to guess the size or frame
    trackingSent?: boolean;
    /** The buyer asked to switch to a different print: they buy it on Etsy with this code. */
    swap?: { code: string; to: NonNullable<Order["print"]>; designId?: string; at: string };
    /** This order replaced an earlier Etsy order (a switch); the design carries over. */
    replaces?: string;
    draftDesignId?: string;
    /** This order was replaced by a newer one: refund it in full on Etsy. */
    replacedBy?: string;
    refundDue?: { amount: number; currency: string; since?: string };
    refunded?: boolean;
  };
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
  /** scrypt hash, for email and password sign-in (null for Google-only accounts). */
  passwordHash: string | null;
  /** Proven to own the email (by Google, or by clicking our link). Needed to see guest orders or be an admin. */
  emailVerified: boolean;
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
  -- Customer support: one row per ticket (the conversation is in json), photos separately.
  CREATE TABLE IF NOT EXISTS support_tickets (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    order_id TEXT,
    status TEXT NOT NULL,
    json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
  );
  CREATE INDEX IF NOT EXISTS support_status ON support_tickets(status, updated_at);
  CREATE TABLE IF NOT EXISTS support_files (
    id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL,
    mime TEXT NOT NULL,
    data TEXT NOT NULL,
    created_at TEXT NOT NULL
  );
  CREATE INDEX IF NOT EXISTS support_files_ticket ON support_files(ticket_id);
  -- "Email me my design": the link we sent, and whether they asked for one reminder.
  CREATE TABLE IF NOT EXISTS design_emails (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    design_id TEXT NOT NULL,
    remind INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    reminded_at TEXT
  );
  CREATE INDEX IF NOT EXISTS design_emails_due ON design_emails(remind, reminded_at, created_at);
  -- Gift cards: a Stripe promotion code per card (details in json).
  CREATE TABLE IF NOT EXISTS gift_cards (
    id TEXT PRIMARY KEY,
    code TEXT,
    status TEXT NOT NULL,
    json TEXT NOT NULL,
    created_at TEXT NOT NULL
  );
  CREATE INDEX IF NOT EXISTS gift_cards_code ON gift_cards(code);
  CREATE INDEX IF NOT EXISTS gift_cards_status ON gift_cards(status);
  -- Customer reviews, one per order (photo stored as a small data URL).
  CREATE TABLE IF NOT EXISTS reviews (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL,
    rating INTEGER NOT NULL,
    json TEXT NOT NULL,
    created_at TEXT NOT NULL
  );
  CREATE INDEX IF NOT EXISTS reviews_status ON reviews(status, created_at);
  -- People who unsubscribed from reminder and offer emails (never emailed again except about orders).
  CREATE TABLE IF NOT EXISTS email_optouts (
    email TEXT PRIMARY KEY,
    at TEXT NOT NULL
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
    // Email and password sign-in. Accounts made before this all came from Google, so are verified.
    await pool.query("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash TEXT");
    await pool.query("ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified INTEGER NOT NULL DEFAULT 1");
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
  const userCols = (db.prepare("SELECT name FROM pragma_table_info('users')").all() as { name: string }[]).map((c) => c.name);
  if (!userCols.includes("password_hash")) db.exec("ALTER TABLE users ADD COLUMN password_hash TEXT");
  if (!userCols.includes("email_verified")) db.exec("ALTER TABLE users ADD COLUMN email_verified INTEGER NOT NULL DEFAULT 1");
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
/** The Mapsie orders made from one Etsy order (one per print). */
export async function listOrdersByEtsyReceipt(receiptId: string): Promise<Order[]> {
  if (!/^\d{1,20}$/.test(receiptId)) return [];
  const rows = await all("SELECT json FROM orders WHERE id LIKE 'ord_etsy_%' AND json LIKE ? ORDER BY created_at", [`%"receiptId":"${receiptId}"%`]);
  return rows.map((r) => JSON.parse(String(r.json)) as Order).filter((o) => o.etsy?.receiptId === receiptId);
}
export async function listOrdersByStatus(status: OrderStatus): Promise<Order[]> {
  const rows = await all("SELECT json FROM orders WHERE status = ? ORDER BY created_at", [status]);
  return rows.map((r) => JSON.parse(String(r.json)));
}
/** A customer's orders: placed while signed in, or (once verified by Google) with their email. */
export async function listOrdersForUser(user: User): Promise<Order[]> {
  // Guest orders are only matched by email once the person has proved they own it.
  if (!user.emailVerified) {
    const mine = await all("SELECT json FROM orders WHERE user_id = ? ORDER BY created_at DESC", [user.id]);
    return mine.map((r) => JSON.parse(String(r.json)) as Order).filter((o) => o.status !== "pending_payment");
  }
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
  passwordHash: (r.password_hash as string) ?? null, emailVerified: Number(r.email_verified ?? 1) === 1,
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
    // Google has proved this email belongs to the person signing in. If the account was made with a
    // password that was never verified, that password may have been set by someone else: remove it.
    const unverifiedPassword = Number(existing.email_verified ?? 1) !== 1;
    await run(
      `UPDATE users SET google_sub = ?, email = ?, name = ?, picture = ?, last_login_at = ?, email_verified = 1${unverifiedPassword ? ", password_hash = NULL" : ""} WHERE id = ?`,
      [p.sub, p.email, p.name ?? existing.name ?? null, p.picture ?? existing.picture ?? null, now(), existing.id],
    );
    return (await getUser(String(existing.id)))!;
  }
  const id = `usr_${nanoid(14)}`;
  await run("INSERT INTO users (id, email, name, picture, google_sub, created_at, last_login_at) VALUES (?, ?, ?, ?, ?, ?, ?)", [
    id, p.email, p.name ?? null, p.picture ?? null, p.sub, now(), now(),
  ]);
  return (await getUser(id))!;
}

export async function getUserByEmail(email: string): Promise<User | null> {
  const r = await one("SELECT * FROM users WHERE lower(email) = lower(?)", [email]);
  return r ? toUser(r) : null;
}

/** A new account made with an email and password (unverified until they click the emailed link). */
export async function createPasswordUser(p: { email: string; name?: string; passwordHash: string }): Promise<User> {
  const id = `usr_${nanoid(14)}`;
  await run("INSERT INTO users (id, email, name, password_hash, email_verified, created_at, last_login_at) VALUES (?, ?, ?, ?, 0, ?, ?)", [
    id, p.email, p.name ?? null, p.passwordHash, now(), now(),
  ]);
  return (await getUser(id))!;
}

export async function setPassword(userId: string, passwordHash: string) {
  await run("UPDATE users SET password_hash = ? WHERE id = ?", [passwordHash, userId]);
}
export async function markEmailVerified(userId: string) {
  await run("UPDATE users SET email_verified = 1 WHERE id = ?", [userId]);
}
export async function touchLogin(userId: string) {
  await run("UPDATE users SET last_login_at = ? WHERE id = ?", [now(), userId]);
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

// ---------------------------------------------------------------- support
export type TicketStatus = "open" | "waiting" | "resolved";
export type TicketReason = "not_arrived" | "damaged" | "quality" | "wrong" | "unhappy" | "change" | "address" | "other";
export interface TicketMessage {
  from: "customer" | "mapsie";
  text: string;
  at: string;
  files?: string[]; // support_files ids
}
export interface Ticket {
  id: string; // e.g. MS-7K2QX9
  email: string;
  name?: string;
  orderRef: string; // what the customer typed
  orderId?: string; // the order it matched (email checked)
  reason: TicketReason;
  status: TicketStatus;
  messages: TicketMessage[];
  /** What we did about it, e.g. "Reprint ord_abc", "Refunded £44". */
  actions?: string[];
  createdAt: string;
  updatedAt: string;
}
export async function saveTicket(t: Ticket) {
  await run(
    `INSERT INTO support_tickets (id, email, order_id, status, json, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)
     ON CONFLICT (id) DO UPDATE SET email = excluded.email, order_id = excluded.order_id, status = excluded.status, json = excluded.json, updated_at = excluded.updated_at`,
    [t.id, t.email, t.orderId ?? null, t.status, JSON.stringify(t), t.createdAt, t.updatedAt],
  );
}
export async function getTicket(id: string): Promise<Ticket | null> {
  const r = await one("SELECT json FROM support_tickets WHERE id = ?", [id]);
  return r ? JSON.parse(String(r.json)) : null;
}
export async function listTickets(): Promise<Ticket[]> {
  const rows = await all("SELECT json FROM support_tickets ORDER BY updated_at DESC LIMIT 500");
  return rows.map((r) => JSON.parse(String(r.json)));
}
export async function saveSupportFile(f: { id: string; ticketId: string; mime: string; data: string }) {
  await run("INSERT INTO support_files (id, ticket_id, mime, data, created_at) VALUES (?, ?, ?, ?, ?)", [f.id, f.ticketId, f.mime, f.data, now()]);
}
export async function getSupportFile(id: string): Promise<{ ticketId: string; mime: string; data: string } | null> {
  const r = await one("SELECT ticket_id, mime, data FROM support_files WHERE id = ?", [id]);
  return r ? { ticketId: String(r.ticket_id), mime: String(r.mime), data: String(r.data) } : null;
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

// ---------------------------------------------------------------- design emails
export interface DesignEmail { id: string; email: string; designId: string; remind: boolean; createdAt: string; remindedAt: string | null }
const designEmailRow = (r: Row): DesignEmail => ({
  id: String(r.id), email: String(r.email), designId: String(r.design_id), remind: !!Number(r.remind), createdAt: String(r.created_at), remindedAt: r.reminded_at ? String(r.reminded_at) : null,
});
export async function addDesignEmail(email: string, designId: string, remind: boolean): Promise<DesignEmail> {
  const row = { id: nanoid(12), email: email.trim().toLowerCase(), designId, remind, createdAt: now(), remindedAt: null };
  await run("INSERT INTO design_emails (id, email, design_id, remind, created_at) VALUES (?, ?, ?, ?, ?)", [row.id, row.email, designId, remind ? 1 : 0, row.createdAt]);
  return row;
}
/** How many design emails went to this address since a time (to stop abuse). */
export async function countDesignEmails(email: string, sinceIso: string): Promise<number> {
  const r = await one("SELECT COUNT(*) AS n FROM design_emails WHERE email = ? AND created_at >= ?", [email.trim().toLowerCase(), sinceIso]);
  return Number(r?.n ?? 0);
}
/** Reminders asked for between `from` and `to` (ISO times) that haven't gone yet. */
export async function listDueReminders(fromIso: string, toIso: string): Promise<DesignEmail[]> {
  const rows = await all("SELECT * FROM design_emails WHERE remind = 1 AND reminded_at IS NULL AND created_at >= ? AND created_at <= ? ORDER BY created_at", [fromIso, toIso]);
  return rows.map(designEmailRow);
}
export async function markReminded(id: string) {
  await run("UPDATE design_emails SET reminded_at = ? WHERE id = ?", [now(), id]);
}
export async function isOptedOut(email: string): Promise<boolean> {
  return !!(await one("SELECT email FROM email_optouts WHERE email = ?", [email.trim().toLowerCase()]));
}
export async function optOut(email: string) {
  await run("INSERT INTO email_optouts (email, at) VALUES (?, ?) ON CONFLICT (email) DO NOTHING", [email.trim().toLowerCase(), now()]);
}
/** Has this address placed an order (paid or later) since a time? */
export async function orderedSince(email: string, sinceIso: string): Promise<boolean> {
  const r = await one("SELECT id FROM orders WHERE lower(email) = ? AND created_at >= ? AND status NOT IN ('pending_payment', 'cancelled', 'failed')", [email.trim().toLowerCase(), sinceIso]);
  return !!r;
}
export async function deleteOldDesignEmails(beforeIso: string) {
  return run("DELETE FROM design_emails WHERE created_at < ?", [beforeIso]);
}

// ---------------------------------------------------------------- gift cards
export type GiftCardStatus = "pending_payment" | "active" | "redeemed" | "expired";
export interface GiftCard {
  id: string;
  status: GiftCardStatus;
  amount: number;
  currency: string;
  region: import("../products").RegionId;
  buyerEmail: string;
  fromName: string;
  recipientName: string;
  message: string;
  /** Send the card straight to the recipient, now or on a date (YYYY-MM-DD, morning UK time). */
  recipientEmail?: string;
  sendOn?: string;
  sentToRecipientAt?: string;
  code?: string;
  couponId?: string;
  promoId?: string;
  expiresAt?: string;
  /** A card made from the unused balance of another card. */
  parentId?: string;
  redeemedOrderId?: string;
  stripeSessionId?: string;
  attribution?: import("../channels").AttributionIn;
  channel?: import("../channels").ChannelId;
  createdAt: string;
}
const giftRow = (r: Row) => JSON.parse(String(r.json)) as GiftCard;
export async function saveGiftCard(g: GiftCard) {
  await run(
    "INSERT INTO gift_cards (id, code, status, json, created_at) VALUES (?, ?, ?, ?, ?) ON CONFLICT (id) DO UPDATE SET code = excluded.code, status = excluded.status, json = excluded.json",
    [g.id, g.code ?? null, g.status, JSON.stringify(g), g.createdAt],
  );
}
export async function getGiftCard(id: string): Promise<GiftCard | null> {
  const r = await one("SELECT json FROM gift_cards WHERE id = ?", [id]);
  return r ? giftRow(r) : null;
}
export async function getGiftCardByCode(code: string): Promise<GiftCard | null> {
  const r = await one("SELECT json FROM gift_cards WHERE code = ?", [code.trim().toUpperCase()]);
  return r ? giftRow(r) : null;
}
export async function updateGiftCard(id: string, patch: Partial<GiftCard>) {
  const g = await getGiftCard(id);
  if (g) await saveGiftCard({ ...g, ...patch });
}
/** Move a card from one status to another exactly once (webhooks can repeat). */
export async function claimGiftCard(id: string, from: GiftCardStatus, to: GiftCardStatus): Promise<GiftCard | null> {
  const g = await getGiftCard(id);
  if (!g || g.status !== from) return null;
  const changed = await run("UPDATE gift_cards SET status = ? WHERE id = ? AND status = ?", [to, id, from]);
  if (!changed) return null;
  const next = { ...g, status: to };
  await run("UPDATE gift_cards SET json = ? WHERE id = ?", [JSON.stringify(next), id]);
  return next;
}
export async function listGiftCards(limit = 200): Promise<GiftCard[]> {
  return (await all("SELECT json FROM gift_cards ORDER BY created_at DESC LIMIT ?", [limit])).map(giftRow);
}
export async function listGiftCardsToSend(): Promise<GiftCard[]> {
  return (await all("SELECT json FROM gift_cards WHERE status = 'active' ORDER BY created_at", [])).map(giftRow).filter((g) => g.code && g.recipientEmail && !g.sentToRecipientAt);
}

// ---------------------------------------------------------------- reviews
export type ReviewStatus = "pending" | "approved" | "hidden";
export interface Review {
  id: string;
  orderId: string;
  status: ReviewStatus;
  rating: number;
  text: string;
  name: string; // as they'd like it shown, e.g. "Sarah, Bristol"
  photo?: string; // data URL, resized in the browser
  publish: boolean; // they agreed to us showing it on the site
  product?: string;
  source: "mapsie" | "etsy";
  createdAt: string;
}
const reviewRow = (r: Row) => JSON.parse(String(r.json)) as Review;
export async function saveReview(v: Review) {
  await run(
    "INSERT INTO reviews (id, order_id, status, rating, json, created_at) VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT (order_id) DO UPDATE SET status = excluded.status, rating = excluded.rating, json = excluded.json",
    [v.id, v.orderId, v.status, v.rating, JSON.stringify(v), v.createdAt],
  );
}
export async function getReviewForOrder(orderId: string): Promise<Review | null> {
  const r = await one("SELECT json FROM reviews WHERE order_id = ?", [orderId]);
  return r ? reviewRow(r) : null;
}
export async function setReviewStatus(id: string, status: ReviewStatus) {
  const r = await one("SELECT json FROM reviews WHERE id = ?", [id]);
  if (!r) return;
  const v = { ...reviewRow(r), status };
  await run("UPDATE reviews SET status = ?, json = ? WHERE id = ?", [status, JSON.stringify(v), id]);
}
export async function listReviews(status?: ReviewStatus, limit = 200): Promise<Review[]> {
  const rows = status
    ? await all("SELECT json FROM reviews WHERE status = ? ORDER BY created_at DESC LIMIT ?", [status, limit])
    : await all("SELECT json FROM reviews ORDER BY created_at DESC LIMIT ?", [limit]);
  return rows.map(reviewRow);
}
/** Average and count of approved reviews (for the homepage and Google). */
export async function reviewSummary(): Promise<{ count: number; average: number }> {
  const r = await one("SELECT COUNT(*) AS n, AVG(rating) AS avg FROM reviews WHERE status = 'approved'", []);
  return { count: Number(r?.n ?? 0), average: Number(r?.avg ?? 0) };
}
