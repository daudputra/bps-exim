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
        self.max_attempts = kwargs.get("max_attempts", 3)


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
            
            print(f"Got {len(list_year)} Year : ", list_year)
            await asyncio.sleep(2)

            return list_year

        except Exception as e:
            raise e
        except TimeoutError:
            raise CantLoadWebPage("Cant load web page to scrape year")
        finally:
            await page.close()



    async def run_process(self):
        """ run playwright process """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless, args=[
                    '--disable-gpu', 
                    '--no-sandbox', 
                    '--disable-dev-shm-usage', 
                    '--disable-extensions', 
                    '--disable-background-timer-throttling', 
                    '--disable-backgrounding-occluded-windows', 
                    '--disable-infobars', 
                    '--window-size=1280,800'
                ])
                context = await browser.new_context()


                # ? ignore image and media to compress memory and cpu usage
                await context.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "stylesheet"] else route.continue_())


                list_years = await self.scrape_year(context)   
                # list_year = ['2024']

                # ! Do multiple tasks
                # tasks = [self.process_category(context, year) for year in list_years]
                # await asyncio.gather(*tasks)

                batch_size = len(list_years)
                for i in range(0, len(list_years), batch_size):
                    tasks = [self.process_category(context, year) for year in list_years[i:i + batch_size]]
                    await asyncio.gather(*tasks)  

                

        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            await browser.close()



    async def process_category(self, context, year):
        """ Start process by aggregasi """
        page = None 
        max_attempts = self.max_attempts
        attempt = 0 

        while attempt < max_attempts:
            try:
                page = await context.new_page()  
                await page.goto(self.url)

                await Process.input_exim(self.exim, page)
                await Process.input_agregasi(self.agregasi, page)

                await page.locator("div").filter(has_text=re.compile(r"^Pilih Tahun$")).nth(1).click()
                await page.get_by_role("option", name=year).click()
                await page.locator("body").press("Escape")

                if self.agregasi == "negara":
                    await Process.negara_process(page)
                elif self.agregasi == "pelabuhan":
                    await Process.pelabuhan_process(page)
                elif "hs" in self.agregasi:
                    await Process.kode_hs_process(page, self.agregasi)
                else:
                    print(f"Invalid agregasi value: {self.agregasi}")
                    return

                await asyncio.sleep(5)
                print(f"Process Tab {year} Completed Successfully!")
                break 

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                attempt += 1

            finally:
                if page is not None: 
                    await page.close()
        
        if attempt == max_attempts:
            raise CantLoadWebPage(f"Failed to load the page after {max_attempts} attempts.")

    async def json_process(self):
        pass












    # async def process_category(self, context, year):
    #     """ start process by agregasi """
    #     try:
    #         page = await context.new_page()
    #         await page.goto(self.url)

    #         await Process.input_exim(self.exim, page)
    #         await Process.input_agregasi(self.agregasi, page)

    #         await page.locator("div").filter(has_text=re.compile(r"^Pilih Tahun$")).nth(1).click()
    #         await page.get_by_role("option", name=year).click()
    #         await page.locator("body").press("Escape")

    #         # await page.screenshot(path=f'output/screenshot/{year}.png', full_page=True)

    #         if self.agregasi == "negara":
    #             await Process.negara_process(page)
    #         elif self.agregasi == "pelabuhan":
    #             await Process.pelabuhan_process(page)
    #         elif "hs" in self.agregasi:
    #             await Process.kode_hs_process(page, self.agregasi)
    #         else:   
    #             print(f"Invalid agregasi value: {self.agregasi}")
    #             return
            
    #         await asyncio.sleep(5)


    #         print(f"Process Tab {year} Completed Successfully!")

    #     except Exception as e:
    #         print(f"An error occurred: {str(e)}")

    #     finally:
    #         await page.close()