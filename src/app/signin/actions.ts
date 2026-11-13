"use server";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { currentUser, isAdminEmail, safeNext, startSession } from "@/lib/server/auth";
import { createPasswordUser, getUser, getUserByEmail, markEmailVerified, setPassword, touchLogin, type User } from "@/lib/server/db";
import { sendEmail } from "@/lib/server/email";
import { logError } from "@/lib/server/log";
import { publicUrl } from "@/lib/server/urls";
import {
  checkLinkToken, clearFailures, hashPassword, linkToken, passwordProblem, recordFailure, tooManyAttempts, validEmail, verifyPassword,
} from "@/lib/server/password";

export type FormState = { error?: string; sent?: boolean; email?: string; name?: string } | null;

const field = (f: FormData, k: string) => String(f.get(k) ?? "").trim();
const clientIp = async () => (await headers()).get("x-forwarded-for")?.split(",")[0]?.trim() || "unknown";
const SLOW = "Too many attempts. Please wait 15 minutes, or reset your password.";

/** Where to go after signing in. Admins heading for the admin area confirm with their authenticator app first. */
const landing = (user: User, next: string) =>
  user.emailVerified && isAdminEmail(user.email) && next.startsWith("/admin") ? "/admin/2fa?next=" + encodeURIComponent(next) : next;

async function sendVerifyEmail(user: User) {
  const link = `${publicUrl()}/api/auth/verify?token=${encodeURIComponent(linkToken("verify", user, 72))}`;
  try {
    await sendEmail({
      to: user.email,
      subject: "Confirm your email for Mapsie",
      text: `Welcome to Mapsie!\n\nConfirm your email so we can link your orders to your account:\n${link}\n\nThis link works for 3 days. If you didn't create an account, you can ignore this email.`,
      html: `<p>Welcome to Mapsie!</p><p>Confirm your email so we can link your orders to your account:</p><p><a href="${link}">Confirm my email</a></p><p style="color:#888">This link works for 3 days. If you didn't create an account, you can ignore this email.</p>`,
    });
  } catch (e) {
    void logError("auth.verify-email", e);
  }
}

export async function signInWithPassword(_: FormState, f: FormData): Promise<FormState> {
  const email = field(f, "email").toLowerCase();
  const password = String(f.get("password") ?? "");
  const next = safeNext(field(f, "next"));
  const ip = await clientIp();
  if (!validEmail(email) || !password) return { error: "Enter your email and password.", email };
  if (tooManyAttempts(email, ip)) return { error: SLOW, email };

  const user = await getUserByEmail(email);
  if (!(await verifyPassword(password, user?.passwordHash ?? null)) || !user) {
    recordFailure(email, ip);
    if (user && !user.passwordHash)
      return { error: "This account signs in with Google. Use “Continue with Google”, or choose “Forgot password” to add a password.", email };
    return { error: "That email and password don't match. Check them, or reset your password.", email };
  }
  clearFailures(email);
  await touchLogin(user.id);
  await startSession(user);
  redirect(landing(user, next));
}

export async function signUpWithPassword(_: FormState, f: FormData): Promise<FormState> {
  const email = field(f, "email").toLowerCase();
  const name = field(f, "name").slice(0, 80);
  const password = String(f.get("password") ?? "");
  const next = safeNext(field(f, "next"));
  const ip = await clientIp();
  if (!validEmail(email)) return { error: "Enter a valid email address.", email, name };
  const problem = passwordProblem(password, email);
  if (problem) return { error: problem, email, name };
  if (tooManyAttempts(email, ip)) return { error: SLOW, email, name };
  if (await getUserByEmail(email)) {
    recordFailure(email, ip);
    return { error: "There's already an account with this email. Sign in instead, or choose “Forgot password”.", email, name };
  }
  let user: User;
  try {
    user = await createPasswordUser({ email, name: name || undefined, passwordHash: await hashPassword(password) });
  } catch {
    // Two sign-ups for the same email at once: the unique index stops the second.
    return { error: "There's already an account with this email. Sign in instead.", email, name };
  }
  await sendVerifyEmail(user);
  await startSession(user);
  redirect(next);
}

/** Always says the same thing, so it can't be used to find out who has an account. */
export async function requestPasswordReset(_: FormState, f: FormData): Promise<FormState> {
  const email = field(f, "email").toLowerCase();
  if (!validEmail(email)) return { error: "Enter a valid email address.", email };
  const ip = await clientIp();
  // Counted separately from sign-in attempts, so someone locked out can still reset.
  if (tooManyAttempts(`reset:${email}`, ip)) return { sent: true, email };
  recordFailure(`reset:${email}`, ip); // limits how many reset emails one address can be sent
  const user = await getUserByEmail(email);
  if (user) {
    const link = `${publicUrl()}/signin/reset?token=${encodeURIComponent(linkToken("reset", user, 1))}`;
    try {
      await sendEmail({
        to: user.email,
        subject: "Reset your Mapsie password",
        text: `Someone (hopefully you) asked to ${user.passwordHash ? "reset" : "set"} the password for your Mapsie account.\n\nChoose a new password here:\n${link}\n\nThis link works for 1 hour, once. If it wasn't you, ignore this email: your account is unchanged.`,
        html: `<p>Someone (hopefully you) asked to ${user.passwordHash ? "reset" : "set"} the password for your Mapsie account.</p><p><a href="${link}">Choose a new password</a></p><p style="color:#888">This link works for 1 hour, once. If it wasn't you, ignore this email: your account is unchanged.</p>`,
      });
    } catch (e) {
      void logError("auth.reset-email", e);
    }
  }
  return { sent: true, email };
}

export async function resetPassword(_: FormState, f: FormData): Promise<FormState> {
  const token = field(f, "token");
  const password = String(f.get("password") ?? "");
  const user = await checkLinkToken("reset", token, getUser);
  if (!user) return { error: "This reset link has expired or was already used. Ask for a new one." };
  const problem = passwordProblem(password, user.email);
  if (problem) return { error: problem };
  await setPassword(user.id, await hashPassword(password));
  // They opened a link sent to the address, so they own it.
  if (!user.emailVerified) await markEmailVerified(user.id);
  clearFailures(user.email);
  await touchLogin(user.id);
  await startSession((await getUser(user.id))!);
  redirect("/account?password=1");
}

export async function resendVerification(): Promise<FormState> {
  const user = await currentUser();
  if (!user || user.emailVerified) return null;
  const ip = await clientIp();
  if (tooManyAttempts(`verify:${user.email}`, ip)) return { error: "We've sent a few already. Check your spam folder, or try again later." };
  recordFailure(`verify:${user.email}`, ip);
  await sendVerifyEmail(user);
  return { sent: true };
}
