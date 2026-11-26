import { applyPreset } from "./lookMatch";
import { useEditor } from "./store";
import { PRESETS } from "./themes";

/** The style they arrived in from an ad, kept when an example or AI trip comes in with its own style. */
export function keepAdStyle() {
  let id: string | null = null;
  try {
    id = sessionStorage.getItem("mapsie-style");
  } catch {}
  const p = PRESETS.find((x) => x.id === id);
  if (!p) return;
  const ed = useEditor.getState();
  ed.set(applyPreset(ed.design, p));
}

