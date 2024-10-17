import asyncio

from playwright.async_api import async_playwright

class BpsExim:

    def __init__(self) -> None:
        self.url = "https://bps.go.id/id/exim"
        self.domain = "bps.go.id"

    async def run_process(self):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            browser.close()