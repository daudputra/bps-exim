import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.bps.go.id/id/exim")
    page.get_by_placeholder("i").check()
    page.locator(".css-19bb58m").first.click()
    page.get_by_role("option", name="Menurut Pelabuhan").click()
    page.locator(".css-13cymwt-control > .css-hlgwow > .css-19bb58m").first.click()
    page.get_by_role("option", name="2024").click()
    page.locator("#react-select-5-input").press("Escape")
    page.locator(".w-full > .w-full > .css-13cymwt-control > .css-hlgwow > .css-19bb58m").first.click()
    page.get_by_role("option", name="ABDULRACHMAN SALEH (U)").click()
    page.locator("#react-select-6-input").press("Escape")
    page.get_by_role("button", name="Buat Tabel").click()
    page.locator("div:nth-child(7) > div > .w-full > .css-13cymwt-control > .css-hlgwow > .css-19bb58m").click()
    page.get_by_role("option", name="Januari").click()
    page.locator("#react-select-3-input").press("Escape")
    page.get_by_role("button", name="Buat Tabel").click()
    page.get_by_role("button", name="▾ Nilai / Net Value (US $)").click()
    page.get_by_role("button", name="Nilai / Net Value (US $)", exact=True).click()
    page.get_by_role("button", name="▾ Nilai / Net Value (US $)").click()
    page.get_by_role("button", name="Berat / Net Weight (KG)", exact=True).click()
    page.get_by_role("button", name="Berat / Net Weight (KG)").click()



    # page.get_by_role("button", name="▾ Berat / Net Weight (KG)").click()
    # page.get_by_role("button", name="Nilai / Net Value (US $)").click()
    # page.get_by_role("button", name="Nilai / Net Value (US $)", exact=True).dblclick()
    # page.get_by_role("button", name="▾ Nilai / Net Value (US $)").click()
    # page.get_by_role("button", name="Berat / Net Weight (KG)").click()
    # page.get_by_role("button", name="Berat / Net Weight (KG)", exact=True).dblclick()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
