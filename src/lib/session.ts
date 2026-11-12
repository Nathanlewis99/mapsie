import { SignJWT, jwtVerify } from "jose";

// Signed session cookie, readable from middleware (edge) and server code alike.
// SESSION_SECRET must be set in production (render.yaml generates one).
export const SESSION_COOKIE = "mapsie_session";
export const SESSION_DAYS = 30;
// Admin access needs the authenticator-app code again after this long.
export const ADMIN_MFA_HOURS = 12;

export interface SessionClaims {
  sub: string; // user id
  email: string;
  admin: boolean;
  mfaAt?: number; // epoch seconds when the admin last passed 2FA
}

const key = () => {
  const s = process.env.SESSION_SECRET;
  if (!s && process.env.NODE_ENV === "production") throw new Error("SESSION_SECRET is not set");
  return new TextEncoder().encode(s ?? "dev-only-session-secret-change-me-0123456789");
};

export async function signSession(c: SessionClaims): Promise<string> {
  return new SignJWT({ email: c.email, admin: c.admin, ...(c.mfaAt ? { mfaAt: c.mfaAt } : {}) })
    .setProtectedHeader({ alg: "HS256" })
    .setSubject(c.sub)
    .setIssuedAt()
    .setExpirationTime(`${SESSION_DAYS}d`)
    .sign(key());
}

export async function readSession(token: string | undefined): Promise<SessionClaims | null> {
  if (!token) return null;
  try {
    const { payload } = await jwtVerify(token, key(), { algorithms: ["HS256"] });
    return { sub: payload.sub!, email: String(payload.email), admin: !!payload.admin, mfaAt: payload.mfaAt as number | undefined };
  } catch {
    return null;
  }
}

export const adminMfaValid = (s: SessionClaims | null) =>
  !!s?.admin && !!s.mfaAt && Date.now() / 1000 - s.mfaAt < ADMIN_MFA_HOURS * 3600;

export const cookieOptions = {
  httpOnly: true,
  sameSite: "lax" as const,
  secure: process.env.NODE_ENV === "production",
  path: "/",
  maxAge: SESSION_DAYS * 24 * 3600,
};
