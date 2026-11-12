// Small line icons (24px grid, 1.75 stroke) used in the editor chrome, so the
// interface matches the clean, understated logo rather than emoji.
const PATHS: Record<string, string> = {
  undo: "M9 14 4 9l5-5M4 9h10.5a5.5 5.5 0 0 1 0 11H11",
  redo: "m15 14 5-5-5-5M20 9H9.5a5.5 5.5 0 0 0 0 11H13",
  wall: "M4 21V5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v16M2 21h20M8 8h8v7H8z",
  share: "M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7",
  save: "M6 3h12a1 1 0 0 1 1 1v17l-7-4-7 4V4a1 1 0 0 1 1-1z",
  check: "M5 12.5 10 17.5 19 7",
  heart: "M12 20.5s-7.5-4.6-9.2-9.6C1.6 7.4 3.8 4 7.3 4c2 0 3.6 1.1 4.7 2.7C13.1 5.1 14.7 4 16.7 4c3.5 0 5.7 3.4 4.5 6.9-1.7 5-9.2 9.6-9.2 9.6z",
  plus: "M12 5v14M5 12h14",
  globe: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM3.6 9h16.8M3.6 15h16.8M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18",
  route: "M6 19a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM18 9a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM8 17h6.5a3.5 3.5 0 0 0 0-7h-5a3.5 3.5 0 0 1 0-7H16",
  palette: "M12 21a9 9 0 1 1 9-9c0 2.2-1.8 3-3.5 3H16a2 2 0 0 0-1.4 3.4A1.6 1.6 0 0 1 12 21zM7.5 11.5h.01M10 7.5h.01M15 7.5h.01",
  sticker: "M15.5 3H6a3 3 0 0 0-3 3v12a3 3 0 0 0 3 3h7l8-8V6a3 3 0 0 0-3-3h-2.5zM13 21v-5a3 3 0 0 1 3-3h5",
  type: "M5 6V4h14v2M12 4v16M9 20h6",
  frame: "M4 4h16v16H4zM8 8h8v8H8z",
};

export default function Icon({ name, size = 18, className = "" }: { name: keyof typeof PATHS | string; size?: number; className?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={`shrink-0 ${className}`}
      aria-hidden
    >
      <path d={PATHS[name] ?? ""} />
    </svg>
  );
}
