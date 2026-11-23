// Mapsie mail connector: a remote MCP server that lets Claude read, draft and send email for one
// Google Workspace mailbox (admin@mapsie.shop, including its aliases such as nathan@mapsie.shop).
//
// How access works
//  - Claude (claude.ai → Settings → Connectors → Add custom connector) registers itself here and
//    sends you to /authorize. That redirects to Google's own sign-in. Only accounts listed in
//    ALLOWED_EMAILS are let in; anyone else is turned away.
//  - Google returns a refresh token for the mailbox. It is never stored here: it is encrypted
//    (AES-256-GCM, key from MCP_SECRET) inside the tokens we give Claude, which are signed and
//    expire (access 1 hour, refresh 30 days). Nothing to leak from this server's disk or database.
//  - To cut access off at once: change MCP_SECRET on Render (every token stops working), and/or
//    remove the app at myaccount.google.com → Security → Third-party connections.
//
// Environment (Render):
//   PUBLIC_URL            https://mail-mcp.mapsie.shop (or the onrender.com address)
//   MCP_SECRET            long random value (Render: "Generate")
//   GOOGLE_CLIENT_ID      OAuth client (Web application) in the DayzeOut Google Cloud project,
//   GOOGLE_CLIENT_SECRET  consent screen "Internal", Gmail API enabled.
//                         Authorised redirect URI: <PUBLIC_URL>/google/callback
//   ALLOWED_EMAILS        admin@mapsie.shop  (comma-separated)
//   ALLOWED_REDIRECT_HOSTS claude.ai,claude.com  (where Claude's sign-in may return to)
import express from "express";
import { createCipheriv, createDecipheriv, createHash, createHmac, randomBytes, timingSafeEqual } from "node:crypto";
import { z } from "zod";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { mcpAuthRouter, getOAuthProtectedResourceMetadataUrl } from "@modelcontextprotocol/sdk/server/auth/router.js";
import { requireBearerAuth } from "@modelcontextprotocol/sdk/server/auth/middleware/bearerAuth.js";
import { InvalidGrantError, InvalidTokenError, InvalidRequestError } from "@modelcontextprotocol/sdk/server/auth/errors.js";

const env = (k, d) => {
  const v = process.env[k] ?? d;
  if (v === undefined || v === "") throw new Error(`${k} is not set`);
  return v;
};
export const config = () => ({
  publicUrl: env("PUBLIC_URL").replace(/\/$/, ""),
  secret: env("MCP_SECRET"),
  googleId: env("GOOGLE_CLIENT_ID"),
  googleSecret: env("GOOGLE_CLIENT_SECRET"),
  allowed: env("ALLOWED_EMAILS").split(",").map((e) => e.trim().toLowerCase()).filter(Boolean),
  redirectHosts: (process.env.ALLOWED_REDIRECT_HOSTS ?? "claude.ai,claude.com").split(",").map((h) => h.trim().toLowerCase()).filter(Boolean),
});
const GMAIL_SCOPE = "https://www.googleapis.com/auth/gmail.modify"; // read, label, draft and send (no permanent delete)
const SETTINGS_SCOPE = "https://www.googleapis.com/auth/gmail.settings.basic"; // list "send mail as" addresses

// ------------------------------------------------------------ signing and sealing (no database)
const b64 = (b) => Buffer.from(b).toString("base64url");
const keyFor = (purpose) => createHash("sha256").update(`${config().secret}:${purpose}`).digest();

