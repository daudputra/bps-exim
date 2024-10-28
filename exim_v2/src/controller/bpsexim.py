import asyncio
import re

from ..exception import CantLoadWebPage
from ..helper import Process, log_message

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright



class BpsExim:

    def __init__(self, headless, **kwargs) -> None:
        self.url = "https://bps.go.id/id/exim"
        self.domain = "bps.go.id"
        self.desc = ""
        self.path = ""

        # ? arguments
        self.headless = headless #? headless mode
        self.exim = kwargs.get("exim") #? pilih data option 
        self.agregasi = kwargs.get("agregasi") #? agregasi option
        self.max_attempts = kwargs.get("attempt", 3) #? max attempts
        self.batch = kwargs.get("batch", None) #? batch size


    async def scrape_year(self, context):
        """ Get year to do multiple tasks """
        await log_message("DEBUG", "logs/debug.log", "Start taking the list of available years")

        try:
            page = await context.new_page()
            await page.goto(self.url)

            processing = Process(self.exim, self.desc)

            await processing.input_exim(page)
            await processing.input_agregasi(self.agregasi, page)

            await page.locator("div").filter(has_text=re.compile(r"^Pilih Tahun$")).nth(1).click()

            html_content = await page.content() 
            soup = BeautifulSoup(html_content, 'html.parser')
            listbox = soup.find('div', class_='css-qr46ko')
            list_year = [option.get_text(strip=True) for option in listbox.find_all('div')]
            
            await log_message("DEBUG", "logs/debug.log", f"Got {len(list_year)} Year : {list_year}")
            await asyncio.sleep(2)

            return list_year

        except Exception as e:
            raise e
        except TimeoutError:
            raise CantLoadWebPage("Cant load web page to scrape year")
        finally:
            await page.close()



    async def run_process(self):
        """ run playwright Process() """
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

                # list_years = await self.scrape_year(context)
                list_years = ["2024"]

                # ! Do multiple tasks
                batch_size =  self.batch if self.batch != None else len(list_years)
                for i in range(0, len(list_years), batch_size):
                    tasks = [self.process_category(context, year) for year in list_years[i:i + batch_size]]
                    await asyncio.gather(*tasks, return_exceptions=True)  

        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            await browser.close()



    async def process_category(self, context, year):
        """ Start Process by aggregasi """

        await log_message("DEBUG", "logs/debug.log", f"Start Process Task {year}")

        page = None 
        max_attempts = self.max_attempts
        attempt = 0 

        while attempt < max_attempts:
            try:
                page = await context.new_page()  
                await page.goto(self.url)

                desc = await page.locator(".text-amber-700").inner_text()
                if desc:
                    desc = desc.strip()


                processing = Process(self.exim, desc)

                await processing.input_exim(page)
                await processing.input_agregasi(self.agregasi, page)

                await page.locator("div").filter(has_text=re.compile(r"^Pilih Tahun$")).nth(1).click()
                await page.get_by_role("option", name=year).click()
                await page.locator("body").press("Escape")

                if self.agregasi == "negara":
                    await processing.negara_process(page, year)
                elif self.agregasi == "pelabuhan":
                    await processing.pelabuhan_process(page, year)
                elif "hs" in self.agregasi:
                    await processing.kode_hs_process(page, self.agregasi, year)
                else:
                    print(f"Invalid agregasi value: {self.agregasi}")
                    return

                await asyncio.sleep(5)
                print(f"processing Tab {year} Completed Successfully!")
                break 

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                attempt += 1

            finally:
                if page is not None: 
                    await page.close()
        
        if attempt == max_attempts:
            raise CantLoadWebPage(f"Failed to load the page after {max_attempts} attempts.")
