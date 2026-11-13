import { describe, expect, it } from "vitest";
import { checkLinkToken, hashPassword, linkToken, passwordProblem, verifyPassword } from "../../src/lib/server/password";

describe("passwords", () => {
  it("hashes and verifies", async () => {
    const h = await hashPassword("correct horse battery");
    expect(h.startsWith("scrypt$")).toBe(true);
    expect(await verifyPassword("correct horse battery", h)).toBe(true);
    expect(await verifyPassword("wrong horse battery", h)).toBe(false);
    expect(await verifyPassword("anything", null)).toBe(false);
  });
  it("rejects weak passwords", () => {
    expect(passwordProblem("short", "a@b.co")).toMatch(/8/);
    expect(passwordProblem("password123", "a@b.co")).toMatch(/guess/);
    expect(passwordProblem("jane.doe", "jane.doe@x.com")).toMatch(/email/);
    expect(passwordProblem("a long travel phrase", "a@b.co")).toBeNull();
  });
});

describe("link tokens", () => {
  const user = { id: "usr_1", email: "a@b.co", passwordHash: "scrypt$old" };
  const load = async (u: typeof user | null) => u;
  it("verify links are tied to the email", async () => {
    const t = linkToken("verify", user, 1);
    expect(await checkLinkToken("verify", t, () => load(user))).toBeTruthy();
    expect(await checkLinkToken("verify", t, () => load({ ...user, email: "other@b.co" }))).toBeNull();
    expect(await checkLinkToken("reset", t, () => load(user))).toBeNull();
  });
  it("reset links stop working once the password changes", async () => {
    const t = linkToken("reset", user, 1);
    expect(await checkLinkToken("reset", t, () => load(user))).toBeTruthy();
    expect(await checkLinkToken("reset", t, () => load({ ...user, passwordHash: "scrypt$new" }))).toBeNull();
    expect(await checkLinkToken("reset", t.replace(/.$/, "x"), () => load(user))).toBeNull();
  });
  it("expired links fail", async () => {
    expect(await checkLinkToken("reset", linkToken("reset", user, -1), () => load(user))).toBeNull();
  });
});
