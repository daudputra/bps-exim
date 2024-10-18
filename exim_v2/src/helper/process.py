import re
import asyncio

from bs4 import BeautifulSoup

from ..exception import FailedInputCategory

class Process:


    async def close_popup(page):
        """tutup popup jika ada pada saat masuk ke dalam page"""
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
            
            if "kode_hs" in agregasi:

                await page.get_by_role("option", name="Menurut Kode HS").click()
                await page.locator(".css-13cymwt-control > .css-hlgwow > .css-19bb58m").first.click()

                if agregasi == "kode_hs_full":
                    await page.get_by_role("option", name="HS Full").click()

                elif agregasi == "kode_hs_digit":
                    await page.get_by_role("option", name="HS 2 Digit").click()

            elif agregasi == "negara": 
                await page.get_by_role("option", name="Menurut Negara").click()

            elif agregasi == "pelabuhan":
                await page.get_by_role("option", name="Menurut Pelabuhan").click()


        except Exception as e:
            print(f"Error input agregasi: {e}")
            raise FailedInputCategory("Invalid input Agregasi")
        

    
    async def negara_process(page):
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
                negara_locators = page.get_by_role("option", name="CURACAO", exact=True)

                count = await negara_locators.count()

                # ! belum bisa mengatasi negara yang memiliki nama sama
                if count > 1    :
                    for i in range(count):
                        pass
                        # print(await negara_locators.nth(i).inner_text())
                        # await negara_locators.nth(i).click()
                        # await page.locator("#react-select-8-input").fill("CURACAO")

                else:
                    print(await negara_locators.inner_text())
                    await negara_locators.click()

                await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(6) > div > div > div > div.css-1wy0on6 > div:nth-child(1)').click()# ? X
                await page.locator("div").filter(has_text=re.compile(r"^Pilih Negara$")).nth(1).click()


        except Exception as e:
            print(f"Error negara: {e}")
            raise FailedInputCategory("Failed to select negara")
        

    async def bulan_process(page):
        await page.get_by_role("button", name="Buat Tabel").click()