/** A compact signed token: base64url(json).hmac. Checks type and expiry. */
export function sign(payload, type, ttlSeconds) {
  const body = b64(JSON.stringify({ ...payload, typ: type, exp: Math.floor(Date.now() / 1000) + ttlSeconds }));
  return `${body}.${createHmac("sha256", keyFor("sign")).update(body).digest("base64url")}`;
}
export function verify(token, type) {
  const [body, mac] = String(token ?? "").split(".");
  if (!body || !mac) return null;
  const want = createHmac("sha256", keyFor("sign")).update(body).digest();
  const got = Buffer.from(mac, "base64url");
  if (got.length !== want.length || !timingSafeEqual(got, want)) return null;
  try {
    const p = JSON.parse(Buffer.from(body, "base64url").toString("utf8"));
    if (p.typ !== type || !(p.exp > Date.now() / 1000)) return null;
    return p;
  } catch {
    return null;
  }
}
export function seal(text) {
  const iv = randomBytes(12);
  const c = createCipheriv("aes-256-gcm", keyFor("seal"), iv);
  const enc = Buffer.concat([c.update(text, "utf8"), c.final()]);
  return [iv, c.getAuthTag(), enc].map(b64).join(".");
}
export function unseal(sealed) {
  const [iv, tag, enc] = String(sealed).split(".").map((x) => Buffer.from(x, "base64url"));
  const d = createDecipheriv("aes-256-gcm", keyFor("seal"), iv);
  d.setAuthTag(tag);
  return Buffer.concat([d.update(enc), d.final()]).toString("utf8");
}

// ------------------------------------------------------------ OAuth for Claude (we are the authorisation server)
export function redirectAllowed(uri) {
  try {
    const u = new URL(uri);
    const host = u.hostname.toLowerCase();
    return u.protocol === "https:" && config().redirectHosts.some((h) => host === h || host.endsWith(`.${h}`));
  } catch {
    return false;
  }
}

// Clients register themselves (Claude does this when you add the connector). Their details are
// signed into the client id itself, so nothing needs storing and restarts don't log you out.
export const clientsStore = {
  async getClient(clientId) {
    const p = verify(clientId, "client");
    return p ? { ...p.meta, client_id: clientId, client_id_issued_at: p.iat } : undefined;
  },
  async registerClient(meta) {
    const uris = meta.redirect_uris ?? [];
    if (!uris.length || !uris.every(redirectAllowed)) throw new InvalidRequestError("Only Claude may connect to this server");
    const clean = { redirect_uris: uris, client_name: String(meta.client_name ?? "client").slice(0, 80), token_endpoint_auth_method: "none", grant_types: ["authorization_code", "refresh_token"], response_types: ["code"] };
    const iat = Math.floor(Date.now() / 1000);
    const clientId = sign({ meta: clean, iat, n: randomBytes(6).toString("base64url") }, "client", 5 * 365 * 24 * 3600);
    return { ...clean, client_id: clientId, client_id_issued_at: iat };
  },
};

const googleAuthUrl = (state) =>
  `https://accounts.google.com/o/oauth2/v2/auth?${new URLSearchParams({
    client_id: config().googleId,
    redirect_uri: `${config().publicUrl}/google/callback`,
    response_type: "code",
    scope: `openid email ${GMAIL_SCOPE} ${SETTINGS_SCOPE}`,
    access_type: "offline",
    prompt: "consent",
    login_hint: config().allowed[0] ?? "",
    state,
  })}`;

export function issueTokens(email, googleRefresh, clientId) {
  const g = seal(googleRefresh);
  return {
    access_token: sign({ sub: email, g, cid: clientId }, "access", 3600),
    token_type: "bearer",
    expires_in: 3600,
    refresh_token: sign({ sub: email, g, cid: clientId }, "refresh", 30 * 24 * 3600),
    scope: "mail",
  };
}

export const provider = {
  clientsStore,
  async authorize(client, params, res) {
    if (!client.redirect_uris.includes(params.redirectUri)) throw new InvalidRequestError("Unregistered redirect URI");
    const state = sign({ cid: client.client_id, ru: params.redirectUri, cc: params.codeChallenge, st: params.state ?? "" }, "pending", 15 * 60);
    res.redirect(googleAuthUrl(state));
  },
  async challengeForAuthorizationCode(client, code) {
    const p = verify(code, "code");
    if (!p || p.cid !== client.client_id) throw new InvalidGrantError("Invalid or expired code");
    return p.cc;
  },
  async exchangeAuthorizationCode(client, code, _verifier, redirectUri) {
    const p = verify(code, "code");
    if (!p || p.cid !== client.client_id || (redirectUri && redirectUri !== p.ru)) throw new InvalidGrantError("Invalid or expired code");
    if (!config().allowed.includes(p.sub)) throw new InvalidGrantError("Not allowed");
    return issueTokens(p.sub, unseal(p.g), client.client_id);
  },
  async exchangeRefreshToken(client, refreshToken) {
    const p = verify(refreshToken, "refresh");
    if (!p || p.cid !== client.client_id || !config().allowed.includes(p.sub)) throw new InvalidGrantError("Please reconnect");
    return issueTokens(p.sub, unseal(p.g), client.client_id);
  },
  async verifyAccessToken(token) {
    const p = verify(token, "access");
    if (!p || !config().allowed.includes(p.sub)) throw new InvalidTokenError("Invalid or expired token");
    return { token, clientId: p.cid, scopes: ["mail"], expiresAt: p.exp, extra: { email: p.sub, g: p.g } };
  },
};

