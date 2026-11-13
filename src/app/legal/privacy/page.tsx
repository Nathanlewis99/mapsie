import type { Metadata } from "next";
import { COMPANY } from "@/lib/company";
import { SESSION_DAYS } from "@/lib/session";
import { Email, Ext, In, LegalTitle, Section, Sub, Summary, Table} from "../_ui";

export const metadata: Metadata = {
  title: "Privacy Policy · Mapsie",
  description: `How ${COMPANY.legalName} collects, uses and protects your personal information when you use Mapsie.`,
};

export default function PrivacyPage() {
  return (
    <>
      <LegalTitle
        title="Privacy Policy"
        intro="What personal information we collect when you use Mapsie, why we need it, who we share it with, and the choices and rights you have."
      />

      <Summary>
        <ul>
          <li>We only collect what we need to let you design maps and to make and deliver your prints.</li>
          <li>We don&apos;t sell your information, and we don&apos;t use analytics, advertising or tracking cookies. We count visits anonymously, without cookies.</li>
          <li>
            We share your details only with the services that help us run {COMPANY.brand}: hosting, payments, printing and
            delivery, sign-in, and maps.
          </li>
          <li>
            You can ask to see, correct or delete your information at any time: email <Email to={COMPANY.privacyEmail} />.
          </li>
        </ul>
      </Summary>

      <Section id="who" n={1} title="Who we are">
        <p>
          {COMPANY.brand} ({COMPANY.site}) is run by <strong>{COMPANY.legalName}</strong>, registered in {COMPANY.jurisdiction}{" "}
          (company no. {COMPANY.number}), registered office {COMPANY.address}. We are the &ldquo;controller&rdquo; of your
          personal information, which means we decide how and why it is used and we&apos;re responsible for looking after it.
        </p>
        <p>
          For anything to do with your personal information, email <Email to={COMPANY.privacyEmail} />, or write to us at
          our registered office. For orders and anything else, use <Email to={COMPANY.supportEmail} />.
        </p>
        <p>
          This policy is written to meet the UK General Data Protection Regulation (UK GDPR) and the Data Protection Act 2018,
          the EU GDPR where it applies, the Australian Privacy Act 1988 and Australian Privacy Principles, and US state privacy
          laws. Sections <a href="#australia">10</a> and <a href="#us">11</a> have extra information for customers in Australia
          and the US.
        </p>
      </Section>

      <Section id="collect" n={2} title="What we collect, and why">
        <Sub title="Your designs">
          <p>
            The maps you create: the places you search for and add as stops, routes, styles, stickers, the text and notes you
            write, and any <strong>photos you upload</strong>. Photos are stored inside the design they belong to. Your design
            in progress is autosaved in your own browser. A copy is stored on our servers when you save it to your account or
            go to checkout.
          </p>
          <p>
            Your designs can reveal things about you, like where you&apos;ve travelled, and your photos may show you or other
            people. We use them only to save your work, show it back to you, and print your order. Please only upload photos of
            other people if they&apos;re happy for you to.
          </p>
        </Sub>
        <Sub title="Your account (if you sign in)">
          <p>
            When you sign in with Google, Google shares your <strong>name, email address and profile picture</strong> with us,
            along with a unique Google account ID. We use these to create your account, keep you signed in, save your designs
            and show you your order history. We don&apos;t get your Google password or access to anything else in your Google
            account. We also record when you created your account and last signed in.
          </p>
          <p>
            If you create an account with your email and a password instead, we store your email, the first name you give us
            (if any) and a secure one-way hash of your password, never the password itself. We email you a link to confirm
            your address, and a link to reset your password if you ask for one.
          </p>
        </Sub>
        <Sub title="Your orders">
          <p>
            When you order, we collect your <strong>email address</strong>, <strong>name and delivery address</strong>, the
            product, size, frame and delivery option you chose, the price and currency, and your order&apos;s status. We create a
            high-resolution <strong>print file</strong> of your design to send to our print partner.
          </p>
        </Sub>
        <Sub title="Payments">
          <p>
            Payments are handled by Stripe on its secure checkout page. We never see or store your full card number. Stripe tells
            us whether your payment succeeded and gives us the delivery details you enter at checkout.
          </p>
        </Sub>
        <Sub title="When you contact us">
          <p>
            If you email us, we keep your message, your email address and anything you send us (such as photos of a damaged
            print) so we can help you.
          </p>
        </Sub>
        <Sub title="Technical information">
          <p>
            Like any website, our servers receive your IP address and basic information about your browser when you visit. Our
            hosting provider keeps short-term technical logs to run the service securely. We don&apos;t use this information
            to identify you or track you across the web.
          </p>
        </Sub>
        <Sub title="Anonymous usage statistics">
          <p>
            We count anonymous steps people take on the site (for example &quot;opened the designer&quot;, &quot;reached
            checkout&quot;, &quot;paid&quot;) and the words typed into the sticker search, with the website that sent them, the first page they landed on and whether they
            used a phone or a computer. Each visit gets a random number that lives only in the open page and isn&apos;t stored
            on your device or linked to your name, email or IP address. We use this, in our legitimate interest in running and
            improving the shop, to see where the site is confusing. Browsers sending Global Privacy Control or Do Not Track
            signals aren&apos;t counted. When you place an order we note the visit&apos;s random number on the order so we can
            count it as &quot;paid&quot;, and nothing more.
          </p>
        </Sub>
        <p>
          We don&apos;t ask for, and don&apos;t want, sensitive information such as health details or religious or political
          beliefs. Please don&apos;t include it in your designs or messages.
        </p>
      </Section>

      <Section id="lawful-bases" n={3} title="Our lawful bases for using your information">
        <p>UK and EU data protection law requires us to have a lawful basis for each use of your information. Ours are:</p>
        <Table
          head={["What we do", "Lawful basis"]}
          rows={[
            [
              "Store your designs and photos, and make, print and deliver your order",
              <><strong>Contract</strong>: it&apos;s needed to provide what you&apos;ve asked for.</>,
            ],
            [
              "Create and run your account, and keep you signed in",
              <><strong>Contract</strong>: it&apos;s needed to provide the account you&apos;ve asked for.</>,
            ],
            [
              "Take payment and deal with refunds",
              <><strong>Contract</strong>, and <strong>legal obligation</strong> to keep financial records.</>,
            ],
            [
              "Contact you about your order and reply to your messages",
              <><strong>Contract</strong>, and our <strong>legitimate interests</strong> in providing good customer service.</>,
            ],
            [
              "Keep the site secure, prevent fraud and misuse, and fix problems",
              <>Our <strong>legitimate interests</strong> in running a safe, working service.</>,
            ],
            [
              "Keep order and accounting records, and respond to legal requests",
              <><strong>Legal obligation</strong>.</>,
            ],
            [
              "Handle disputes and legal claims",
              <>Our <strong>legitimate interests</strong> in protecting our business.</>,
            ],
          ]}
        />
        <p>
          Where we rely on legitimate interests, we&apos;ve balanced them against your rights and you can object (see{" "}
          <a href="#rights">section 9</a>). We don&apos;t send marketing emails. If we start, we&apos;ll only send them to people
          who have agreed to receive them, and every email will have an unsubscribe link.
        </p>
      </Section>

      <Section id="sharing" n={4} title="Who we share your information with">
        <p>
          We use trusted service providers to run {COMPANY.brand}. They only process your information on our instructions, or
          as independent services you use directly, and only for the purposes below.
        </p>
        <Table
          head={["Who", "What they do", "What they receive"]}
          rows={[
            [<strong key="w">Render</strong>, "Hosts our website, servers and database (in Frankfurt, Germany)", "Everything we store, including designs, photos, accounts and orders"],
            [<strong key="w">Stripe</strong>, "Takes payments securely and handles refunds", "Your email address, card details, delivery details and the order amount"],
            [<strong key="w">Prodigi</strong>, "Our print partner: prints, frames, packs and delivers your order, using local print labs and couriers", "Your name, delivery address, email address and the print file of your design"],
            [<strong key="w">Google</strong>, "Lets you sign in with your Google account", "That you’re signing in to Mapsie. Google sends us your name, email and profile picture"],
            [<strong key="w">Photon (komoot)</strong>, "Place search: finds the places you type in", "The places you search for, the coordinates of points you add to the map (to look up their names), and, because your browser sends these requests directly, your IP address"],
            [<strong key="w">OSRM (Project OSRM)</strong>, "Calculates road routes between your stops", "The coordinates of the stops being joined. Requests are sent from our server, not your browser"],
            [<strong key="w">OpenFreeMap</strong>, "Supplies the map tiles (map data from OpenStreetMap)", "Your IP address and which area of the map you’re viewing, as your browser loads the tiles"],
            [<strong key="w">Amazon Web Services</strong>, "Supplies the open elevation data used for map styles with terrain shading", "Your IP address and which area of the map you’re viewing, as your browser loads the tiles"],
          ]}
        />
        <p>We may also share information:</p>
        <ul>
          <li>with professional advisers such as accountants and lawyers, where needed;</li>
          <li>where the law requires it, for example with tax authorities, the police or a court;</li>
          <li>
            with a buyer or investor if our business, or part of it, is sold or restructured, in which case they&apos;d have to
            protect your information in line with this policy.
          </li>
        </ul>
        <p>
          <strong>We never sell your personal information</strong>, and we don&apos;t share it with anyone for advertising.
        </p>
      </Section>

      <Section id="transfers" n={5} title="International transfers">
        <p>
          Our website and database are hosted in the European Union (Frankfurt, Germany). The UK recognises the EU as providing
          an adequate level of protection for personal information.
        </p>
        <p>
          Some of our service providers are based in, or use systems in, other countries. In particular, Stripe and Google
          may process information in the United States, and Prodigi prints and ships your order from a site in or near your
          country, so if you order from the US or Australia, your order details will be processed there. Where your information
          is transferred outside the UK or EU to a country without an adequacy decision, we make sure it is protected by
          appropriate safeguards, such as the UK International Data Transfer Agreement or Addendum, the EU Standard Contractual
          Clauses, or the UK Extension to the EU-US Data Privacy Framework where the recipient is certified. Contact us if
          you&apos;d like more details.
        </p>
      </Section>

      <Section id="retention" n={6} title="How long we keep your information">
        <p>We keep information only as long as we need it, then delete it or make it anonymous.</p>
        <Table
          head={["Information", "How long we keep it"]}
          rows={[
            ["Design in progress in your browser", "Until you clear your browser's site data. It never leaves your device unless you save it or go to checkout"],
            ["Designs saved to your account (including photos)", "Until you delete them or close your account"],
            [
              "Designs sent to checkout but not ordered",
              "90 days, then deleted automatically. This also applies to designs shared by link",
            ],
            ["Your account (name, email, profile picture)", "Until you ask us to close it"],
            [
              "Order records (email, name, address, what you bought and paid)",
              "6 years after the end of the financial year of the order, as required by UK tax and company law. If you close your account, we keep your orders for this period but unlink them from your account",
            ],
            [
              "The design and print file for an order",
              "12 months after the order, so we can deal with reprints and problems, then deleted automatically",
            ],
            ["Emails and support messages", "2 years after the matter is resolved"],
            ["Server technical logs", "Up to 30 days, kept by our hosting provider"],
            ["Anonymous usage statistics", "About 13 months, then deleted automatically"],
            ["Error reports (what went wrong, on which page, browser type)", "Until the problem is fixed, and at most 12 months"],
            ["Sign-in cookie", <>Up to {SESSION_DAYS} days, or until you sign out (see our <In href="/legal/cookies">Cookie policy</In>)</>],
          ]}
        />
        <p>
          We may keep information for longer if we need it to deal with a complaint or legal claim, or if the law requires it.
        </p>
      </Section>

      <Section id="security" n={7} title="How we keep it safe">
        <p>
          Everything you send to {COMPANY.site} is encrypted in transit (HTTPS). Access to our systems is restricted to the
          people who need it, and our admin area is protected by Google sign-in plus an authenticator-app code. Card payments are
          handled entirely by Stripe. No system is perfectly secure, but if we ever have a data breach that puts you at risk,
          we&apos;ll tell you and the regulator as the law requires.
        </p>
      </Section>

      <Section id="children" n={8} title="Children">
        <p>
          {COMPANY.brand} isn&apos;t aimed at children, and you must be 18 or over (or have a parent or guardian&apos;s
          permission) to place an order. We don&apos;t knowingly collect information from children under 13. If you think a
          child has given us their information, please contact us and we&apos;ll delete it.
        </p>
      </Section>

      <Section id="rights" n={9} title="Your rights">
        <p>Under UK and EU data protection law, you have the right to:</p>
        <ul>
          <li><strong>access</strong> the personal information we hold about you and get a copy;</li>
          <li><strong>correct</strong> information that&apos;s wrong or incomplete;</li>
          <li><strong>delete</strong> your information (sometimes called the &ldquo;right to be forgotten&rdquo;), unless we have to keep it, for example order records for tax;</li>
          <li><strong>restrict</strong> how we use your information, for example while a complaint is looked into;</li>
          <li><strong>object</strong> to us using your information where we rely on legitimate interests;</li>
          <li><strong>data portability</strong>: receive the information you gave us in a common, machine-readable format, or have it sent to another organisation;</li>
          <li><strong>withdraw consent</strong> at any time, where we rely on consent.</li>
        </ul>
        <p>
          We don&apos;t make decisions about you using solely automated processing that have legal or similarly significant
          effects.
        </p>
        <p>
          To use any of these rights, email <Email to={COMPANY.privacyEmail} />. It&apos;s free, and we&apos;ll reply within one
          month. We may need to confirm your identity first, for example by asking you to email us from the address linked to
          your account or order.
        </p>
      </Section>

      <Section id="australia" n={10} title="Extra information for customers in Australia">
        <p>
          We handle your personal information in line with the Australian Privacy Principles (APPs) in the Privacy Act 1988
          (Cth). In particular:
        </p>
        <ul>
          <li>
            You can ask to access the personal information we hold about you, and to correct it, by emailing{" "}
            <Email to={COMPANY.privacyEmail} />. We&apos;ll respond within 30 days.
          </li>
          <li>
            <strong>Overseas disclosure:</strong> we are based in the UK, our servers are in Germany, and some of our service
            providers process information in the United States. Your order is printed and delivered locally in Australia by our
            print partner, Prodigi. See <a href="#sharing">section 4</a> and <a href="#transfers">section 5</a> for who receives
            your information and how we protect it.
          </li>
          <li>
            You can deal with us without giving your name while you design maps, but we need your name, email and address to
            fulfil an order.
          </li>
          <li>
            If you have a complaint, please contact us first and we&apos;ll respond within 30 days. If you&apos;re not satisfied,
            you can complain to the{" "}
            <Ext href="https://www.oaic.gov.au/privacy/privacy-complaints">Office of the Australian Information Commissioner (OAIC)</Ext>.
          </li>
        </ul>
      </Section>

      <Section id="us" n={11} title="Extra information for customers in the United States">
        <p>
          Some US states, including California, Colorado, Connecticut, Virginia and others, give residents specific privacy
          rights. Whether or not those laws apply to a business of our size, we&apos;re happy to honour these requests from any
          US customer.
        </p>
        <ul>
          <li>
            <strong>What we collect:</strong> identifiers (name, email, delivery address, IP address, Google account ID),
            commercial information (your orders), the content you create (designs, text and photos), and limited technical
            information. Section 2 explains the sources and purposes. We don&apos;t collect sensitive personal information
            beyond what you choose to put in your own designs, and we don&apos;t use it to infer anything about you.
          </li>
          <li>
            <strong>No selling or &ldquo;sharing&rdquo;:</strong> we do not sell your personal information or share it for
            cross-context behavioural advertising, and we haven&apos;t done so in the last 12 months. We don&apos;t use
            tracking technology, so there&apos;s nothing to opt out of.
          </li>
          <li>
            <strong>Your rights:</strong> you can ask to know what information we hold and how we use it, to get a copy, to
            correct it, and to delete it. Email <Email to={COMPANY.privacyEmail} />. You can use an authorised agent, and we may
            need to verify your identity. If we decline your request, you can appeal by replying to our decision.
          </li>
          <li>
            <strong>No discrimination:</strong> we won&apos;t treat you differently for using your privacy rights.
          </li>
          <li>Retention periods are in <a href="#retention">section 6</a>.</li>
        </ul>
      </Section>

      <Section id="complaints" n={12} title="Complaints">
        <p>
          If you&apos;re unhappy with how we&apos;ve handled your information, please contact us first at{" "}
          <Email to={COMPANY.privacyEmail} /> so we can try to put it right.
        </p>
        <p>
          You also have the right to complain to the UK&apos;s data protection regulator, the{" "}
          <strong>Information Commissioner&apos;s Office (ICO)</strong>:{" "}
          <Ext href="https://ico.org.uk/make-a-complaint/">ico.org.uk/make-a-complaint</Ext>, or by phone on 0303 123 1113. If
          you live in the EU, you can complain to the data protection authority in your country. Australian customers can
          contact the OAIC (see <a href="#australia">section 10</a>).
        </p>
      </Section>

      <Section id="changes" n={13} title="Changes to this policy">
        <p>
          We&apos;ll update this policy if we change how we use your information, for example if we add a new service provider.
          The &ldquo;Last updated&rdquo; date at the top shows when it last changed. If a change significantly affects you,
          we&apos;ll let you know before it takes effect. See also our <In href="/legal/cookies">Cookie policy</In> and{" "}
          <In href="/legal/terms">Terms &amp; Conditions</In>.
        </p>
      </Section>
    </>
  );
}
