import { createHmac, randomBytes, scrypt, timingSafeEqual } from "node:crypto";

// Email and password sign-in: hashing, sign-in attempt limits, and signed links
// for verifying an email address and resetting a password.

const N = 16384, R = 8, P = 1, KEYLEN = 64;
const derive = (pw: string, salt: Buffer, n = N, r = R, p = P) =>
  new Promise<Buffer>((res, rej) =>
    scrypt(pw.normalize("NFKC"), salt, KEYLEN, { N: n, r, p, maxmem: 64 * 1024 * 1024 }, (e, k) => (e ? rej(e) : res(k))),
  );

/** "scrypt$N$r$p$salt$hash", so the cost can be raised later without breaking old hashes. */
export async function hashPassword(pw: string): Promise<string> {
  const salt = randomBytes(16);
  return `scrypt$${N}$${R}$${P}$${salt.toString("base64url")}$${(await derive(pw, salt)).toString("base64url")}`;
}

export async function verifyPassword(pw: string, stored: string | null): Promise<boolean> {
  if (!stored) {
    // Spend the same time as a real check, so response times don't reveal which emails have passwords.
    await derive(pw, Buffer.alloc(16));
    return false;
  }
  const [kind, n, r, p, salt, hash] = stored.split("$");
  if (kind !== "scrypt" || !salt || !hash) return false;
  const want = Buffer.from(hash, "base64url");
  const got = await derive(pw, Buffer.from(salt, "base64url"), Number(n), Number(r), Number(p));
  return got.length === want.length && timingSafeEqual(got, want);
}

export const MIN_PASSWORD = 8;
/** Why the password isn't acceptable, or null. */
export function passwordProblem(pw: string, email: string): string | null {
  if (pw.length < MIN_PASSWORD) return `Use at least ${MIN_PASSWORD} characters.`;
  if (pw.length > 200) return "That password is too long.";
  const low = pw.toLowerCase();
  if (low === email.toLowerCase() || low === email.split("@")[0].toLowerCase()) return "Don't use your email as your password.";
  if (/^(.)\1+$/.test(pw) || COMMON.has(low)) return "That password is too easy to guess. Try a short phrase.";
  return null;
}
const COMMON = new Set([
  "password", "password1", "password123", "12345678", "123456789", "1234567890", "qwerty123", "qwertyuiop", "iloveyou", "11111111",
  "abc12345", "letmein1", "welcome1", "mapsie123", "passw0rd", "football", "baseball", "sunshine", "princess", "admin123",
]);

export const validEmail = (e: string) => e.length <= 254 && /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(e);

// ---------------------------------------------------------------- attempt limits
// Per email and per IP, in this server's memory: enough to stop password guessing.
const WINDOW = 15 * 60 * 1000;
const LIMITS = { email: 8, ip: 30 };
const hits = new Map<string, number[]>();
const recent = (k: string) => (hits.get(k) ?? []).filter((x) => Date.now() - x < WINDOW);

export function tooManyAttempts(email: string, ip: string): boolean {
  return recent(`e:${email.toLowerCase()}`).length >= LIMITS.email || recent(`i:${ip}`).length >= LIMITS.ip;
}
export function recordFailure(email: string, ip: string) {
  if (hits.size > 50_000) hits.clear();
  for (const k of [`e:${email.toLowerCase()}`, `i:${ip}`]) hits.set(k, [...recent(k), Date.now()]);
}
export const clearFailures = (email: string) => void hits.delete(`e:${email.toLowerCase()}`);

// ---------------------------------------------------------------- signed links
const secret = () => process.env.SESSION_SECRET ?? "dev-only-session-secret-change-me-0123456789";
const mac = (s: string) => createHmac("sha256", secret()).update(s).digest("base64url");
const same = (a: string, b: string) => a.length === b.length && timingSafeEqual(Buffer.from(a), Buffer.from(b));
type LinkUser = { id: string; email: string; passwordHash: string | null };
const bindFor = (kind: "verify" | "reset", u: LinkUser) => (kind === "reset" ? (u.passwordHash ?? "") : u.email.toLowerCase());

/**
 * A link token for one user: "verify" confirms the email they signed up with, "reset" sets a
 * new password. Reset tokens are tied to the current password hash, so each works only once:
 * after the password changes, older links stop working.
 */
export function linkToken(kind: "verify" | "reset", user: LinkUser, hours: number) {
  const exp = Math.floor(Date.now() / 1000) + hours * 3600;
  return `${user.id}.${exp}.${mac(`${kind}:${user.id}:${exp}:${bindFor(kind, user)}`)}`;
}

/** The user the token belongs to, if it's genuine, unexpired and still current. */
export async function checkLinkToken<U extends LinkUser>(kind: "verify" | "reset", token: string, load: (id: string) => Promise<U | null>) {
  const [id, exp, sig] = token.split(".");
  if (!id || !exp || !sig || !(Number(exp) > Date.now() / 1000)) return null;
  const u = await load(id);
  if (!u) return null;
  return same(sig, mac(`${kind}:${id}:${exp}:${bindFor(kind, u)}`)) ? u : null;
}
