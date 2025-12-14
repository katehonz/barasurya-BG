import { type Page, expect, test } from "@playwright/test"
import { firstSuperuser, firstSuperuserPassword } from "./config"
import { randomTeamName } from "./utils/random"

const login = async (page: Page) => {
  await page.goto("/login")
  await page.getByPlaceholder("Email").fill(firstSuperuser)
  await page.getByPlaceholder("Password", { exact: true }).fill(firstSuperuserPassword)
  await page.getByRole("button", { name: "Log In" }).click()
  await page.waitForURL("/")
}

test.describe("Organization", () => {
  test("Create a new organization", async ({ page }) => {
    await login(page)

    // Open the organization switcher
    await page.getByRole("button", { name: /Organization/ }).click()

    // Click the "Create New Organization" button
    await page.getByRole("menuitem", { name: "Create New Organization" }).click()

    // Fill out the form
    const orgName = randomTeamName()
    const orgSlug = orgName.toLowerCase().replace(/\s+/g, "-")
    await page.getByPlaceholder("Enter organization name").fill(orgName)
    await page.getByPlaceholder("Enter organization slug").fill(orgSlug)

    // Click the "Create" button
    await page.getByRole("button", { name: "Create" }).click()

    // Wait for the success message or for the new organization to appear in the switcher
    await expect(page.getByText(`${orgName}`)).toBeVisible()
  })
})
