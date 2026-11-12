import { promises as fs, existsSync, mkdirSync, readdirSync, readFileSync } from "fs";
import path from "path";
import Database from "better-sqlite3";
import { nanoid } from "nanoid";
import type { Design } from "../types";
import type { ShippingId, RegionId } from "../products";

// Storage: one SQLite database plus a folder of rendered print files, both under
// DATA_DIR (a persistent disk in production, see render.yaml). SQLite suits a
// single server; move to Postgres if Mapsie ever runs on several machines.
const ROOT = process.env.DATA_DIR ?? path.join(process.cwd(), "data");

export interface Address {
  name: string;
  line1: string;
  line2?: string;
  city: string;
  postcode: string;
  country: string; // ISO-2
}

export type OrderStatus = "pending_payment" | "paid" | "rendering" | "submitted" | "failed";

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
  error?: string;
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
let db: Database.Database | null = null;

function open(): Database.Database {
  if (db) return db;
  mkdirSync(ROOT, { recursive: true });
  db = new Database(path.join(ROOT, "mapsie.db"));
  db.pragma("journal_mode = WAL");
  db.pragma("foreign_keys = ON");
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT NOT NULL UNIQUE COLLATE NOCASE,
      name TEXT,
      picture TEXT,
      google_sub TEXT UNIQUE,
      totp_secret TEXT,
      totp_enabled INTEGER NOT NULL DEFAULT 0,
      created_at TEXT NOT NULL,
      last_login_at TEXT
    );
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
    CREATE INDEX IF NOT EXISTS saved_designs_user ON saved_designs(user_id, updated_at DESC);
    CREATE TABLE IF NOT EXISTS orders (
      id TEXT PRIMARY KEY,
      user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
      email TEXT NOT NULL,
      status TEXT NOT NULL,
      json TEXT NOT NULL,
      created_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS orders_user ON orders(user_id, created_at DESC);
    CREATE INDEX IF NOT EXISTS orders_email ON orders(email COLLATE NOCASE);
    -- Road geometry per leg, so a route is only ever fetched once.
    CREATE TABLE IF NOT EXISTS route_cache (
      key TEXT PRIMARY KEY,
      json TEXT NOT NULL,
      created_at TEXT NOT NULL
    );
  `);
  importLegacyJson(db);
  return db;
}

/** One-off: bring in designs and orders saved as JSON files by earlier versions. */
function importLegacyJson(d: Database.Database) {
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
    const ins = d.prepare("INSERT OR IGNORE INTO orders (id, user_id, email, status, json, created_at) VALUES (?, NULL, ?, ?, ?, ?)");
    for (const o of read("orders")) ins.run(o.id, o.email ?? "", o.status ?? "failed", JSON.stringify(o), o.createdAt ?? new Date().toISOString());
  }
}

const now = () => new Date().toISOString();

// ---------------------------------------------------------------- design snapshots
export async function saveDesign(d: Design) {
  open().prepare("INSERT OR REPLACE INTO designs (id, json, created_at) VALUES (?, ?, ?)").run(d.id, JSON.stringify(d), now());
}
export async function getDesign(id: string): Promise<Design | null> {
  const row = open().prepare("SELECT json FROM designs WHERE id = ?").get(id) as { json: string } | undefined;
  return row ? JSON.parse(row.json) : null;
}

// ---------------------------------------------------------------- orders
export async function saveOrder(o: Order) {
  open()
    .prepare("INSERT OR REPLACE INTO orders (id, user_id, email, status, json, created_at) VALUES (?, ?, ?, ?, ?, ?)")
    .run(o.id, o.userId ?? null, o.email, o.status, JSON.stringify(o), o.createdAt);
}
export async function getOrder(id: string): Promise<Order | null> {
  const row = open().prepare("SELECT json FROM orders WHERE id = ?").get(id) as { json: string } | undefined;
  return row ? JSON.parse(row.json) : null;
}
export async function updateOrder(id: string, patch: Partial<Order>) {
  const o = await getOrder(id);
  if (!o) throw new Error("order not found");
  const n = { ...o, ...patch };
  await saveOrder(n);
  return n;
}
export async function listOrders(): Promise<Order[]> {
  const rows = open().prepare("SELECT json FROM orders ORDER BY created_at DESC").all() as { json: string }[];
  return rows.map((r) => JSON.parse(r.json));
}
/** A customer's orders: placed while signed in, or (once verified by Google) with their email. */
export async function listOrdersForUser(user: User): Promise<Order[]> {
  const rows = open()
    .prepare("SELECT json FROM orders WHERE user_id = ? OR (user_id IS NULL AND email = ? COLLATE NOCASE) ORDER BY created_at DESC")
    .all(user.id, user.email) as { json: string }[];
  return rows.map((r) => JSON.parse(r.json)).filter((o: Order) => o.status !== "pending_payment");
}

export const rendersDir = async () => {
  const d = path.join(ROOT, "renders");
  await fs.mkdir(d, { recursive: true });
  return d;
};

// ---------------------------------------------------------------- users
type UserRow = {
  id: string; email: string; name: string | null; picture: string | null; google_sub: string | null;
  totp_secret: string | null; totp_enabled: number; created_at: string; last_login_at: string | null;
};
const toUser = (r: UserRow): User => ({
  id: r.id, email: r.email, name: r.name, picture: r.picture, googleSub: r.google_sub,
  totpSecret: r.totp_secret, totpEnabled: !!r.totp_enabled, createdAt: r.created_at, lastLoginAt: r.last_login_at,
});

export function getUser(id: string): User | null {
  const r = open().prepare("SELECT * FROM users WHERE id = ?").get(id) as UserRow | undefined;
  return r ? toUser(r) : null;
}

/** Create or update a user after a successful Google sign-in. */
export function upsertGoogleUser(p: { sub: string; email: string; name?: string; picture?: string }): User {
  const d = open();
  const existing = (d.prepare("SELECT * FROM users WHERE google_sub = ?").get(p.sub) ??
    d.prepare("SELECT * FROM users WHERE email = ? COLLATE NOCASE").get(p.email)) as UserRow | undefined;
  if (existing) {
    d.prepare("UPDATE users SET google_sub = ?, email = ?, name = ?, picture = ?, last_login_at = ? WHERE id = ?")
      .run(p.sub, p.email, p.name ?? existing.name, p.picture ?? existing.picture, now(), existing.id);
    return getUser(existing.id)!;
  }
  const id = `usr_${nanoid(14)}`;
  d.prepare("INSERT INTO users (id, email, name, picture, google_sub, created_at, last_login_at) VALUES (?, ?, ?, ?, ?, ?, ?)")
    .run(id, p.email, p.name ?? null, p.picture ?? null, p.sub, now(), now());
  return getUser(id)!;
}

export function setTotp(userId: string, secret: string | null, enabled: boolean) {
  open().prepare("UPDATE users SET totp_secret = ?, totp_enabled = ? WHERE id = ?").run(secret, enabled ? 1 : 0, userId);
}

// ---------------------------------------------------------------- saved designs
type SavedRow = { id: string; user_id: string; title: string; json: string; created_at: string; updated_at: string };
const toSaved = (r: SavedRow): SavedDesign => ({
  id: r.id, userId: r.user_id, title: r.title, design: JSON.parse(r.json), createdAt: r.created_at, updatedAt: r.updated_at,
});

export function listSavedDesigns(userId: string): SavedDesign[] {
  const rows = open().prepare("SELECT * FROM saved_designs WHERE user_id = ? ORDER BY updated_at DESC").all(userId) as SavedRow[];
  return rows.map(toSaved);
}
export function getSavedDesign(userId: string, id: string): SavedDesign | null {
  const r = open().prepare("SELECT * FROM saved_designs WHERE id = ? AND user_id = ?").get(id, userId) as SavedRow | undefined;
  return r ? toSaved(r) : null;
}
/** Create (no id) or update (id) one of a user's designs. Returns its id. */
export function upsertSavedDesign(userId: string, design: Design, id?: string): string {
  const d = open();
  const title = (design.title || "Untitled map").slice(0, 80);
  if (id && d.prepare("SELECT 1 FROM saved_designs WHERE id = ? AND user_id = ?").get(id, userId)) {
    d.prepare("UPDATE saved_designs SET title = ?, json = ?, updated_at = ? WHERE id = ?").run(title, JSON.stringify(design), now(), id);
    return id;
  }
  const newId = `sd_${nanoid(12)}`;
  d.prepare("INSERT INTO saved_designs (id, user_id, title, json, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)")
    .run(newId, userId, title, JSON.stringify(design), now(), now());
  return newId;
}
export function deleteSavedDesign(userId: string, id: string) {
  open().prepare("DELETE FROM saved_designs WHERE id = ? AND user_id = ?").run(id, userId);
}

// ---------------------------------------------------------------- route cache
export function getCachedRoute(key: string): unknown | undefined {
  const r = open().prepare("SELECT json FROM route_cache WHERE key = ?").get(key) as { json: string } | undefined;
  return r ? JSON.parse(r.json) : undefined;
}
export function putCachedRoute(key: string, value: unknown) {
  open().prepare("INSERT OR REPLACE INTO route_cache (key, json, created_at) VALUES (?, ?, ?)").run(key, JSON.stringify(value), now());
}
