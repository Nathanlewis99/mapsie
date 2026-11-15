"use client";
/** A submit button that asks first (for refunds and reprints). */
export default function ConfirmButton({ message, className, disabled, children }: { message: string; className: string; disabled?: boolean; children: React.ReactNode }) {
  return (
    <button className={className} disabled={disabled} onClick={(e) => !confirm(message) && e.preventDefault()}>
      {children}
    </button>
  );
}
