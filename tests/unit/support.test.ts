import { describe, expect, it } from "vitest";
import { newTicketId, ticketToken, ticketTokenValid } from "../../src/lib/server/support";
import { REASONS, reasonFor } from "../../src/lib/support";

describe("support", () => {
  it("ticket ids are short and easy to read out", () => {
    const id = newTicketId();
    expect(id).toMatch(/^MS-[2-9A-HJKMNP-Z]{6}$/);
  });
  it("ticket links are checked", () => {
    expect(ticketTokenValid("MS-ABCDEF", ticketToken("MS-ABCDEF"))).toBe(true);
    expect(ticketTokenValid("MS-ABCDEG", ticketToken("MS-ABCDEF"))).toBe(false);
    expect(ticketTokenValid("MS-ABCDEF", "")).toBe(false);
  });
  it("damage and quality problems need a photo", () => {
    expect(reasonFor("damaged").photos).toBe("required");
    expect(reasonFor("quality").photos).toBe("required");
    expect(reasonFor("nonsense").id).toBe("other");
    expect(new Set(REASONS.map((r) => r.id)).size).toBe(REASONS.length);
  });
});
