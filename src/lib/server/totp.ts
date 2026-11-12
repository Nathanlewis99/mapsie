import { TOTP, Secret } from "otpauth";

const totp = (secret: string, email: string) =>
  new TOTP({ issuer: "Mapsie", label: email, algorithm: "SHA1", digits: 6, period: 30, secret: Secret.fromBase32(secret) });

export const newTotpSecret = () => new Secret({ size: 20 }).base32;
export const totpUri = (secret: string, email: string) => totp(secret, email).toString();
/** Accepts the current code and one step either side (clock drift). */
export const checkTotp = (secret: string, email: string, code: string) =>
  totp(secret, email).validate({ token: code.replace(/\s/g, ""), window: 1 }) !== null;
