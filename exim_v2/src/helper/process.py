# body > div > div > h2 


import re
import asyncio
import os

from bs4 import BeautifulSoup

from ..exception import FailedInputCategory, CantDownloadFiles

from .save_json import SaveJson

class Process:
    def __init__(self, exim, desc) -> None:
        self.exim_text = None
        if "i" in exim: self.exim_text = "impor"
        elif "e" in exim: self.exim_text = "ekspor"

        self.negara_text = None
        self.bulan_text = None
        self.pelabuhan_text = None
        self.year_text = None
        self.agregasi_text = None
        self.jenis_hs = None
        self.desc = desc



    async def close_popup(self, page):
        """tutup popup "jika ada" pada saat masuk ke dalam page"""
        close_button = page.locator('//html/body/div[5]/div/div/div/div/div/div/div[2]/button')

        if not await close_button.is_visible():
            pass
        else:
            await close_button.wait_for(timeout=36000000)
            if await close_button.count() > 0:
                await close_button.click()


    async def input_exim(self, page):
        """ click exim radio button """
        try:
            if "i" in self.exim_text:
                exim_placeholder = "i"
            elif "e" in self.exim_text:
                exim_placeholder = "e"
            await page.get_by_placeholder(exim_placeholder).click()


        except Exception as e:
            print(f"Error input exim: {e}")
            raise FailedInputCategory("Invalid input exim")






    async def __negara_pick(self, page, negara):
        await page.locator("div").filter(has_text=re.compile(r"^Pilih Negara$")).nth(1).click()
        negara_locators = page.get_by_role("option", name=negara, exact=True)

        count = await negara_locators.count()

        # ! jika ada nama yang sama dia akan di click semua tetapi setelah itu dia akan melakukan click lagi dengan nama yang sama
        if count > 1:
            options = await page.query_selector_all(f"role=option[name={negara}]")
            for option in options:
                await option.click()
                # print(await option.inner_text())
        else:
            # print(await negara_locators.inner_text())
            await negara_locators.click()

        await page.locator("body").press("Escape")




    async def __pelabuhan_pick(self, page, pelabuhan):
        await page.locator("div").filter(has_text=re.compile(r"^Pilih Pelabuhan$")).nth(1).click()
        pelabuhan_locators = page.get_by_role("option", name=pelabuhan, exact=True)

        count = await pelabuhan_locators.count()

        # ! jika ada nama yang sama dia akan di click semua tetapi setelah itu dia akan melakukan click lagi dengan nama yang sama
        if count > 1:
            options = await page.query_selector_all(f"role=option[name='{pelabuhan}']")
            for option in options:
                await option.click()
                # print(await option.inner_text())
        else:
            # print(await pelabuhan_locators.inner_text())
            await pelabuhan_locators.click()

        await page.locator("body").press("Escape")
        await asyncio.sleep(1)




    async def input_agregasi(self, agregasi: str, page):
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


    async def return_datas(self):
        """Return Data"""
        xlsx_names = [
            f"{self.bulan_text}_(us$).xlsx",
            f"{self.bulan_text}_(kg).xlsx"
        ]

        print(self.agregasi_text)
        if "hs" in self.agregasi_text:
            return {
                "tipe_data" : self.exim_text,
                "agregasi" : self.agregasi_text,
                "tahun" : self.year_text,
                "negara" : self.negara_text,
                "pelabuhan" : self.pelabuhan_text,
                "bulan" : self.bulan_text,  
                "filename_xlsx" : xlsx_names,
            }
        
        elif "negara" in self.agregasi_text.lower():
            return {
                "tipe_data" : self.exim_text,
                "agregasi" : self.agregasi_text,
                "tahun" : self.year_text,
                "negara" : self.negara_text,
                "bulan" : self.bulan_text,
                "filename_xlsx" : xlsx_names,
            }
        elif "pelabuhan" in self.agregasi_text.lower():
            return {
                "tipe_data" : self.exim_text,
                "agregasi" : self.agregasi_text,
                "tahun" : self.year_text,
                "pelabuhan" : self.pelabuhan_text,
                "bulan" : self.bulan_text,
                "filename_xlsx" : xlsx_names,
            }
        else:
            # ! ganti dengan exception lains
            raise FailedInputCategory("Failed Return Datas")


    async def negara_process(self, page, year):
        """Prpcess category negara"""

        self.year_text = year
        self.agregasi_text = "Menurut Negara"

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
                await self.__negara_pick(page, negara)

                # ! lanjut proses disini
                # ....

                list_bulan = await self.check_table(page, "negara")
                # ? bulan option process and download file
                if list_bulan is not None:
                    for bulan_option in list_bulan:
                        
                        # ? path to save files
                        path_files = f"{self.exim_text}/menurut_negara/{year}/{negara.lower().replace(" ","_")}"

                        # ? datas to data
                        self.negara_text = negara
                        self.bulan_text = bulan_option.split()[1]


                        await self.bulan_process(page, bulan_option)
                        await self.download_files(page, f"data/{path_files}/xlsx/", self.bulan_text)

                        try:
                            data = await self.return_datas()
                            setup_json = SaveJson(self.year_text, data, "", self.desc)
                            await setup_json.save_json_local(f"{self.bulan_text.lower()}.json", f"{path_files}/json/")
                        except Exception as e:
                            #! ganti exception ini
                            print("Error saving json")
                            raise e

                        await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(7) > div > div > div > div.css-1wy0on6 > div:nth-child(1)').click() #? bulan X
                await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(6) > div > div > div > div.css-1wy0on6 > div:nth-child(1)').click()# ? X


        except Exception as e:
            print(f"Error negara: {e}")
            raise FailedInputCategory("Failed to select negara")







    async def pelabuhan_process(self, page, year):
        """Process category pelabuhan"""

        self.year_text = year
        self.agregasi_text = "Menurut Pelabuhan"

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
                await self.__pelabuhan_pick(page, pelabuhan)

                # ! lanjut proses disini
                # ....

                list_bulan = await self.check_table(page, "pelabuhan")
                # ? pelabuhan option process and download file
                if list_bulan is not None:
                    for bulan_option in list_bulan:
                        await self.bulan_process(page, bulan_option)

                        # ? path to save files
                        path_files = f"{self.exim_text}/menurut_pelabuhan/{year}/{pelabuhan.lower().replace(" ", "_")}/"

                        # ? datas to data
                        self.pelabuhan_text = pelabuhan
                        self.bulan_text = bulan_option.split()[1]
                        await self.download_files(page, f"data/{path_files}/xlsx/", self.bulan_text)


                        try:
                            data = await self.return_datas()
                            setup_json = SaveJson(self.year_text, data, "", self.desc)
                            await setup_json.save_json_local(f"{self.bulan_text.lower()}.json", f"{path_files}/json/")
                        except:
                            #! ganti exception ini
                            print("Error saving json")


                        await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(7) > div > div > div > div.css-1wy0on6 > div:nth-child(1)').click() #? bulan X

                await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(5) > div > div > div > div.css-1wy0on6 > div:nth-child(1)').click() #? X

        except Exception as e:
            print(f"Error pelabuhan: {e}")
            raise FailedInputCategory("Failed to select pelabuhan")







    async def kode_hs_process(self, page, kode_hs, year):
        """process category kode hs"""

        self.year_text = year
        self.agregasi_text = kode_hs

        try:
            if "digit" in kode_hs:
                """process category kode hs"""

                self.jenis_hs = "HS 2 Digit"

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

                try:
                    list_digits = await get_digit_count(page)
                    for digit in list_digits:

                        await page.locator("div").filter(has_text=re.compile(r"^Ketikkan Kode HS$")).nth(1).click()
                        digit_locators = page.get_by_role("option", name=digit, exact=True)

                        await page.wait_for_function("document.querySelector('.css-qr46ko').innerText !== 'Loading...'")

                        print(await digit_locators.inner_text())
                        self.hs_digit_text = await digit_locators.inner_text()
                        await digit_locators.click()
                        await page.locator("body").press("Escape")
                        await asyncio.sleep(1)


                        _, pelabuhan_list, _ = await self.check_table(page, "hs_digit")
                        for pelabuhan_option in pelabuhan_list:
                            print(f"PELABUHAN = {pelabuhan_option}")
                            await self.__pelabuhan_pick(page, pelabuhan_option)

                            negara_list, _, _ = await self.check_table(page, "hs_digit")

                            for negara_option in negara_list:
                                print(f"NEGARA = {negara_option}")
                                await self.__negara_pick(page, negara_option)

                                _, _, bulan_list = await self.check_table(page, "hs_digit")
                                for bulan_option in bulan_list:
                                    print(f"BULAN = {bulan_option}")
                                    await self.bulan_process(page, bulan_option)


                                    # ? path to save files
                                    path_files = f"{self.exim_text}/menurut_kode_hs/hs_2_digit/{year}/{self.hs_digit_text.lower().replace(" ", "_")}/{pelabuhan_option.lower().replace(" ", "_")}/{negara_option.lower().replace(" ", "_")}/"

                                    # ? datas to data
                                    self.pelabuhan_text = pelabuhan_option
                                    self.negara_text = negara_option
                                    self.bulan_text = bulan_option.split()[1]
                                    print(self.bulan_text)

                                    await self.download_files(page, f"data/{path_files}/xlsx/", self.bulan_text)


                                    try:
                                        data = await self.return_datas()
                                        setup_json = SaveJson(self.year_text, data, "", self.desc)
                                        await setup_json.save_json_local(f"{self.bulan_text.lower()}.json", f"{path_files}/json/")
                                    except:
                                        #! ganti exception ini
                                        print("Error saving json")

                                    await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(7) > div > div > div > div.css-1wy0on6 > div:nth-child(1)').click() #? bulan X
                                await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(6) > div > div > div > div.css-1wy0on6 > div:nth-child(1)').click()# ? X negara
                            await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(5) > div > div > div > div.css-1wy0on6 > div:nth-child(1)').click() #? X pelabuhan



                        await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(4) > div.w-full.mt-2 > div > div > div.css-1wy0on6 > div:nth-child(1)').click() #? X
                except Exception as e:
                    print(f"Error digit: {e}")
                    raise FailedInputCategory("Failed to select digit")




            elif "full" in kode_hs:
                """process category kode full"""

                self.jenis_hs = "HS Full"

                try:
                    pass
                    index = 0
                    while True:

                        await page.locator("div").filter(has_text=re.compile(r"^Ketikkan Kode HS$")).nth(1).click()
                        await asyncio.sleep(2)
                        # full_locator = page.locator(f"#react-select-10-option-{index}")
                        full_locator = page.locator(f"//html/body/div[2]/div[2]/div[2]/div[1]/div/div[2]/div[4]/div[2]/div/div[2]/div/div[{index+1}]")

                        if index != 0 and index % 10 == 0:
                            try:
                                click_option_scroll = page.locator(f"#react-select-10-option-{index-1}")
                                await click_option_scroll.scroll_into_view_if_needed(timeout=60000)
                                await click_option_scroll.wait_for(state='visible', timeout=60000)
                            except TimeoutError as t:
                                print(f"Error loading options: {t}")
                                raise FailedInputCategory("Failed to scroll and load options")

                        await page.wait_for_function("document.querySelector('.css-qr46ko').innerText !== 'Loading...'")

                        print(await full_locator.inner_text())
                        self.hs_full_text = await full_locator.inner_text()
                        await full_locator.click()

                        await page.locator("body").press("Escape")
                        await asyncio.sleep(1)


                        _, pelabuhan_list, _ = await self.check_table(page, "hs_full")
                        if pelabuhan_list is not None:
                            for pelabuhan_option in pelabuhan_list:
                                print(f"PELABUHAN = {pelabuhan_option}")
                                await self.__pelabuhan_pick(page, pelabuhan_option)

                                negara_list, _, _ = await self.check_table(page, "hs_digit")
                                if negara_list is not None:
                                    for negara_option in negara_list:
                                        print(f"NEGARA = {negara_option}")
                                        await self.__negara_pick(page, negara_option)

                                        _, _, bulan_list = await self.check_table(page, "hs_digit")
                                        for bulan_option in bulan_list:
                                            print(f"BULAN = {bulan_option}")
                                            await self.bulan_process(page, bulan_option)


                                            # ? path to save files
                                            path_files = f"{self.exim_text}/menurut_kode_hs/hs_full/{year}/{self.hs_full_text.split("[")[1].split("]")[0]}/{pelabuhan_option.lower().replace(" ", "_")}/{negara_option.lower().replace(" ", "_")}/"

                                            # ? datas to data
                                            self.pelabuhan_text = pelabuhan_option
                                            self.negara_text = negara_option
                                            self.bulan_text = bulan_option.split()[1]
                                            print(self.bulan_text)

                                            await self.download_files(page, f"data/{path_files}/xlsx/", self.bulan_text)


                                            try:
                                                data = await self.return_datas()
                                                setup_json = SaveJson(self.year_text, data, "", self.desc)
                                                await setup_json.save_json_local(f"{self.bulan_text.lower()}.json", f"{path_files}/json/")
                                            except:
                                                #! ganti exception ini
                                                print("Error saving json")

                                            await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(7) > div > div > div > div.css-1wy0on6 > div:nth-child(1)').click() #? bulan X
                                        await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(6) > div > div > div > div.css-1wy0on6 > div:nth-child(1)').click()# ? X negara
                                        
                                    await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(5) > div > div > div > div.css-1wy0on6 > div:nth-child(1)').click() #? X pelabuhan

                        await page.locator('//*[@id="ss"]/div[2]/div[4]/div[2]/div/div/div[2]/div[1]').click() #? X

                        index += 1


                except Exception as e:
                    print(f"Error kode_hs_full: {e}")
                    raise FailedInputCategory("Failed to select kode_hs_full")


        except Exception as e:
            print(f"Error kode_hs: {e}")
            raise FailedInputCategory(f"Failed to select {kode_hs}")








    async def check_table(self, page, agregasi):
        """Get list of option negara, pelabuhan, and bulan who has table data"""
        await page.get_by_role("button", name="Buat Tabel").click()

        await asyncio.sleep(5)

        try:
            html_content = await page.content()
            soup = BeautifulSoup(html_content, "html.parser")

            #? negara
            table_data = soup.find('table', class_='pvtTable')

            if table_data:
                await page.wait_for_selector("#ss > div:nth-child(3) > div > div.overflow-x-scroll > table")
                
                if "hs" in agregasi:
                    list_negara = list(set(negara.get_text(strip=True) for negara in table_data.select('thead:nth-child(1) > tr:nth-child(1) > th.pvtColLabel')))
                    print(list_negara)

                    list_pelabuhan = list(set(pelabuhan.get_text(strip=True) for pelabuhan in table_data.select('thead:nth-child(1) > tr:nth-child(2) > th.pvtColLabel')))
                    print(list_pelabuhan)

                    list_bulan = list(set(bulan.get_text(strip=True) for bulan in table_data.select('thead:nth-child(1) > tr:nth-child(3) > th.pvtColLabel')))
                    print(list_bulan)

                    return list_negara, list_pelabuhan, list_bulan
                
                elif "negara" or "pelabuhan" in agregasi:
                    list_bulan = list(set(bulan.get_text(strip=True) for bulan in table_data.select('thead:nth-child(1) > tr:nth-child(2) > th.pvtColLabel')))
                    print(list_bulan)

                    return list_bulan
                else:
                    print(f"option {agregasi} salah")
            else:
                print("Tabel dengan class 'pvtTable' tidak ditemukan.")
                if "hs" in agregasi:
                    return None, None, None
                else:
                    return None
            

        except Exception as e:
            raise e
        




    async def bulan_process(self, page, bulan):
        bulan_option = bulan.split()[1].strip()
        if bulan_option:

            print(f"in bulan_process {bulan_option}")
            try:
                await page.locator("div").filter(has_text=re.compile(r"^Pilih Bulan$")).nth(1).click()
                bulan_locator = page.get_by_role("option", name=bulan_option, exact=True)
                await bulan_locator.click()

                await page.locator("body").press("Escape")
                await page.get_by_role("button", name="Buat Tabel").click()
                await asyncio.sleep(2)

            except Exception as e:
                print(f"Error download_file: {e}")
                raise FailedInputCategory("Failed to select bulan")




    async def download_files(self, page, download_path, bulan):
        """Download xlx files"""
        os.makedirs(download_path, exist_ok=True)

        try:

            dropdown_list_name = ['Nilai / Net Value (US $)', 'Berat / Net Weight (KG)']
            for dropdown_name in dropdown_list_name:
                await page.locator("#ss > div:nth-child(3) > div > div.overflow-x-scroll > table > tbody > tr:nth-child(2) > td.pvtVals > div > div.pvtDropdownValue").click()
                await asyncio.sleep(1)
                await page.get_by_role("button", name=dropdown_name, exact=True).click()
                await asyncio.sleep(1)
                await page.get_by_role("button", name="Buat Tabel", exact=True).click()
                await asyncio.sleep(1)


                await page.locator("#ss").get_by_role("button", name="Unduh").wait_for(state="visible", timeout=600000)
                async with page.expect_download() as download_info:
                    await page.locator("#ss").get_by_role("button", name="Unduh").click()
                downloads = await download_info.value


                if "KG" in dropdown_name: filename = f"{bulan}_(kg).xlsx"
                elif "US" in dropdown_name: filename = f"{bulan}_(us$).xlsx"
                file_path = os.path.join(download_path, filename)
                await downloads.save_as(file_path)


        except TimeoutError:
            print("Button timeout reached")
            pass
        except Exception as e:
            print(e)
            raise CantDownloadFiles



    async def find_elements(page):
        skeleton_element = await page.query_selector('div.skeleton-box')

        if skeleton_element:
            print("skeleton div ditemukan")
        else:
            print("skeleton not found")
        
        # Mencari elemen lain
        element1 = await page.query_selector('div.mt-4.w-full.p-4.rounded-lg.bg-white')
        element2 = await page.query_selector('div.mt-4.w-full.h-96')

        if element1 or element2:
            print("salah satu elemen lainnya ditemukan")
        else:
            print("tidak ada elemen lain yang ditemukan")