// ------------------------------------------------------------ Gmail
const accessCache = new Map(); // hash(sealed refresh) → { token, until }
async function googleAccess(sealedRefresh) {
  const k = createHash("sha256").update(sealedRefresh).digest("hex");
  const hit = accessCache.get(k);
  if (hit && hit.until > Date.now() + 60_000) return hit.token;
  const r = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ refresh_token: unseal(sealedRefresh), client_id: config().googleId, client_secret: config().googleSecret, grant_type: "refresh_token" }),
    signal: AbortSignal.timeout(15_000),
  });
  const j = await r.json();
  if (!r.ok || !j.access_token) throw new Error(`Google sign-in has expired or was removed: please reconnect the Mapsie mail connector (${j.error ?? r.status})`);
  if (accessCache.size > 100) accessCache.clear();
  accessCache.set(k, { token: j.access_token, until: Date.now() + (j.expires_in ?? 3600) * 1000 });
  return j.access_token;
}

async function gmail(auth, path, init = {}) {
  const r = await fetch(`https://gmail.googleapis.com/gmail/v1/users/me/${path}`, {
    ...init,
    headers: { authorization: `Bearer ${await googleAccess(auth.extra.g)}`, "content-type": "application/json", ...(init.headers ?? {}) },
    signal: AbortSignal.timeout(30_000),
  });
  const text = await r.text();
  if (!r.ok) {
    let msg = text.slice(0, 400);
    try {
      msg = JSON.parse(text).error?.message ?? msg;
    } catch {}
    throw new Error(`Gmail ${r.status}: ${msg}`);
  }
  return text ? JSON.parse(text) : {};
}

const header = (m, name) => m.payload?.headers?.find((h) => h.name.toLowerCase() === name.toLowerCase())?.value ?? "";
const decode = (data) => Buffer.from(String(data ?? "").replace(/-/g, "+").replace(/_/g, "/"), "base64").toString("utf8");
export function htmlToText(html) {
  return html
    .replace(/<(script|style)[\s\S]*?<\/\1>/gi, "")
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<\/(p|div|tr|li|h\d)>/gi, "\n")
    .replace(/<[^>]+>/g, "")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}
/** The readable body of a message: plain text if there is one, else the HTML as text. Plus attachment names. */
export function bodyOf(payload) {
  let plain = "";
  let html = "";
  const attachments = [];
  const walk = (p) => {
    if (!p) return;
    if (p.filename && p.body?.attachmentId) attachments.push({ name: p.filename, type: p.mimeType, size: p.body.size });
    else if (p.mimeType === "text/plain" && p.body?.data && !plain) plain = decode(p.body.data);
    else if (p.mimeType === "text/html" && p.body?.data && !html) html = decode(p.body.data);
    for (const c of p.parts ?? []) walk(c);
  };
  walk(payload);
  return { text: (plain || htmlToText(html)).slice(0, 20_000), attachments };
}

const summary = (m) => ({ id: m.id, threadId: m.threadId, date: header(m, "Date"), from: header(m, "From"), to: header(m, "To"), cc: header(m, "Cc") || undefined, subject: header(m, "Subject"), snippet: m.snippet, labels: m.labelIds });

