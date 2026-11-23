import { NextResponse } from "next/server";
import { sameOrigin } from "@/lib/server/rateLimit";
import { currentPartner } from "@/lib/server/partnerAuth";
import { savePartner } from "@/lib/server/partners";
import { publicUrl } from "@/lib/server/urls";

// Partner dashboard: show a map on their page, hide it, rename or remove it.
export async function POST(req: Request) {
  const f = await req.formData();
  const s = await currentPartner(String(f.get("p") ?? ""));
  if (!s) return NextResponse.redirect(`${publicUrl()}/partner/signin`, { status: 303 });
  const back = (msg: string) => NextResponse.redirect(`${publicUrl()}/partner?p=${s.partner.id}&msg=${encodeURIComponent(msg)}#maps`, { status: 303 });
  if (!sameOrigin(req, publicUrl())) return back("Please try again");
  const id = String(f.get("id") ?? "");
  const list = s.partner.designs ?? [];
  const d = list.find((x) => x.id === id);
  if (!d) return back("That map wasn't found");
  const act = String(f.get("do") ?? "");
  const name = String(f.get("name") ?? "").trim().slice(0, 80);
  const next =
    act === "remove" ? list.filter((x) => x.id !== id)
    : act === "publish" || act === "unpublish" ? list.map((x) => (x.id === id ? { ...x, published: act === "publish" } : x))
    : act === "rename" && name ? list.map((x) => (x.id === id ? { ...x, name } : x))
    : list;
  await savePartner({ ...s.partner, designs: next });
  return back(act === "publish" ? `“${d.name}” is now on your page` : act === "unpublish" ? `“${d.name}” is hidden from your page` : act === "remove" ? `“${d.name}” removed` : "Saved");
}
