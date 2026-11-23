import { NextResponse } from "next/server";
import { sameOrigin } from "@/lib/server/rateLimit";
import { currentPartner, sealPayout } from "@/lib/server/partnerAuth";
import { savePartner } from "@/lib/server/partners";
import { alertAdmin, sendEmail } from "@/lib/server/email";
import { publicUrl } from "@/lib/server/urls";
import { cleanPayout, payoutSummary } from "@/lib/partners";

// Partner dashboard: their billing details (for trade invoices) and how they'd like commission paid.
export async function POST(req: Request) {
  const f = await req.formData();
  const s = await currentPartner(String(f.get("p") ?? ""));
  const back = (msg: string) => NextResponse.redirect(`${publicUrl()}/partner?p=${s?.partner.id ?? ""}&msg=${encodeURIComponent(msg)}#details`, { status: 303 });
  if (!s) return NextResponse.redirect(`${publicUrl()}/partner/signin`, { status: 303 });
  if (!sameOrigin(req, publicUrl())) return back("Please try again");
  const get = (k: string, max = 200) => String(f.get(k) ?? "").trim().slice(0, max);
  const p = s.partner;
  if (get("do") === "billing") {
    if (!get("company", 120) || !get("address", 400)) return back("Add your company name and address");
    const invoiceEmail = get("invoiceEmail", 120);
    if (invoiceEmail && !/^\S+@\S+\.\S+$/.test(invoiceEmail)) return back("That invoice email doesn't look right");
    await savePartner({ ...p, billing: { company: get("company", 120), address: get("address", 400), vatNumber: get("vatNumber", 30) || undefined, invoiceEmail: invoiceEmail || undefined } });
    return back("Billing details saved");
  }
  if (get("do") === "payout") {
    const r = cleanPayout(Object.fromEntries([...f.entries()].map(([k, v]) => [k, String(v)])));
    if (typeof r === "string") return back(r);
    const summary = payoutSummary(r);
    await savePartner({ ...p, payoutDetails: { sealed: sealPayout(r), summary, updatedAt: new Date().toISOString() } });
    // So a changed bank account never goes unnoticed before the next payment.
    await alertAdmin(`Partner payout details changed: ${p.name}`, `${p.name} (${p.id}) updated how they're paid, signed in as ${s.email}.\nNew: ${summary}\nPrevious: ${p.payoutDetails?.summary ?? "none"}\n\nCheck it's genuine before the next payment: ${publicUrl()}/admin/partners?p=${p.id}`);
    // And tell everyone who can sign in for this partner, in case it wasn't them.
    for (const to of p.logins ?? []) {
      await sendEmail({
        to,
        subject: "Your Mapsie payment details were changed",
        text: `Hi,\n\nThe details we use to pay ${p.name}'s commission were just changed (by ${s.email}) to: ${summary}.\n\nIf this wasn't you or a colleague, reply to this email straight away and we'll hold any payments.\n\nMapsie`,
        html: `<p>Hi,</p><p>The details we use to pay ${p.name.replace(/[<>&"]/g, "")}'s commission were just changed (by ${s.email.replace(/[<>&"]/g, "")}) to: <b>${summary.replace(/[<>&"]/g, "")}</b>.</p><p>If this wasn't you or a colleague, reply to this email straight away and we'll hold any payments.</p><p>Mapsie</p>`,
      }).catch(() => {});
    }
    return back("Payment details saved");
  }
  return back("Nothing changed");
}
