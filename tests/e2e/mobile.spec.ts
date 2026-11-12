import { expect, test } from "@playwright/test";

test("the editor works on a phone, including lock-and-zoom", async ({ page }) => {
  await page.goto("/create?new=1");
  await page.getByRole("button", { name: /Asia & Oz/ }).click();
  await expect(page.locator(".mapsie-stop").first()).toBeVisible();
  await page.getByRole("button", { name: /Lock framing/ }).click();
  await page.getByRole("button", { name: "Zoom in" }).click();
  await expect(page.getByRole("button", { name: /Framing locked/ })).toBeVisible();
  // The page itself must not scroll sideways on a phone.
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)).toBe(true);
});
