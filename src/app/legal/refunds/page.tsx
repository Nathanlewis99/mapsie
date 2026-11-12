import type { Metadata } from "next";
import { COMPANY } from "@/lib/company";
import { Email, Ext, In, LegalTitle, Section, Sub, Summary } from "../_ui";

export const metadata: Metadata = {
  title: "Returns, Refunds & Reprints · Mapsie",
  description: "What to do if your Mapsie print arrives damaged or isn't right, how to cancel an order, and how refunds work.",
};

export default function RefundsPage() {
  return (
    <>
      <LegalTitle
        title="Returns, Refunds & Reprints"
        intro="Every Mapsie print is made just for you. Here's what happens if something isn't right, and what we can and can't take back."
      />

      <Summary>
        <ul>
          <li>
            <strong>Damaged, faulty or not as you designed it?</strong> Email us within 30 days of delivery with a photo and
            we&apos;ll reprint it free or refund you in full, whichever you prefer.
          </li>
          <li>
            <strong>Changed your mind?</strong> You can cancel for a full refund within 1 hour of ordering, using the
            Cancel button on your order page. After that it goes to print and can&apos;t be cancelled.
          </li>
          <li>
            <strong>No change-of-mind returns</strong>, because each print is personalised. Your legal rights for faulty goods
            always apply.
          </li>
        </ul>
      </Summary>

      <Section id="personalised" n={1} title="Why we can't accept change-of-mind returns">
        <p>
          Each print is custom-made from your own design, with your places, route, notes and photos, so we can&apos;t resell
          it to anyone else. For that reason, personalised goods are not covered by the usual 14-day right to cancel an online
          order once production has started. In the UK, this exception is in regulation 28(1)(b) of the Consumer Contracts
          (Information, Cancellation and Additional Charges) Regulations 2013.
        </p>
        <p>
          That means we don&apos;t accept returns or give refunds if you simply change your mind, choose the wrong size or frame,
          or spot a mistake in your design after the order has gone to print. Please check your design carefully before you
          pay.
        </p>
      </Section>

      <Section id="cancel" n={2} title="Cancelling an order">
        <p>
          You can cancel your order for a <strong>full refund</strong>, including any delivery charge, within{" "}
          <strong>1 hour of placing it</strong>. We hold every order for an hour before sending it to print, so you have time to
          spot a mistake. Use the <strong>Cancel order</strong> button on your order page (the link is in your confirmation and in
          your account), and the refund is made automatically.
        </p>
        <p>
          If you can&apos;t use the button, email <Email to={COMPANY.supportEmail} /> within the hour with your order number and
          we&apos;ll cancel it for you. Once your order has been sent to our print partner, it can&apos;t be cancelled or changed,
          including the design, size, frame or delivery address.
        </p>
      </Section>

      <Section id="problems" n={3} title="If your print arrives damaged, faulty or not as designed">
        <p>We&apos;ll put it right free of charge if your print:</p>
        <ul>
          <li>arrives damaged, for example creased, torn, scratched or with a broken frame or glazing;</li>
          <li>has a printing fault, such as streaks, smudges, missing areas or a badly misaligned print; or</li>
          <li>
            isn&apos;t what you designed and ordered: for example, the wrong design, size, orientation or frame, or something in
            your design that is missing or noticeably different from your final preview.
          </li>
        </ul>
        <Sub title="How to tell us">
          <ol>
            <li>
              Email <Email to={COMPANY.supportEmail} /> within <strong>30 days of delivery</strong>.
            </li>
            <li>Include your order number and a short description of the problem.</li>
            <li>
              Attach at least one clear photo of the problem. If it was damaged in transit, a photo of the packaging helps too.
            </li>
            <li>Please keep the print and packaging until we&apos;ve sorted it out.</li>
          </ol>
          <p>
            Once we&apos;ve looked at your photos, we&apos;ll offer you a <strong>free reprint</strong> (sent by the same
            delivery method you originally chose) or a <strong>full refund</strong>, including what you paid for delivery. It&apos;s
            your choice.
          </p>
        </Sub>
        <Sub title="What isn't covered">
          <ul>
            <li>
              Mistakes that were in the design you submitted, such as spelling errors, wrong dates, low-resolution or blurry
              photos, or stickers and labels placed where you put them.
            </li>
            <li>Small colour differences between your screen and the printed paper. Every screen shows colour differently.</li>
            <li>
              Map details shown in your preview, such as place names, borders or the path of an automatically calculated
              route.
            </li>
            <li>Damage caused after delivery, for example while hanging or moving the print.</li>
          </ul>
        </Sub>
      </Section>

      <Section id="lost" n={4} title="Lost or late parcels">
        <p>
          If your order hasn&apos;t arrived by the end of its estimated delivery window (see our{" "}
          <In href="/legal/shipping">Shipping &amp; Delivery policy</In>), please email us. We&apos;ll chase it with the
          courier, and if it has been lost we&apos;ll send a free reprint or give you a full refund. If the courier hasn&apos;t
          found it within 5 working days of your email, we treat it as lost.
        </p>
        <p>
          If a parcel can&apos;t be delivered because the address given at checkout was incorrect or incomplete, we can&apos;t
          offer a free reprint, but please get in touch and we&apos;ll help however we can.
        </p>
      </Section>

      <Section id="how-refunds-work" n={5} title="How refunds are paid">
        <p>
          Refunds are made to the card or payment method you used, through our payment provider Stripe. We&apos;ll process your
          refund within 14 days of agreeing that you&apos;re entitled to it. Depending on your bank, it can take a further 5 to 10
          working days to appear in your account. Refunds are made in the currency you paid in, and are for the amount you
          actually paid (after any discount code).
        </p>
      </Section>

      <Section id="your-rights" n={6} title="Your legal rights">
        <p>
          This policy is <strong>in addition to</strong> your legal rights as a consumer, and nothing in it takes them away. Even
          after our 30-day window, you may still be entitled to a repair, replacement, refund or price reduction if your print
          is faulty or not as described.
        </p>
        <ul>
          <li>
            <strong>UK:</strong> your rights under the Consumer Rights Act 2015 include a 30-day right to reject faulty goods for
            a full refund, and you may be able to make a claim for up to six years. For more, see{" "}
            <Ext href="https://www.citizensadvice.org.uk/consumer/">Citizens Advice</Ext>.
          </li>
          <li>
            <strong>Australia:</strong> our goods come with guarantees that cannot be excluded under the Australian Consumer
            Law. You are entitled to a replacement or refund for a major failure and compensation for any other reasonably
            foreseeable loss or damage. You are also entitled to have the goods repaired or replaced if the goods fail to be of
            acceptable quality and the failure does not amount to a major failure.
          </li>
          <li>
            <strong>United States:</strong> this policy applies, along with any rights given to you by the law of your state.
          </li>
        </ul>
        <p>
          Questions? Email <Email to={COMPANY.supportEmail} /> and a real person will help. You can read our full{" "}
          <In href="/legal/terms">Terms &amp; Conditions</In> too.
        </p>
      </Section>
    </>
  );
}
