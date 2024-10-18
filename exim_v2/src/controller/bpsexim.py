import asyncio
import re

from ..exception import CantLoadWebPage
from ..helper import Process

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright



class BpsExim:

    def __init__(self, headless, **kwargs) -> None:
        self.url = "https://bps.go.id/id/exim"
        self.domain = "bps.go.id"

        # ? arguments
        self.headless = headless
        self.exim = kwargs.get("exim")
        self.agregasi = kwargs.get("agregasi")




    async def run_process(self):
        """ run playwright process """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                context = await browser.new_context()

                # list_year = await self.scrape_year(context)   
                list_year = ['2024', '2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014']

                # ! Do multiple tasks
                tasks = [self.process_categrory(context, year) for year in list_year]
                await asyncio.gather(*tasks)



        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            await browser.close()





    async def process_categrory(self, context, year):
        """ start process by agregasi """
        try:
            page = await context.new_page()
            await page.goto(self.url)

            await Process.input_exim(self.exim, page)
            await Process.input_agregasi(self.agregasi, page)

            await page.locator("div").filter(has_text=re.compile(r"^Pilih Tahun$")).nth(1).click()
            await page.get_by_role("option", name=year).click()
            await page.locator("body").press("Escape")

            # await page.screenshot(path=f'output/screenshot/{year}.png', full_page=True)

            if self.agregasi == "negara":
                await Process.negara_process(page)

            await asyncio.sleep(10)



        except Exception as e:
            print(f"An error occurred: {str(e)}")

        finally:
            await page.close()





    async def scrape_year(self, context):
        """ Get year to do multiple tasks """
        try:
            page = await context.new_page()
            await page.goto(self.url)

            await Process.input_exim(self.exim, page)
            await Process.input_agregasi(self.agregasi, page)

            await page.locator("div").filter(has_text=re.compile(r"^Pilih Tahun$")).nth(1).click()

            html_content = await page.content() 
            soup = BeautifulSoup(html_content, 'html.parser')
            listbox = soup.find('div', class_='css-qr46ko')
            list_year = [option.get_text(strip=True) for option in listbox.find_all('div')]
            
            print(f"Got Year : ", list_year)
            await asyncio.sleep(2)

            return list_year

        except Exception as e:
            raise e
        except TimeoutError:
            raise CantLoadWebPage
        finally:
            await page.close()




    async def json_process(self):
        pass