import re
import asyncio

from bs4 import BeautifulSoup

from ..exception import FailedInputCategory

class Process:

    async def close_popup(page):
        """tutup popup "jika ada" pada saat masuk ke dalam page"""
        close_button = page.locator('//html/body/div[5]/div/div/div/div/div/div/div[2]/button')

        if not await close_button.is_visible():
            pass
        else:
            await close_button.wait_for(timeout=36000000)
            if await close_button.count() > 0:
                await close_button.click()


    async def input_exim(exim:str, page):
        try:
            """ click exim radio button """
            if "i" in exim:
                exim_placeholder = "i"
            elif "e" in exim:
                exim_placeholder = "e"
            await page.get_by_placeholder(exim_placeholder).click()
        except Exception as e:
            print(f"Error input exim: {e}")
            raise FailedInputCategory("Invalid input exim")


    async def input_agregasi(agregasi: str, page):
        """ Input agregasi """

        try:
            await page.locator(".css-19bb58m").first.click()
            
            if "hs" in agregasi:

                await page.get_by_role("option", name="Menurut Kode HS").click()
                await page.locator(".css-13cymwt-control > .css-hlgwow > .css-19bb58m").first.click()

                if agregasi == "hs_full":
                    await page.get_by_role("option", name="HS Full").click()

                elif agregasi == "hs_digit":
                    await page.get_by_role("option", name="HS 2 Digit").click()

            elif agregasi == "negara": 
                await page.get_by_role("option", name="Menurut Negara").click()

            elif agregasi == "pelabuhan":
                await page.get_by_role("option", name="Menurut Pelabuhan").click()


        except Exception as e:
            print(f"Error input agregasi: {e}")
            raise FailedInputCategory("Invalid input Agregasi")




    async def negara_process(page):
        """Prpcess category negara"""
        try:
            async def get_negara_text(page):
                await page.locator("div").filter(has_text=re.compile(r"^Pilih Negara$")).nth(1).click()

                html_content = await page.content()
                soup = BeautifulSoup(html_content, "html.parser")
                listbox = soup.find('div', class_='css-qr46ko')
                list_negara = [negara.get_text(strip=True) for negara in listbox.find_all('div')]

                await page.locator("body").press("Escape")
                return list_negara
            
            list_negara = await get_negara_text(page)
            

            for negara in list_negara:
                await page.locator("div").filter(has_text=re.compile(r"^Pilih Negara$")).nth(1).click()
                negara_locators = page.get_by_role("option", name=negara, exact=True)

                count = await negara_locators.count()

                # ! jika ada nama yang sama dia akan di click semua tetapi setelah itu dia akan melakukan click lagi dengan nama yang sama
                if count > 1:
                    options = await page.query_selector_all(f"role=option[name={negara}]")
                    for option in options:
                        await option.click();
                        print(await option.inner_text())
                else:
                    print(await negara_locators.inner_text())
                    await negara_locators.click()

                # ! lanjut proses disini
                # ....
                

                await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(6) > div > div > div > div.css-1wy0on6 > div:nth-child(1)').click()# ? X
                await page.locator("div").filter(has_text=re.compile(r"^Pilih Negara$")).nth(1).click()


        except Exception as e:
            print(f"Error negara: {e}")
            raise FailedInputCategory("Failed to select negara")



    async def pelabuhan_process(page):
        """Process category pelabuhan"""
        try:
            async def get_pelabuhan_text(page):
                await page.locator("div").filter(has_text=re.compile(r"^Pilih Pelabuhan$")).nth(1).click()

                html_content = await page.content()
                soup = BeautifulSoup(html_content, "html.parser")
                listbox = soup.find('div', class_='css-qr46ko')
                list_pelabuhan = [pelabuhan.get_text(strip=True) for pelabuhan in listbox.find_all('div')]

                await page.locator("body").press("Escape")
                return list_pelabuhan
            
            list_pelabuhan = await get_pelabuhan_text(page)
            

            for pelabuhan in list_pelabuhan:
                await page.locator("div").filter(has_text=re.compile(r"^Pilih Pelabuhan$")).nth(1).click()
                pelabuhan_locators = page.get_by_role("option", name=pelabuhan, exact=True)

                count = await pelabuhan_locators.count()

                # ! jika ada nama yang sama dia akan di click semua tetapi setelah itu dia akan melakukan click lagi dengan nama yang sama
                if count > 1:
                    options = await page.query_selector_all(f"role=option[name='{pelabuhan}']")
                    for option in options:
                        await option.click();
                        print(await option.inner_text())
                else:
                    print(await pelabuhan_locators.inner_text())
                    await pelabuhan_locators.click()

                # ! lanjut proses disini
                # ....

                await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(5) > div > div > div > div.css-1wy0on6 > div:nth-child(1)').click() #? X
                await page.locator("div").filter(has_text=re.compile(r"^Pilih Pelabuhan$")).nth(1).click()

        except Exception as e:
            print(f"Error pelabuhan: {e}")
            raise FailedInputCategory("Failed to select pelabuhan")



    async def kode_hs_process(page, kode_hs):
        """process category kode hs"""
        try:
            if "digit" in kode_hs:
                """process category kode hs"""
                
                async def get_digit_count(page):
                    """get digit list"""
                    await page.locator("div").filter(has_text=re.compile(r"^Ketikkan Kode HS$")).nth(1).click()
                    await page.wait_for_function("document.querySelector('.css-qr46ko').innerText !== 'Loading...'")

                    html_content = await page.content()
                    soup = BeautifulSoup(html_content, "html.parser")
                    listbox = soup.find('div', class_='css-qr46ko')
                    list_digits = [digit.get_text(strip=True) for digit in listbox.find_all('div')]

                    await page.locator("body").press("Escape")
                    return list_digits

                list_digits = await get_digit_count(page)
                for digit in list_digits:

                    await page.locator("div").filter(has_text=re.compile(r"^Ketikkan Kode HS$")).nth(1).click()
                    digit_locators = page.get_by_role("option", name=digit, exact=True)

                    await page.wait_for_function("document.querySelector('.css-qr46ko').innerText !== 'Loading...'")

                    print(await digit_locators.inner_text())
                    await digit_locators.click()
                    await asyncio.sleep(1)

                    # ! lanjut proses disini
                    # ....

                    await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(4) > div.w-full.mt-2 > div > div > div.css-1wy0on6 > div:nth-child(1)').click() #? X
                    await page.locator("div").filter(has_text=re.compile(r"^Ketikkan Kode HS$")).nth(1).click()

            elif "full" in kode_hs:
                """process category kode full"""
                try:
                    pass
                # ! inprogress
                    # index = 0
                    # while True:
                    #     await page.locator("div").filter(has_text=re.compile(r"^Ketikkan Kode HS$")).nth(1).click()
                    #     full_locator = page.locator(f"#react-select-10-option-{index}")

                    #     await full_locator.click()
                    #     print(await full_locator.inner_text())

                    #     # await asyncio.sleep(20)
                        
                    #     # await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(4) > div.w-full.mt-2 > div > div > div.css-1wy0on6 > div:nth-child(1)').click() #? X
                    #     await page.locator('//*[@id="ss"]/div[2]/div[4]/div[2]/div/div/div[2]/div[1]').click() #? X

                    #     index += 1


                except Exception as e:
                    print(f"Error kode_hs: {e}")
                    raise FailedInputCategory("Failed to select kode_hs_full")


        except Exception as e:
            print(f"Error kode_hs: {e}")
            raise FailedInputCategory(f"Failed to select {kode_hs}")











    async def check_table(self, page):
        pass

    async def bulan_process(page):
        """Process category bulan"""
        await page.get_by_role("button", name="Buat Tabel").click()