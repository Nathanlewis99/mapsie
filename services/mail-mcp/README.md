# Mapsie mail connector

A small, separate web service that gives Claude access to the **admin@mapsie.shop** Gmail inbox, including its aliases such as nathan@mapsie.shop. It runs as a remote MCP connector added in claude.ai. It sits alongside the existing Gmail connector and doesn't replace it.

What Claude can do with it:
- search and read email;
- write drafts (including replies in the right thread) from any "send mail as" address;
- send a draft;
- label, archive and mark threads as read.

It can't delete email: the `gmail.modify` scope doesn't allow permanent deletion.

## Security

- **Who can use it:** only the Google accounts in `ALLOWED_EMAILS` can connect. Connecting goes through Google's own sign-in.
- **Where Claude's sign-in may return:** only to `claude.ai` or `claude.com` addresses (`ALLOWED_REDIRECT_HOSTS`).
- **No stored secrets:** there's no database. The Google refresh token is encrypted (AES-256-GCM) inside the signed tokens Claude holds. Access tokens last 1 hour and refresh tokens 30 days.
- **To cut access off immediately:** change `MCP_SECRET` on Render, and/or remove the app at myaccount.google.com → Security → Third-party connections.

## Set up

1. **Google Cloud**, in the DayzeOut organisation where admin@mapsie.shop lives:
   1. Create a project, for example "Mapsie mail connector", and enable the **Gmail API**.
   2. Set the OAuth consent screen's user type to **Internal**. That means no Google review, and only DayzeOut accounts can sign in.
   3. Add the scopes `gmail.modify`, `gmail.settings.basic`, `openid` and `email`.
   4. Create an OAuth client ID of type **Web application**, with the authorised redirect URI `https://<service address>/google/callback`.
2. **Render:** create a new Web Service from this repository with these settings:
   - Root directory: `services/mail-mcp`
   - Runtime: Node
   - Build command: `npm ci`
   - Start command: `node server.mjs`
   - Health check path: `/health`
   - Region: Frankfurt
   - Plan: Starter

   Environment variables:
   - `PUBLIC_URL`: the service address, for example `https://mapsie-mail-mcp.onrender.com`
   - `MCP_SECRET`: use "Generate"
   - `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`: from step 1
   - `ALLOWED_EMAILS`: `admin@mapsie.shop`
3. **claude.ai:** go to Settings → Connectors → Add custom connector, name it "Mapsie mail" and use the URL `https://<service address>/mcp`. Click Connect, sign in to Google as admin@mapsie.shop and allow access. Start a new Claude Code session to use it.

## Tests

`cd services/mail-mcp && npm ci && npm test`
