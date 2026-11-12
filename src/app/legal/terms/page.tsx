import type { Metadata } from "next";
import { COMPANY } from "@/lib/company";
import { PRODUCTS } from "@/lib/products";
import { Email, Ext, In, LegalTitle, Section, Sub, Summary, Todo } from "../_ui";

export const metadata: Metadata = {
  title: "Terms & Conditions · Mapsie",
  description: `Terms of Sale and Website Terms of Use for Mapsie, run by ${COMPANY.legalName}.`,
};

const sizes = PRODUCTS.map((p) => p.label).join(", ");

export default function TermsPage() {
  return (
    <>
      <LegalTitle
        title="Terms & Conditions"
        intro="Our Terms of Sale and Website Terms of Use. Please read them before you order: they explain what you can expect from us, and what we ask of you."
      />

      <Summary>
        <ul>
          <li>Designing a map on {COMPANY.brand} is free. You only pay when you order a print.</li>
          <li>
            Every print is made to order from your design, so you can&apos;t return it just because you&apos;ve changed your mind.
            You can cancel for a full refund until it goes into production.
          </li>
          <li>
            If your print arrives damaged, faulty or not as you designed it, tell us within 30 days and we&apos;ll reprint it or
            refund you. Your legal rights always apply on top of this.
          </li>
          <li>You must own (or have permission to use) any photos you upload, and keep your content lawful.</li>
          <li>Your photos and words stay yours. You let us use them only to save your design and print your order.</li>
        </ul>
      </Summary>

      <Section id="about" n={1} title="About us and these terms">
        <p>
          {COMPANY.site} (&ldquo;{COMPANY.brand}&rdquo;) is run by <strong>{COMPANY.legalName}</strong>, a company registered in{" "}
          {COMPANY.jurisdiction} under company number {COMPANY.number}, with its registered office at {COMPANY.address}. In these
          terms, &ldquo;we&rdquo;, &ldquo;us&rdquo; and &ldquo;our&rdquo; mean {COMPANY.legalName}, and &ldquo;you&rdquo; means
          the person using the website or placing an order.
        </p>
        <p>
          You can contact us at <Email to={COMPANY.supportEmail} />. If we need to contact you, we&apos;ll use the email address
          you gave us when you ordered or signed in.
        </p>
        <p>These terms have two parts:</p>
        <ul>
          <li>
            <strong>Website Terms of Use</strong> (sections 2 to 4) apply whenever you use {COMPANY.site}, including the map
            designer, whether or not you buy anything.
          </li>
          <li>
            <strong>Terms of Sale</strong> (sections 5 to 14) apply when you order a print from us.
          </li>
        </ul>
        <p>
          Sections 15 to 18 apply to both. Our <In href="/legal/privacy">Privacy Policy</In>,{" "}
          <In href="/legal/refunds">Returns, Refunds &amp; Reprints policy</In>,{" "}
          <In href="/legal/shipping">Shipping &amp; Delivery policy</In> and <In href="/legal/cookies">Cookie policy</In> also
          form part of how we work, so please read them too.
        </p>
        <p>
          We sell to consumers in the United Kingdom, the United States and Australia. These terms are written for consumers
          (people buying for personal use). Nothing in them takes away the rights you have under the consumer law of the country
          you live in.
        </p>
      </Section>

      {/* ------------------------------------------------------------- Website terms */}
      <Section id="using-the-site" n={2} title="Using our website">
        <Sub title="2.1 The designer is free to use">
          <p>
            You can design maps on {COMPANY.site} for free. While you work, your design in progress is saved in your own
            browser so you don&apos;t lose it (see our <In href="/legal/cookies">Cookie policy</In>). When you go to checkout, or
            save a design to your account, a copy of it is stored on our servers.
          </p>
        </Sub>
        <Sub title="2.2 Accounts">
          <p>
            You can sign in with your Google account to save designs and see your order history. You don&apos;t need an account
            to order. If you sign in, you&apos;re responsible for keeping access to your Google account secure, and for anything
            done through your {COMPANY.brand} account. Tell us straight away at <Email to={COMPANY.supportEmail} /> if you think
            someone else has used it.
          </p>
          <p>
            You can ask us to delete your account at any time. We may suspend or close an account if it&apos;s used in breach of
            these terms, for example to upload unlawful content.
          </p>
        </Sub>
        <Sub title="2.3 Fair use">
          <p>Please don&apos;t:</p>
          <ul>
            <li>use the site for anything unlawful, fraudulent or harmful;</li>
            <li>try to gain unauthorised access to the site, our servers or other people&apos;s designs or accounts;</li>
            <li>
              overload, scrape or automate requests to the site or the map, search and routing services it uses (these are
              shared services with fair-use limits);
            </li>
            <li>upload viruses or any other malicious code.</li>
          </ul>
        </Sub>
        <Sub title="2.4 Availability">
          <p>
            We work hard to keep {COMPANY.site} running smoothly, but it&apos;s provided free of charge and we can&apos;t
            promise it will always be available or error-free. We may change, pause or withdraw features at any time. The site
            relies on third-party map, search and routing services that are sometimes slow or unavailable. Please keep your own
            copies of any photos you upload; the site isn&apos;t a backup service.
          </p>
        </Sub>
      </Section>

      <Section id="your-content" n={3} title="Your photos, text and designs">
        <Sub title="3.1 You keep ownership">
          <p>
            Photos you upload and the text you write (&ldquo;your content&rdquo;) remain yours. We don&apos;t claim ownership
            of them.
          </p>
        </Sub>
        <Sub title="3.2 The permission you give us">
          <p>
            So that we can run the site and make your print, you give us a worldwide, non-exclusive, royalty-free licence to
            store, copy, process, resize, render and print your content, and to share it with our print partner and service
            providers, only as needed to save your designs, show them back to you, and make and deliver your orders. This licence
            ends when your content is deleted from our systems, except where we need to keep a copy of an order for the reasons
            explained in our <In href="/legal/privacy#retention">Privacy Policy</In>. We won&apos;t use your content in our
            marketing without asking you first.
          </p>
        </Sub>
        <Sub title="3.3 What you promise us">
          <p>When you upload or add content, you confirm that:</p>
          <ul>
            <li>
              you own it, or you have permission from whoever does (for example, the photographer) to use it and have it printed;
            </li>
            <li>
              you have permission from anyone clearly identifiable in your photos, where the law requires it, or you&apos;re
              otherwise entitled to use their image;
            </li>
            <li>
              it isn&apos;t unlawful, defamatory, obscene, hateful, harassing, threatening or discriminatory, doesn&apos;t
              promote violence or illegal activity, and doesn&apos;t include sexual content involving anyone under 18;
            </li>
            <li>
              it doesn&apos;t infringe anyone else&apos;s copyright, trade marks, privacy or other rights (for example, logos,
              artwork or photos you found online and don&apos;t have a licence to use).
            </li>
          </ul>
          <p>
            If someone makes a claim against us because content you uploaded broke these promises, you&apos;re responsible for
            the losses that we reasonably suffer as a result.
          </p>
        </Sub>
        <Sub title="3.4 We may refuse to print">
          <p>
            We don&apos;t check every design before it&apos;s printed, but we may refuse or cancel an order, or remove content,
            if we reasonably believe it breaks these terms or the law, or if we receive a complaint about it. If we cancel your
            order for this reason before it&apos;s printed, we&apos;ll refund you in full.
          </p>
          <p>
            If you think content on {COMPANY.site} infringes your rights, please email <Email to={COMPANY.supportEmail} /> with
            the details and we&apos;ll look into it promptly.
          </p>
        </Sub>
      </Section>

      <Section id="our-content" n={4} title="Our content and credits">
        <p>
          The {COMPANY.brand} name and logo, the design of the website, the map styles and templates we&apos;ve created, and our
          own artwork (including the illustrations we call &ldquo;{COMPANY.brand} Originals&rdquo;) belong to {COMPANY.legalName}{" "}
          or our licensors.
        </p>
        <p>
          When you buy a print, it&apos;s yours to keep, display and give as a gift. It&apos;s for personal, non-commercial use:
          please don&apos;t resell prints, reproduce them commercially, or extract {COMPANY.brand} Originals artwork or our
          templates for use elsewhere without our written permission. This doesn&apos;t limit what you can do with your own photos
          and text.
        </p>
        <p>We gratefully use, and credit, these open resources:</p>
        <ul>
          <li>
            Map data ©{" "}
            <Ext href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</Ext>, available under the Open
            Database Licence (ODbL), with map tiles served by <Ext href="https://openfreemap.org">OpenFreeMap</Ext>.
          </li>
          <li>
            Terrain shading uses the open{" "}
            <Ext href="https://registry.opendata.aws/terrain-tiles/">Terrain Tiles</Ext> dataset (Mapzen, hosted by AWS Open Data).
          </li>
          <li>
            Some stickers are from <Ext href="https://github.com/jdecked/twemoji">Twemoji</Ext>, © Twitter, Inc. and other
            contributors, licensed under{" "}
            <Ext href="https://creativecommons.org/licenses/by/4.0/">CC-BY 4.0</Ext>.
          </li>
          <li>
            Some stickers are from <Ext href="https://github.com/microsoft/fluentui-emoji">Microsoft Fluent Emoji</Ext>, ©
            Microsoft Corporation, licensed under the MIT licence.
          </li>
        </ul>
      </Section>

      {/* ------------------------------------------------------------- Terms of sale */}
      <Section id="ordering" n={5} title="Placing an order">
        <Sub title="5.1 What we sell">
          <p>
            We sell custom map prints made from the design you create on {COMPANY.site}, in the sizes {sizes}, in portrait or
            landscape, unframed or in a black, white or natural oak frame. The options and prices available to you are shown in
            the designer and at checkout.
          </p>
        </Sub>
        <Sub title="5.2 Check your design carefully">
          <p>
            Your print is made exactly from the design you submit, so please check it carefully before you pay: the spelling of
            names, places and notes, dates, the positions of stops and stickers, and the size, frame and orientation. We
            don&apos;t proofread or edit designs. If a mistake was in the design you submitted, it isn&apos;t a fault in the
            print (see section 10).
          </p>
        </Sub>
        <Sub title="5.3 How the contract is made">
          <p>
            When you pay at checkout, you&apos;re offering to buy the print. Our contract with you begins when your payment is
            confirmed and we show you your order confirmation. If we can&apos;t accept your order (for example, because a product
            is unavailable, we can&apos;t deliver to your address, there&apos;s an obvious pricing error, or your design breaks
            section 3), we&apos;ll tell you and refund you in full.
          </p>
        </Sub>
        <Sub title="5.4 Who can order">
          <p>
            To place an order you must be 18 or over, or have the permission of a parent or guardian. You must be buying for
            personal use, not for resale.
          </p>
        </Sub>
      </Section>

      <Section id="prices" n={6} title="Prices and payment">
        <ul>
          <li>
            Prices are shown in pounds sterling (GBP) for the UK, US dollars (USD) for the US, and Australian dollars (AUD) for
            Australia. You&apos;ll pay in the currency of the country we&apos;re delivering to.
          </li>
          <li>For UK orders, prices include VAT where applicable.</li>
          <li>
            Sales taxes for the US and Australia: <Todo>confirm how US state sales tax and Australian GST are charged and shown at checkout</Todo>
          </li>
          <li>
            Delivery charges, if any, are shown at checkout before you pay. Standard delivery is free. See our{" "}
            <In href="/legal/shipping">Shipping &amp; Delivery policy</In>.
          </li>
          <li>
            We print locally in each region so that, wherever possible, you won&apos;t have to pay import duties or taxes. If
            any do apply to your delivery, you&apos;re responsible for them.
          </li>
          <li>
            Payment is taken securely by <strong>Stripe</strong> when you place your order. We never see or store your full
            card details. Your bank may charge a fee if you pay in a currency other than your card&apos;s.
          </li>
          <li>
            We may change our prices at any time, but changes won&apos;t affect orders you&apos;ve already paid for. If we make
            an obvious mistake with a price, we&apos;ll contact you before your order goes ahead, and you can choose to cancel
            for a full refund.
          </li>
        </ul>
      </Section>

      <Section id="making" n={7} title="How your print is made">
        <p>
          Each print is made to order, just for you. We send your order to our print partner, <strong>Prodigi</strong>, which
          prints, frames (if you chose a frame), packs and dispatches it from a production site in or near your country. Orders
          are usually dispatched within 2 to 4 working days.
        </p>
        <p>A few things to know about printing:</p>
        <ul>
          <li>
            Screens and printed paper show colour differently, and every screen is different, so colours on your print may look
            slightly different from your preview. This is normal and isn&apos;t a fault.
          </li>
          <li>
            Photos you upload print best at a good resolution. A small or blurry photo will look small or blurry when printed,
            especially on larger sizes.
          </li>
        </ul>
      </Section>

      <Section id="delivery" n={8} title="Delivery">
        <p>
          We deliver to addresses in the UK, the US and Australia. Delivery options, timescales and costs are set out in our{" "}
          <In href="/legal/shipping">Shipping &amp; Delivery policy</In>. Delivery times are estimates; if your order is late,
          please let us know and we&apos;ll chase it. If we don&apos;t deliver within 30 days of your order (or any later date
          we agree with you), you can cancel and get a full refund.
        </p>
        <p>
          Your print is our responsibility until it&apos;s delivered to the address you gave us. It becomes yours once
          we&apos;ve received full payment, and it&apos;s your responsibility once it&apos;s delivered. Please make sure your
          delivery address is correct at checkout: we can&apos;t change it once your order has gone to print.
        </p>
      </Section>

      <Section id="cancelling" n={9} title="Cancelling your order">
        <p>
          Because every print is personalised and made to your own design, the usual 14-day &ldquo;cooling-off&rdquo; right
          to cancel an online purchase doesn&apos;t apply once production has started. In the UK this is set out in regulation
          28(1)(b) of the Consumer Contracts (Information, Cancellation and Additional Charges) Regulations 2013.
        </p>
        <p>
          But we know mistakes happen. We&apos;ll cancel your order for a full refund <strong>if it hasn&apos;t been sent to print
          yet</strong>. Orders usually go to print within minutes of payment, so we can&apos;t promise to catch it. Email <Email to={COMPANY.supportEmail} /> with your order
          number as quickly as you can. Once production has started we can&apos;t cancel or change the order. Full details are
          in our <In href="/legal/refunds#cancel">Returns, Refunds &amp; Reprints policy</In>.
        </p>
        <p>We don&apos;t accept returns for change of mind.</p>
      </Section>

      <Section id="problems" n={10} title="If something is wrong with your print">
        <p>
          We want you to love your print. If it arrives <strong>damaged, faulty, or not as you designed it</strong>, tell us
          within 30 days of delivery, with a photo, and we&apos;ll reprint it free of charge or give you a full refund. See our{" "}
          <In href="/legal/refunds">Returns, Refunds &amp; Reprints policy</In> for how to do this and what&apos;s covered.
        </p>
        <p>
          This promise is <strong>in addition to</strong> your legal rights. It doesn&apos;t replace or limit them.
        </p>
        <Sub title="Your legal rights">
          <ul>
            <li>
              <strong>UK:</strong> under the Consumer Rights Act 2015, goods must be as described, fit for purpose and of
              satisfactory quality. If they aren&apos;t, you can usually reject them for a full refund within 30 days of
              delivery. After that, you can ask for a repair or replacement and, if that doesn&apos;t fix things, a refund or
              price reduction. You may have up to six years to make a claim. Citizens Advice can tell you more.
            </li>
            <li>
              <strong>Australia:</strong> our goods come with guarantees that cannot be excluded under the Australian Consumer
              Law. You are entitled to a replacement or refund for a major failure and compensation for any other reasonably
              foreseeable loss or damage. You are also entitled to have the goods repaired or replaced if the goods fail to be of
              acceptable quality and the failure does not amount to a major failure.
            </li>
            <li>
              <strong>United States:</strong> you have the benefit of the policy above and any rights given to you by the law of
              your state, including implied warranties that can&apos;t be excluded.
            </li>
          </ul>
        </Sub>
        <p>
          Things that <strong>aren&apos;t</strong> faults: mistakes that were in the design you submitted (such as typos,
          low-resolution photos or stickers in the wrong place), small colour differences between screen and print, and the map
          details described in section 13.
        </p>
      </Section>

      <Section id="liability" n={11} title="Our responsibility to you">
        <p>
          If we break these terms or fail to use reasonable care and skill, we&apos;re responsible for loss or damage you
          suffer that is a foreseeable result. Loss or damage is foreseeable if it&apos;s obvious it will happen, or if both of
          us knew it might happen when the contract was made.
        </p>
        <p>
          We supply prints for personal use only. We aren&apos;t responsible for business losses such as loss of profit,
          business or opportunity.
        </p>
        <p>
          We don&apos;t exclude or limit our liability where it would be unlawful to do so. That includes liability for death
          or personal injury caused by our negligence, for fraud or fraudulent misrepresentation, or for breaching your legal
          rights as a consumer (for example, under the Consumer Rights Act 2015 or the Australian Consumer Law).
        </p>
        <p>
          The website and designer are provided free. Apart from the above, we aren&apos;t responsible for losing designs or
          photos stored with us, so please keep your own copies.
        </p>
      </Section>

      <Section id="outside-control" n={12} title="Events outside our control">
        <p>
          We&apos;re not responsible for delays or failures caused by events outside our reasonable control, such as severe
          weather, strikes, courier or postal disruption, or a failure of our print partner or a service we rely on. If this
          happens, we&apos;ll let you know as soon as we can and do what we reasonably can to reduce the delay. If there&apos;s a
          risk of a significant delay, you can contact us to cancel and receive a refund for anything you&apos;ve paid for but
          not received.
        </p>
      </Section>

      <Section id="maps" n={13} title="About the maps">
        <p>
          {COMPANY.brand} prints are decorative keepsakes. Route lines are drawn to look good: flights, boats, hikes and other
          journeys are shown as styled lines, and road routes are calculated automatically, so they may not match the exact way
          you travelled. Place names, borders and other map details come from OpenStreetMap, a map made by volunteers, and may
          not always be complete or up to date. Showing a border or place name doesn&apos;t mean we take a position on it.
          Please don&apos;t use a {COMPANY.brand} map for navigation.
        </p>
        <p>
          Because your preview shows the map as it will be printed, details visible on the map in your preview aren&apos;t a
          fault in your print.
        </p>
      </Section>

      <Section id="complaints" n={14} title="Questions and complaints">
        <p>
          If you&apos;re unhappy with anything, please email us at <Email to={COMPANY.supportEmail} /> with your order number
          (if you have one) and tell us what&apos;s happened. We&apos;ll reply as soon as we can and try to put
          things right fairly and quickly.
        </p>
        <p>
          If we can&apos;t resolve a complaint between us, you may be able to use an alternative dispute resolution scheme,
          or go to court (see section 18). <Todo>confirm whether DayzeOut Limited uses an ADR provider and, if so, name it here; if not, keep the sentence below</Todo>{" "}
          We aren&apos;t currently a member of an alternative dispute resolution scheme. UK customers can get free advice from{" "}
          <Ext href="https://www.citizensadvice.org.uk/consumer/">Citizens Advice</Ext>; Australian customers can contact their
          state or territory consumer protection agency.
        </p>
      </Section>

      {/* ------------------------------------------------------------- general */}
      <Section id="privacy" n={15} title="Your personal information">
        <p>
          We use your personal information only as set out in our <In href="/legal/privacy">Privacy Policy</In>.
        </p>
      </Section>

      <Section id="changes" n={16} title="Changes to these terms">
        <p>
          We may update these terms from time to time, for example to reflect changes in the law or in how we work. The
          version that applies to an order is the one shown on this page when you placed it. The &ldquo;Last updated&rdquo;
          date at the top shows when they last changed. If we make a significant change that affects you, and you have an
          account with us, we&apos;ll let you know.
        </p>
      </Section>

      <Section id="general" n={17} title="Other important terms">
        <ul>
          <li>
            We may transfer our rights and obligations under these terms to another organisation, for example if our business
            is sold. We&apos;ll tell you if this happens, and it won&apos;t affect your rights. You may only transfer your rights
            to someone else with our written agreement.
          </li>
          <li>This contract is between you and us. Nobody else has any rights to enforce it.</li>
          <li>
            If a court decides that part of these terms is invalid or unenforceable, the rest of the terms will still apply.
          </li>
          <li>
            If we don&apos;t insist straight away that you do something you&apos;re required to do, that doesn&apos;t stop us
            from asking you to do it later.
          </li>
        </ul>
      </Section>

      <Section id="law" n={18} title="Which laws apply and where you can bring legal proceedings">
        <p>
          These terms are governed by the law of England and Wales, and you can bring legal proceedings about them in the
          English courts. If you live in Scotland or Northern Ireland, you can also bring proceedings in your local courts.
        </p>
        <p>
          If you live outside the UK, choosing English law doesn&apos;t take away the protection you have under the mandatory
          consumer laws of the country, state or territory you live in, and you may also be able to bring proceedings in your
          local courts.
        </p>
      </Section>
    </>
  );
}
