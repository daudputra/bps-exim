import asyncio
import re
from playwright.async_api import Playwright, async_playwright, expect


async def run(playwright: Playwright) -> None:
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://www.bps.go.id/id/exim")
    await page.get_by_placeholder("i").check()
    await page.locator(".css-19bb58m").first.click()
    await page.get_by_role("option", name="Menurut Negara").click()
    await page.locator(".css-13cymwt-control > .css-hlgwow > .css-19bb58m").first.click()
    await page.get_by_role("option", name="2024").click()
    await page.locator("body").click()
    await page.locator(".w-full > .w-full > .css-13cymwt-control > .css-hlgwow > .css-19bb58m").first.click()
    await page.locator("body").click()
    await page.locator(".w-full > .w-full > .css-13cymwt-control > .css-hlgwow > .css-19bb58m").first.click()
    await page.get_by_role("option", name="AFGHANISTAN").click()
    await page.locator("body").click()

    # ---------------------
    await context.close()
    await browser.close()


async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())
