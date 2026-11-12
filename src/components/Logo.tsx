/**
 * The Mapsie wordmark: "Mapsie" in the display face with a coral map pin for
 * the full stop. Real text (sized with the parent's font-size), so it stays crisp
 * and selectable. Vector versions live in design/brand/out/.
 */
export default function Logo({ className = "" }: { className?: string }) {
  return (
    <span className={`font-display font-extrabold tracking-tight inline-flex items-baseline ${className}`} aria-label="Mapsie">
      <span aria-hidden>Mapsie</span>
      <svg aria-hidden viewBox="0 0 24 32" className="text-coral" style={{ width: "0.32em", height: "0.43em", marginLeft: "0.05em" }}>
        <path
          d="M12 31C10.6 27.5 2 21 2 12A10 10 0 1 1 22 12C22 21 13.4 27.5 12 31Z"
          fill="currentColor"
        />
        <circle cx="12" cy="12" r="4.2" fill="#FBF6EE" />
      </svg>
    </span>
  );
}
