import { expect, test } from "@playwright/test";

test("the site is up and protected pages stay protected", async ({ request }) => {
  expect((await (await request.get("/api/health")).json()).ok).toBe(true);
  expect((await request.get("/print/anything")).status()).toBe(404); // needs a signed token
  expect((await request.get("/admin", { maxRedirects: 0 })).status()).toBe(307); // needs sign-in
  expect((await request.post("/api/webhooks/prodigi?o=ord_x&t=bad")).status()).toBe(401);
});

test("design a map and place a (test) order", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));

  await page.goto("/");
  await page.locator('a[href="/create"]').first().click();
  await expect(page).toHaveURL(/\/create/);

  // Start from a template: stops, route and stickers appear on the map.
  await page.getByRole("button", { name: /Asia & Oz/ }).click();
  await expect(page.locator(".mapsie-stop").first()).toBeVisible();
  expect(await page.locator(".mapsie-stop").count()).toBeGreaterThan(2);

  // Change the style and the title.
  await page.getByRole("button", { name: "Style", exact: false }).filter({ hasText: /^.{0,4}Style$/ }).click();
  await page.getByRole("button", { name: /Atlas/ }).first().click();
  await page.getByRole("button", { name: /Text$/ }).filter({ hasText: /^.{0,4}Text$/ }).click();
  await page.locator("input").first().fill("Our Big Adventure");
  await expect(page.locator("#poster")).toContainText("Our Big Adventure");

  // Order -> checkout: switch to a framed print and pay (test mode).
  await page.getByRole("button", { name: /Order/ }).first().click();
  await expect(page).toHaveURL(/\/checkout\//);
  await page.getByRole("button", { name: /Add a frame/ }).click();
  await page.getByRole("button", { name: /^Black/ }).first().click();
  await expect(page.getByText("Black frame", { exact: true })).toBeVisible();
  await page.getByPlaceholder("you@example.com").fill("e2e@example.com");
  await page.getByRole("button", { name: /^Pay / }).click();

  await expect(page).toHaveURL(/\/checkout\/test\//);
  // The test checkout comes with an address filled in.
  await page.getByRole("button", { name: "Place test order" }).click();

  await expect(page).toHaveURL(/\/order\/ord_/);
  await expect(page.getByText("Thank you!")).toBeVisible();
  await expect(page.getByText("Payment received")).toBeVisible();
  await expect(page.getByRole("button", { name: "Cancel order" })).toBeVisible({ timeout: 20_000 });

  // Cancel inside the hold window.
  await page.getByRole("button", { name: "Cancel order" }).click();
  await page.getByRole("button", { name: /Yes, cancel/ }).click();
  await expect(page.getByText("Order cancelled")).toBeVisible();

  expect(errors).toEqual([]);
});