/** RFC 2822 message, base64url, with UTF-8 subject. Rejects header injection in addresses and subject. */
export function buildRaw({ from, to, cc, bcc, subject, body, inReplyTo, references }) {
  const safe = (v) => {
    if (/[\r\n]/.test(v ?? "")) throw new Error("Line breaks aren't allowed in addresses or the subject");
    return v;
  };
  const enc = (s) => (/^[\x20-\x7e]*$/.test(s) ? s : `=?UTF-8?B?${Buffer.from(s, "utf8").toString("base64")}?=`);
  const lines = [
    from && `From: ${safe(from)}`,
    `To: ${safe(to)}`,
    cc && `Cc: ${safe(cc)}`,
    bcc && `Bcc: ${safe(bcc)}`,
    `Subject: ${enc(safe(subject ?? ""))}`,
    inReplyTo && `In-Reply-To: ${safe(inReplyTo)}`,
    references && `References: ${safe(references)}`,
    "MIME-Version: 1.0",
    'Content-Type: text/plain; charset="UTF-8"',
    "Content-Transfer-Encoding: base64",
    "",
    Buffer.from(body ?? "", "utf8").toString("base64").replace(/(.{76})/g, "$1\r\n"),
  ].filter((l) => l !== undefined && l !== null && l !== false);
  return Buffer.from(lines.join("\r\n"), "utf8").toString("base64url");
}

// ------------------------------------------------------------ the MCP tools
const ok = (data) => ({ content: [{ type: "text", text: typeof data === "string" ? data : JSON.stringify(data, null, 2) }] });

