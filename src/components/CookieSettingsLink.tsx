"use client";
import { openCookieSettings } from "@/lib/consent";

/** Footer link to change cookie choices (only useful once optional tags are set up). */
export default function CookieSettingsLink() {
  return (
    <button type="button" onClick={openCookieSettings} className="hover:text-coral-dark font-bold">
      Cookie settings
    </button>
  );
}
