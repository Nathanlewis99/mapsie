// node --test (from services/mail-mcp)
import { test } from "node:test";
import assert from "node:assert/strict";
process.env.PUBLIC_URL = "http://localhost:4799";
process.env.MCP_SECRET = "test-secret-test-secret-test-secret";
process.env.GOOGLE_CLIENT_ID = "gid";
process.env.GOOGLE_CLIENT_SECRET = "gsecret";
process.env.ALLOWED_EMAILS = "admin@mapsie.shop";
const m = await import("./server.mjs");

test("signed tokens can't be forged, retyped or kept past expiry", () => {
  const t = m.sign({ sub: "admin@mapsie.shop" }, "access", 60);
  assert.equal(m.verify(t, "access").sub, "admin@mapsie.shop");
  assert.equal(m.verify(t, "refresh"), null);
  const [body] = t.split(".");
  const forged = Buffer.from(JSON.stringify({ sub: "evil@x.com", typ: "access", exp: 9e9 })).toString("base64url");
  assert.equal(m.verify(`${forged}.${t.split(".")[1]}`, "access"), null);
  assert.equal(m.verify(`${body}.AAAA`, "access"), null);
  assert.equal(m.verify(m.sign({}, "access", -1), "access"), null);
});

test("the Google refresh token is encrypted inside our tokens", () => {
  const s = m.seal("1//google-refresh-token");
  assert.ok(!s.includes("google-refresh"));
  assert.equal(m.unseal(s), "1//google-refresh-token");
  assert.throws(() => m.unseal(s.slice(0, -3) + "AAA"));
});

test("only Claude's sign-in pages may register", async () => {
  assert.ok(m.redirectAllowed("https://claude.ai/api/mcp/auth_callback"));
  assert.ok(m.redirectAllowed("https://claude.com/api/mcp/auth_callback"));
  assert.ok(!m.redirectAllowed("https://claude.ai.evil.com/cb"));
  assert.ok(!m.redirectAllowed("http://claude.ai/cb"));
  await assert.rejects(() => m.clientsStore.registerClient({ redirect_uris: ["https://evil.com/cb"] }));
  const c = await m.clientsStore.registerClient({ redirect_uris: ["https://claude.ai/api/mcp/auth_callback"], client_name: "Claude" });
  assert.deepEqual((await m.clientsStore.getClient(c.client_id)).redirect_uris, ["https://claude.ai/api/mcp/auth_callback"]);
  assert.equal(await m.clientsStore.getClient(c.client_id + "x"), undefined);
});

test("emails can't smuggle extra headers", () => {
  assert.throws(() => m.buildRaw({ to: "a@b.com\r\nBcc: x@y.com", subject: "hi", body: "x" }));
  const raw = Buffer.from(m.buildRaw({ from: "Nathan <nathan@mapsie.shop>", to: "a@b.com", subject: "Café ☕", body: "Hello" }), "base64url").toString();
  assert.match(raw, /From: Nathan <nathan@mapsie.shop>/);
  assert.match(raw, /Subject: =\?UTF-8\?B\?/);
});

test("reads plain text, or HTML as text, and lists attachments", () => {
  const b64 = (s) => Buffer.from(s).toString("base64url");
  const r = m.bodyOf({ mimeType: "multipart/mixed", parts: [{ mimeType: "text/html", body: { data: b64("<p>Hi&nbsp;there</p><script>x</script>") } }, { filename: "a.pdf", mimeType: "application/pdf", body: { attachmentId: "1", size: 10 } }] });
  assert.equal(r.text, "Hi there");
  assert.deepEqual(r.attachments, [{ name: "a.pdf", type: "application/pdf", size: 10 }]);
});

test("the HTTP endpoints: discovery, registration, sign-in redirect, and a locked MCP endpoint", async () => {
  const server = m.createApp().listen(4799);
  const base = "http://localhost:4799";
  try {
    const meta = await (await fetch(`${base}/.well-known/oauth-authorization-server`)).json();
    assert.equal(meta.issuer, `${base}/`);
    assert.ok(meta.registration_endpoint);
    const prm = await fetch(`${base}/.well-known/oauth-protected-resource/mcp`);
    assert.equal(prm.status, 200);
    const bad = await fetch(meta.registration_endpoint, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ redirect_uris: ["https://evil.com/cb"], token_endpoint_auth_method: "none" }) });
    assert.equal(bad.status, 400);
    const reg = await (await fetch(meta.registration_endpoint, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ redirect_uris: ["https://claude.ai/api/mcp/auth_callback"], client_name: "Claude", token_endpoint_auth_method: "none" }) })).json();
    assert.ok(reg.client_id);
    const auth = await fetch(`${meta.authorization_endpoint}?${new URLSearchParams({ client_id: reg.client_id, redirect_uri: "https://claude.ai/api/mcp/auth_callback", response_type: "code", code_challenge: "x".repeat(43), code_challenge_method: "S256", state: "s1" })}`, { redirect: "manual" });
    assert.equal(auth.status, 302);
    assert.match(auth.headers.get("location"), /^https:\/\/accounts\.google\.com\/o\/oauth2\/v2\/auth\?/);
    const init = { jsonrpc: "2.0", id: 1, method: "tools/list", params: {} };
    const h = { "content-type": "application/json", accept: "application/json, text/event-stream" };
    assert.equal((await fetch(`${base}/mcp`, { method: "POST", headers: h, body: JSON.stringify(init) })).status, 401);
    assert.equal((await fetch(`${base}/mcp`, { method: "POST", headers: { ...h, authorization: "Bearer forged.token" }, body: JSON.stringify(init) })).status, 401);
    const someoneElse = m.issueTokens("evil@example.com", "r", reg.client_id).access_token;
    assert.equal((await fetch(`${base}/mcp`, { method: "POST", headers: { ...h, authorization: `Bearer ${someoneElse}` }, body: JSON.stringify(init) })).status, 401);
    const good = m.issueTokens("admin@mapsie.shop", "r", reg.client_id).access_token;
    const list = await (await fetch(`${base}/mcp`, { method: "POST", headers: { ...h, authorization: `Bearer ${good}` }, body: JSON.stringify(init) })).json();
    assert.deepEqual(list.result.tools.map((t) => t.name).sort(), ["create_draft", "get_thread", "label_thread", "list_drafts", "list_labels", "list_send_as", "search_threads", "send_draft"]);
  } finally {
    server.close();
  }
});