function mailServer(auth) {
  const s = new McpServer({ name: "mapsie-mail", version: "1.0.0" });

  s.registerTool(
    "search_threads",
    {
      title: "Search email",
      description: "Search the Mapsie mailbox (admin@mapsie.shop and its aliases) with Gmail search syntax, e.g. 'in:inbox is:unread', 'from:someone@example.com newer_than:7d', 'subject:partner'. Returns the latest message of each thread.",
      inputSchema: { query: z.string().max(500).default("in:inbox"), maxResults: z.number().int().min(1).max(25).default(10), pageToken: z.string().optional() },
      annotations: { readOnlyHint: true },
    },
    async ({ query, maxResults, pageToken }) => {
      const list = await gmail(auth, `threads?${new URLSearchParams({ q: query, maxResults: String(maxResults), ...(pageToken ? { pageToken } : {}) })}`);
      const threads = await Promise.all(
        (list.threads ?? []).map(async (t) => {
          const full = await gmail(auth, `threads/${t.id}?format=metadata&metadataHeaders=From&metadataHeaders=To&metadataHeaders=Cc&metadataHeaders=Subject&metadataHeaders=Date`);
          const last = full.messages?.[full.messages.length - 1];
          return { threadId: t.id, messages: full.messages?.length ?? 0, latest: last ? summary(last) : undefined };
        }),
      );
      return ok({ threads, nextPageToken: list.nextPageToken, estimate: list.resultSizeEstimate });
    },
  );

  s.registerTool(
    "get_thread",
    {
      title: "Read a thread",
      description: "Read every message in a thread: headers, the text of each message (HTML converted to text, up to 20,000 characters each) and attachment names.",
      inputSchema: { threadId: z.string().regex(/^[a-zA-Z0-9]+$/) },
      annotations: { readOnlyHint: true },
    },
    async ({ threadId }) => {
      const t = await gmail(auth, `threads/${threadId}?format=full`);
      return ok({ threadId, messages: (t.messages ?? []).map((m) => ({ ...summary(m), messageId: header(m, "Message-ID"), ...bodyOf(m.payload) })) });
    },
  );

  s.registerTool(
    "list_send_as",
    { title: "Addresses I can send from", description: "The addresses this mailbox can send as (e.g. nathan@mapsie.shop), for the 'from' of a draft.", inputSchema: {}, annotations: { readOnlyHint: true } },
    async () => {
      const r = await gmail(auth, "settings/sendAs");
      return ok((r.sendAs ?? []).map((a) => ({ address: a.sendAsEmail, name: a.displayName, default: !!a.isDefault, verified: a.verificationStatus ?? "accepted" })));
    },
  );

  s.registerTool(
    "create_draft",
    {
      title: "Write a draft",
      description: "Save a plain-text email as a draft (it is NOT sent). To reply, pass replyToMessageId (a message id from get_thread): it goes in the same thread with the right subject and headers. 'from' can be any send-as address from list_send_as.",
      inputSchema: {
        to: z.string().max(1000),
        cc: z.string().max(1000).optional(),
        bcc: z.string().max(1000).optional(),
        subject: z.string().max(300).optional(),
        body: z.string().max(50_000),
        from: z.string().max(200).optional(),
        replyToMessageId: z.string().regex(/^[a-zA-Z0-9]+$/).optional(),
      },
    },
    async ({ to, cc, bcc, subject, body, from, replyToMessageId }) => {
      let threadId;
      let inReplyTo;
      let references;
      if (replyToMessageId) {
        const m = await gmail(auth, `messages/${replyToMessageId}?format=metadata&metadataHeaders=Subject&metadataHeaders=Message-ID&metadataHeaders=References`);
        threadId = m.threadId;
        inReplyTo = header(m, "Message-ID");
        references = [header(m, "References"), inReplyTo].filter(Boolean).join(" ");
        const orig = header(m, "Subject");
        subject = subject ?? (/^re:/i.test(orig) ? orig : `Re: ${orig}`);
      }
      const raw = buildRaw({ from, to, cc, bcc, subject: subject ?? "", body, inReplyTo, references });
      const d = await gmail(auth, "drafts", { method: "POST", body: JSON.stringify({ message: { raw, ...(threadId ? { threadId } : {}) } }) });
      return ok({ draftId: d.id, messageId: d.message?.id, threadId: d.message?.threadId, note: "Saved as a draft. Nothing has been sent." });
    },
  );

  s.registerTool(
    "send_draft",
    {
      title: "Send a draft",
      description: "Send a draft made with create_draft. Only send when the person has approved this exact email.",
      inputSchema: { draftId: z.string().regex(/^[a-zA-Z0-9_-]+$/) },
      annotations: { destructiveHint: false, openWorldHint: true },
    },
    async ({ draftId }) => {
      const r = await gmail(auth, "drafts/send", { method: "POST", body: JSON.stringify({ id: draftId }) });
      return ok({ sent: true, messageId: r.id, threadId: r.threadId });
    },
  );

  s.registerTool(
    "list_drafts",
    { title: "List drafts", description: "Drafts waiting to be sent.", inputSchema: { maxResults: z.number().int().min(1).max(25).default(10) }, annotations: { readOnlyHint: true } },
    async ({ maxResults }) => {
      const r = await gmail(auth, `drafts?maxResults=${maxResults}`);
      const drafts = await Promise.all((r.drafts ?? []).map(async (d) => {
        const full = await gmail(auth, `drafts/${d.id}?format=metadata`);
        return { draftId: d.id, ...summary(full.message ?? {}) };
      }));
      return ok(drafts);
    },
  );

  s.registerTool(
    "label_thread",
    {
      title: "Tidy a thread",
      description: "Add or remove labels on a thread. Archive = remove 'INBOX'; mark read = remove 'UNREAD'; star = add 'STARRED'. Use list_labels for custom label ids.",
      inputSchema: { threadId: z.string().regex(/^[a-zA-Z0-9]+$/), add: z.array(z.string().max(100)).max(10).default([]), remove: z.array(z.string().max(100)).max(10).default([]) },
    },
    async ({ threadId, add, remove }) => {
      await gmail(auth, `threads/${threadId}/modify`, { method: "POST", body: JSON.stringify({ addLabelIds: add, removeLabelIds: remove }) });
      return ok({ threadId, added: add, removed: remove });
    },
  );

  s.registerTool(
    "list_labels",
    { title: "List labels", description: "The mailbox's labels and their ids.", inputSchema: {}, annotations: { readOnlyHint: true } },
    async () => ok(((await gmail(auth, "labels")).labels ?? []).map((l) => ({ id: l.id, name: l.name, type: l.type }))),
  );

  return s;
}

