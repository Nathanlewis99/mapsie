// Relevance scoring for sticker search. Whole-word matches in the name beat
// matches in descriptions, and a word has to start a word to count, so "car"
// finds a car before "Caribbean" scenery and never a parrot.

const words = (s: string) => s.toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
// "cars" -> "car", "beaches" -> "beach", "noodles" -> "noodle"
const stem = (w: string) => (w.length > 4 && w.endsWith("es") && !w.endsWith("ses") ? w.slice(0, -2) : w.length > 3 && w.endsWith("s") && !w.endsWith("ss") ? w.slice(0, -1) : w);

export interface SearchFields {
  name: string; // the thing's name: best match
  tags?: string; // synonyms and search words
  extra?: string; // category, region, description
}

/** 0 = no match. Every query word must match somewhere. */
export function scoreMatch(query: string, f: SearchFields): number {
  const q = words(query).map(stem);
  if (!q.length) return 0;
  const name = words(f.name).map(stem);
  const tags = words(f.tags ?? "").map(stem);
  const extra = words(f.extra ?? "").map(stem);
  let total = 0;
  for (const w of q) {
    const best = Math.max(
      name.includes(w) ? 100 : name.some((t) => t.startsWith(w)) ? 60 : 0,
      tags.includes(w) ? 45 : tags.some((t) => t.startsWith(w)) ? 25 : 0,
      extra.includes(w) ? 15 : w.length >= 4 && extra.some((t) => t.startsWith(w)) ? 6 : 0,
    );
    if (!best) return 0;
    total += best;
  }
  // The whole query is the name ("car" -> "Car"): top of the list.
  if (name.join(" ") === q.join(" ")) total += 50;
  // Short, simple names first among equals.
  return total - name.length;
}

export function rank<T>(items: T[], query: string, fields: (x: T) => SearchFields): T[] {
  return items
    .map((x, i) => ({ x, i, s: scoreMatch(query, fields(x)) }))
    .filter((r) => r.s > 0)
    .sort((a, b) => b.s - a.s || a.i - b.i)
    .map((r) => r.x);
}
