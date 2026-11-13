import { cookies } from "next/headers";
import { Google } from "arctic";
import { readSession, signSession, SESSION_COOKIE, cookieOptions, type SessionClaims } from "../session";
import { getUser, type User } from "./db";
import { publicUrl } from "./urls";

/** Emails that get the admin role (comma-separated). */
export const adminEmails = () =>
  (process.env.ADMIN_EMAILS ?? "admin@mapsie.shop").split(",").map((e) => e.trim().toLowerCase()).filter(Boolean);
export const isAdminEmail = (email: string) => adminEmails().includes(email.toLowerCase());

export const googleConfigured = () => !!(process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET);

export function google() {
  return new Google(process.env.GOOGLE_CLIENT_ID!, process.env.GOOGLE_CLIENT_SECRET!, `${publicUrl()}/api/auth/google/callback`);
}

export async function getSession(): Promise<SessionClaims | null> {
  return readSession((await cookies()).get(SESSION_COOKIE)?.value);
}

/** The signed-in user, or null. */
export async function currentUser(): Promise<User | null> {
  const s = await getSession();
  return s ? getUser(s.sub) : null;
}

export async function startSession(user: User, mfaAt?: number) {
  // Admin rights need an email the person has proved they own: a password account can't claim one just by typing it.
  const token = await signSession({ sub: user.id, email: user.email, admin: user.emailVerified && isAdminEmail(user.email), mfaAt });
  (await cookies()).set(SESSION_COOKIE, token, cookieOptions);
}

export async function endSession() {
  (await cookies()).delete(SESSION_COOKIE);
}

/** Only allow same-site relative paths after sign-in. */
export const safeNext = (next: string | null | undefined) => (next && /^\/(?!\/)/.test(next) ? next : "/account");
