import type { Metadata } from "next";
import { COMPANY } from "@/lib/company";
import { money, REGIONS, SHIPPING } from "@/lib/products";
import { Email, In, LegalTitle, Section, Summary, Table} from "../_ui";

export const metadata: Metadata = {
  title: "Shipping & Delivery · Mapsie",
  description: "Where Mapsie delivers, how long your print takes, delivery costs, and customs.",
};

const countries = REGIONS.map((r) => r.label).join(", ").replace(/, ([^,]*)$/, " and $1");

export default function ShippingPage() {
  return (
    <>
      <LegalTitle
        title="Shipping & Delivery"
        intro="Your print is made to order and printed close to you, so it arrives quickly and in good shape."
      />

      <Summary>
        <ul>
          <li>We deliver to the {countries}.</li>
          <li>Prints are usually dispatched within 2 to 4 working days of your order.</li>
          <li>Standard delivery is free and takes 3 to 5 working days after dispatch. Express takes 1 to 2.</li>
          <li>We print locally in each region, so you shouldn&apos;t normally pay import duties or taxes.</li>
        </ul>
      </Summary>

      <Section id="where" n={1} title="Where we deliver">
        <p>
          We currently deliver to addresses in the {countries}. Prices are shown in the currency of the country you&apos;re
          delivering to, and the delivery address must be in that country. We can&apos;t deliver anywhere else yet.
        </p>
      </Section>

      <Section id="production" n={2} title="Making your print">
        <p>
          Every print is made to order. Once you&apos;ve paid, your design is sent to our print partner, Prodigi, who print it
          (and frame it, if you chose a frame) at a production site in or near your country. Orders are usually dispatched{" "}
          <strong>within 2 to 4 working days</strong>. Busy periods, such as the run-up to Christmas, can take a little longer.
        </p>
      </Section>

      <Section id="options" n={3} title="Delivery options and costs">
        <p>Delivery times are counted from dispatch, so add them to the production time above.</p>
        <Table
          head={["Option", "Time after dispatch", ...REGIONS.map((r) => `${r.flag} ${r.label}`)]}
          rows={SHIPPING.map((s) => [
            <strong key="l">{s.id === "standard" ? "Standard" : s.label}</strong>,
            s.detail,
            ...REGIONS.map((r) => (s.price[r.id] === 0 ? "Free" : money(r.id, s.price[r.id]))),
          ])}
        />
        <p>
          So, for example, a print sent by standard delivery will typically arrive within 5 to 9 working days of your order,
          and by express within 3 to 6 working days. &ldquo;Working days&rdquo; means Monday to Friday, excluding public holidays
          where your print is made and delivered.
        </p>
        <p>
          These are estimates, not guarantees. Delivery is handled by local couriers and postal services, and occasionally
          parcels take longer, especially to remote areas.
        </p>
      </Section>

      <Section id="tracking" n={4} title="Tracking your order">
        <p>
          You can check the progress of your order on your order page, and in your order history if you&apos;re signed in.{" "}
          When your print is dispatched we&apos;ll email you, with the courier&apos;s tracking link where the courier provides one.
        </p>
      </Section>

      <Section id="customs" n={5} title="Customs, duties and taxes">
        <p>
          Because we print in the region you&apos;re ordering from, your print normally won&apos;t cross a border and you
          shouldn&apos;t have to pay any import duties or taxes on delivery. If, exceptionally, your order has to be sent from
          another country and duties or taxes become payable, they&apos;re your responsibility. If that happens and you
          weren&apos;t told before ordering, please contact us.
        </p>
      </Section>

      <Section id="address" n={6} title="Your delivery address">
        <p>
          Please double-check your address at checkout. Your order goes to print quickly, and once it has, we can&apos;t change
          the delivery address. If you&apos;ve made a mistake, email <Email to={COMPANY.supportEmail} /> straight away and
          we&apos;ll do our best.
        </p>
      </Section>

      <Section id="problems" n={7} title="Late, lost or damaged deliveries">
        <p>
          Your print is our responsibility until it&apos;s delivered. If it&apos;s late, lost or arrives damaged, please email{" "}
          <Email to={COMPANY.supportEmail} /> and we&apos;ll put it right. See our{" "}
          <In href="/legal/refunds">Returns, Refunds &amp; Reprints policy</In> for details. If we don&apos;t deliver within 30
          days of your order, you can cancel and get a full refund.
        </p>
      </Section>
    </>
  );
}