// ------------------------------------------------------------ the web server
export function createApp() {
  const c = config();
  const app = express();
  app.set("trust proxy", 1); // behind Render's proxy: rate limits see the real visitor
  const issuer = new URL(c.publicUrl);
  const mcpUrl = new URL(`${c.publicUrl}/mcp`);

  app.get("/", (_req, res) => res.type("text").send("Mapsie mail connector. Add it in Claude: Settings → Connectors → Add custom connector, with the URL ending /mcp."));
  app.get("/health", (_req, res) => res.json({ ok: true }));

  app.use(mcpAuthRouter({ provider, issuerUrl: issuer, resourceServerUrl: mcpUrl, scopesSupported: ["mail"], resourceName: "Mapsie mail" }));

  // Back from Google's sign-in: check who it is, then hand Claude a one-time code.
  app.get("/google/callback", async (req, res) => {
    const pending = verify(req.query.state, "pending");
    if (!pending) return res.status(400).type("text").send("This sign-in link has expired. Please try connecting again from Claude.");
    if (req.query.error || !req.query.code) return res.status(400).type("text").send("Google sign-in was cancelled.");
    const r = await fetch("https://oauth2.googleapis.com/token", {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ code: String(req.query.code), client_id: c.googleId, client_secret: c.googleSecret, redirect_uri: `${c.publicUrl}/google/callback`, grant_type: "authorization_code" }),
      signal: AbortSignal.timeout(15_000),
    });
    const j = await r.json();
    if (!r.ok || !j.id_token) return res.status(400).type("text").send("Google sign-in failed. Please try again.");
    // The id token comes straight from Google over TLS in this server-to-server call, so decoding it is enough.
    const claims = JSON.parse(Buffer.from(j.id_token.split(".")[1], "base64url").toString("utf8"));
    const email = String(claims.email ?? "").toLowerCase();
    if (!claims.email_verified || !c.allowed.includes(email)) return res.status(403).type("text").send(`${email || "That account"} isn't allowed to use this connector.`);
    const scopes = String(j.scope ?? "").split(" ");
    if (!scopes.includes(GMAIL_SCOPE)) return res.status(400).type("text").send("Please tick the Gmail permission on Google's screen. Try connecting again from Claude.");
    if (!j.refresh_token) return res.status(400).type("text").send("Google didn't return long-lived access. Remove the app at myaccount.google.com → Security → Third-party connections, then connect again.");
    const code = sign({ cid: pending.cid, ru: pending.ru, cc: pending.cc, sub: email, g: seal(j.refresh_token) }, "code", 5 * 60);
    const back = new URL(pending.ru);
    back.searchParams.set("code", code);
    if (pending.st) back.searchParams.set("state", pending.st);
    res.redirect(back.toString());
  });

  // The MCP endpoint itself. Stateless: a fresh server per request.
  const bearer = requireBearerAuth({ verifier: provider, resourceMetadataUrl: getOAuthProtectedResourceMetadataUrl(mcpUrl) });
  app.post("/mcp", bearer, express.json({ limit: "2mb" }), async (req, res) => {
    const server = mailServer(req.auth);
    const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined, enableJsonResponse: true });
    res.on("close", () => {
      transport.close();
      server.close();
    });
    try {
      await server.connect(transport);
      await transport.handleRequest(req, res, req.body);
    } catch (e) {
      console.error(JSON.stringify({ level: "error", scope: "mcp", message: String(e?.message ?? e).slice(0, 300) }));
      if (!res.headersSent) res.status(500).json({ jsonrpc: "2.0", error: { code: -32603, message: "Internal error" }, id: null });
    }
  });
  app.get("/mcp", bearer, (_req, res) => res.status(405).set("allow", "POST").json({ jsonrpc: "2.0", error: { code: -32000, message: "Use POST" }, id: null }));
  app.delete("/mcp", bearer, (_req, res) => res.status(405).set("allow", "POST").end());
  return app;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  config(); // fail fast if anything is missing
  const port = Number(process.env.PORT ?? 10000);
  createApp().listen(port, () => console.log(JSON.stringify({ level: "info", scope: "mail-mcp", message: `listening on ${port}` })));
}
