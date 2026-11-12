import type { Metadata } from "next";
import { COMPANY } from "@/lib/company";
import { SESSION_COOKIE, SESSION_DAYS } from "@/lib/session";
import { Email, Ext, In, LegalTitle, Section, Summary, Table } from "../_ui";

export const metadata: Metadata = {
  title: "Cookies & Local Storage · Mapsie",
  description: "Mapsie uses only essential cookies and browser storage. No analytics or advertising cookies.",
};

export default function CookiesPage() {
  return (
    <>
      <LegalTitle
        title="Cookies & Local Storage"
        intro="The short version: we only store what the site needs to work. No analytics, no advertising, no tracking."
      />

      <Summary>
        <ul>
          <li>We use one sign-in cookie (plus a few short-lived ones while you sign in), and only if you sign in.</li>
          <li>Your browser&apos;s local storage autosaves the map you&apos;re designing, so you don&apos;t lose your work.</li>
          <li>We don&apos;t use analytics, advertising or social media cookies, so there&apos;s no cookie banner to click through.</li>
        </ul>
      </Summary>

      <Section id="what" n={1} title="What cookies and local storage are">
        <p>
          A <strong>cookie</strong> is a small text file a website saves in your browser, which your browser sends back to that
          site on each visit. <strong>Local storage</strong> is similar, but it stays in your browser and isn&apos;t sent to
          our servers automatically. The law treats both in the same way: a site needs your consent to use them, unless
          they&apos;re strictly necessary to provide something you&apos;ve asked for.
        </p>
      </Section>

      <Section id="what-we-use" n={2} title="What we use">
        <p>Everything below is strictly necessary for the site to do what you ask, so it doesn&apos;t need consent.</p>
        <Table
          head={["Name", "Type", "What it's for", "How long it lasts"]}
          rows={[
            [
              <code key="n">{SESSION_COOKIE}</code>,
              "Cookie",
              "Keeps you signed in to your account, so you can save designs and see your orders. Only set if you sign in.",
              `${SESSION_DAYS} days, or until you sign out`,
            ],
            [
              <code key="n">g_state</code>,
              "Cookie",
              "Set for a few minutes while you sign in with Google, to keep the sign-in secure and return you to the page you were on.",
              "10 minutes",
            ],
            [<code key="n">g_verifier</code>, "Cookie", "As above.", "10 minutes"],
            [<code key="n">g_next</code>, "Cookie", "As above.", "10 minutes"],
            [
              <code key="n">mapsie-design</code>,
              "Local storage",
              "Autosaves the design you're working on (including any photos you've added) and your chosen country, so your work is still there if you close the tab.",
              "Until you clear your browser's site data",
            ],
          ]}
        />
        <p>
          If you sign in to the admin area, the same sign-in cookie also records when you last entered your authenticator
          code.
        </p>
      </Section>

      <Section id="not-used" n={3} title="What we don't use">
        <p>
          We don&apos;t use analytics cookies, advertising or retargeting cookies, social media pixels, or any other tracking
          technology. We don&apos;t build profiles of what you do on the site.
        </p>
        <p>
          If we ever want to add anything that isn&apos;t strictly necessary (for example, analytics to understand how people
          use the designer), we&apos;ll update this page and our <In href="/legal/privacy">Privacy Policy</In> first, and ask
          for your consent before setting it.
        </p>
      </Section>

      <Section id="third-parties" n={4} title="Other services you'll interact with">
        <ul>
          <li>
            <strong>Paying:</strong> checkout takes place on a secure page run by Stripe, which uses its own cookies to process
            payments and prevent fraud. See{" "}
            <Ext href="https://stripe.com/cookies-policy/legal">Stripe&apos;s cookie policy</Ext>.
          </li>
          <li>
            <strong>Signing in:</strong> when you sign in with Google you&apos;re briefly taken to Google&apos;s own sign-in page,
            where Google&apos;s cookies apply. See <Ext href="https://policies.google.com/technologies/cookies">Google&apos;s
            cookie policy</Ext>.
          </li>
          <li>
            <strong>Maps and search:</strong> to show the map and search for places, your browser loads map tiles from
            OpenFreeMap and elevation data from Amazon Web Services, and sends your searches to Photon (run by komoot). These
            requests share your IP address with those services, as any web request does, but we don&apos;t ask them to set
            cookies. See our <In href="/legal/privacy#sharing">Privacy Policy</In> for more.
          </li>
        </ul>
      </Section>

      <Section id="control" n={5} title="Managing and deleting them">
        <p>
          You can delete cookies and local storage for {COMPANY.site} at any time in your browser settings (usually under
          &ldquo;Privacy&rdquo; or &ldquo;Site data&rdquo;). If you do, you&apos;ll be signed out and any design you haven&apos;t
          saved to your account or ordered will be lost from that browser. Blocking these entirely will stop sign-in and
          autosave from working.
        </p>
        <p>
          Questions? Email <Email to={COMPANY.privacyEmail} />.
        </p>
      </Section>
    </>
  );
}
