import { promises as fs } from "fs";
import path from "path";
import type { Design } from "../types";
import type { ShippingId, RegionId } from "../products";

// MVP storage: JSON files on disk. Swap for Supabase/Postgres + object storage
// before deploying (Vercel's disk is not persistent).
// DATA_DIR points at a persistent disk in production (see render.yaml).
const ROOT = process.env.DATA_DIR ?? path.join(process.cwd(), "data");
const dir = async (name: string) => {
  const d = path.join(ROOT, name);
  await fs.mkdir(d, { recursive: true });
  return d;
};
const safe = (id: string) => id.replace(/[^a-zA-Z0-9_-]/g, "");

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

async function readJson<T>(kind: string, id: string): Promise<T | null> {
  try {
    return JSON.parse(await fs.readFile(path.join(await dir(kind), `${safe(id)}.json`), "utf8"));
  } catch {
    return null;
  }
}
async function writeJson(kind: string, id: string, v: unknown) {
  await fs.writeFile(path.join(await dir(kind), `${safe(id)}.json`), JSON.stringify(v, null, 2));
}

export const saveDesign = (d: Design) => writeJson("designs", d.id, d);
export const getDesign = (id: string) => readJson<Design>("designs", id);
export const saveOrder = (o: Order) => writeJson("orders", o.id, o);
export const getOrder = (id: string) => readJson<Order>("orders", id);
export async function updateOrder(id: string, patch: Partial<Order>) {
  const o = await getOrder(id);
  if (!o) throw new Error("order not found");
  const n = { ...o, ...patch };
  await saveOrder(n);
  return n;
}
export const rendersDir = () => dir("renders");

export async function listOrders(): Promise<Order[]> {
  const d = await dir("orders");
  const files = (await fs.readdir(d)).filter((f) => f.endsWith(".json"));
  const all = await Promise.all(files.map((f) => fs.readFile(path.join(d, f), "utf8").then((t) => JSON.parse(t) as Order)));
  return all.sort((a, b) => b.createdAt.localeCompare(a.createdAt));
}
