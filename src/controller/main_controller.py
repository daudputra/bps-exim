from src.helper.save_json import SaveJson
from src.helper.uploadS3 import upload_to_s3
from src.helper.logging import log_message

from playwright.async_api import async_playwright

import asyncio
import os
import traceback


class Controller():
    def __init__(self, url_page, path_s3, headless=True, miniwin=False, uploads3=True, **kwargs) -> None:
        self.path_s3 = path_s3
        self.url_page = url_page
        self.headless = headless
        self.miniwin = miniwin
        self.uploads3 = uploads3
        self.type_data = kwargs.get('data', None)
        self.cusindex_hs = kwargs.get('indexhs', 1)
        self.cusagregasi = kwargs.get('agr', None)

        # ? item text
        self.type_data_text = None
        self.agregasi_text = None
        self.jenis_hs_text = None
        self.tahun_text = None
        self.kode_hs_text = None
        self.pelabuhan_text = None
        self.negara_text = None
        self.bulan_text = None
        self.title_page = None
        self.deskirpsi = None



    async def main_controller(self):
        page = await self._start_playwright()



    async def _start_playwright(self):
        """mulai chromium dan masuk ke url_page | mulai proses"""

        async with async_playwright() as pw:
            viewports = {'width': 500, 'height': 500} if self.miniwin and not self.headless else None
            
            try:
                #? launch chromium
                browser = await pw.chromium.launch(headless=self.headless)
                context = await browser.new_context(viewport=viewports) 
                page = await context.new_page()
                await page.goto(self.url_page, timeout=1800000)
                # await page.wait_for_load_state("networkidle")
                await asyncio.sleep(5)

                #? tutup banner
                await self._close_bannerpage(page)

                await asyncio.sleep(5)

                #? donwload data export import nasional
                await self.get_data_exim_nasional(page, '//html/body/div[2]/div[2]/div[2]/div[2]/div/div[1]/div/div[1]/h4', '//html/body/div[2]/div[2]/div[2]/div[2]/div/div[1]/div/div[1]/button', 'Data Ekspor Impor Nasional Bulanan') #Bulanan 
                await self.get_data_exim_nasional(page, '//html/body/div[2]/div[2]/div[2]/div[2]/div/div[2]/div/div/div/div[1]/h4', '//html/body/div[2]/div[2]/div[2]/div[2]/div/div[2]/div/div/div/div[1]/button', 'Data Ekspor Impor Nasional HS 2 Digit') #HS 2 digit

                # #? json item
                self.title_page = await page.locator(r'body > div.mx-4.md\:mx-8.lg\:mx-16.xl\:mx-32.py-8 > div.w-full > div.flex.flex-col.flex-nowrap.justify-start.gap-x-8.gap-y-2.rounded-xl > div > h1').inner_text()
                self.sub_title = await page.locator('//html/body/div[2]/div[2]/div[1]/p').inner_text()
                self.deskirpsi = await page.locator('#ss > div.w-full.flex-col.justify-start.items-start.flex > div > div').inner_text()

                # ? pilih type data
                if self.type_data == "impor":
                    pilih_data = ['impor']
                elif self.type_data == "ekspor":
                    pilih_data = ['ekspor']
                elif self.type_data == None:
                    pilih_data = ['ekspor', 'impor']

                for type_data in pilih_data:
                    await asyncio.sleep(5)
                    await self._exim(page, type_data)

                    self.type_data_text = type_data
                    await log_message('DEBUG', 'logs/debug.log', f'{self.type_data_text}')




                    mappings = {
                        "pelabuhan": ("Menurut Pelabuhan", self.menurut_pelabuhan),
                        "kodehs": ("Menurut Kode HS", self.menurut_kodehs),
                        "negara": ("Menurut Negara", self.menurut_negara)
                    }
                    
                    if self.cusagregasi in mappings:
                        cusagregasi, method = mappings[self.cusagregasi]
                        self.agregasi_text = cusagregasi
                        await self._agregasi(page, cusagregasi)
                        print(self.cusagregasi)
                        await method(page)
                    

                    else:
                        # ? pilih agregasi
                        all_agregasi = ["Menurut Kode HS", "Menurut Pelabuhan", "Menurut Negara"]
                        for agregasi in all_agregasi:

                            await self._agregasi(page, agregasi)

                            self.agregasi_text = agregasi
                            await log_message('DEBUG', 'logs/debug.log', f'{self.agregasi_text}')

                            if agregasi == "Menurut Kode HS":
                                await self.menurut_kodehs(page)
                            elif agregasi == "Menurut Pelabuhan":
                                await self.menurut_pelabuhan(page)
                            elif agregasi == "Menurut Negara":
                                await self.menurut_negara(page)


            except TimeoutError:
                await log_message('ERROR', 'logs/error.log', 'Timeout load page')
            except Exception as e:
                await log_message('ERROR', 'logs/error.log', f'Error: {e}')
            finally:
                if browser:
                    await browser.close()





    async def _exim(self, page, placeholder:str):
        """klik type impor atau ekspor"""
        if placeholder == 'ekspor':
            placeholder = 'e'
        elif placeholder == 'impor':
            placeholder = 'i'
        await page.get_by_placeholder(placeholder).click()

    async def _agregasi(self, page, agregasi):
        await page.locator(".css-19bb58m").first.click()
        await page.get_by_role("option", name=agregasi).click()
        await asyncio.sleep(1)

    async def _jenis_hs(self, page, hs):
        await page.locator("#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(2) > div:nth-child(3) > div > div.css-hlgwow > div.css-19bb58m").click()
        await page.get_by_role("option", name=hs).click()
        await asyncio.sleep(1)




    async def _tahun(self, page, index_tahun):
        try:
            if index_tahun != 0 :
                await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(3) > div > div > div > div.css-1wy0on6 > div:nth-child(1)').click() #? X    

            await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(3) > div > div > div > div.css-hlgwow > div.css-19bb58m').click() #? input tahun

            # if index_tahun == 1:
            #     return False

            try:
                tahun_locator = page.locator(f'#react-select-5-option-{index_tahun}')
                await tahun_locator.wait_for(timeout=3000)
                if await tahun_locator.is_visible():
                    tahun_text = await tahun_locator.inner_text()
                else:
                    tahun_text = None

                self.tahun_text = tahun_text

                await log_message('DEBUG', 'logs/debug.log', self.tahun_text)
            except TimeoutError: await log_message('ERROR', 'logs/error.log', f'Timeout pada select {tahun_text}:')



            if await tahun_locator.evaluate('element => !!element') is None:
                return False
            await tahun_locator.click()
            await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(3) > div > div > div > div.css-1dyz3mf > div.css-19bb58m').click()  # ? input tahun close
            await asyncio.sleep(1)
            return True

        except Exception as e:
            await log_message('ERROR', 'logs/error.log', f'Error _tahun: {e}')
            return False




    async def _kode_hs(self, page, index_kode_hs, jenis_hs):
        try:
            if index_kode_hs != self.cusindex_hs:
                await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(4) > div.w-full.mt-2 > div > div > div.css-1wy0on6 > div:nth-child(1)').click()
            await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(4) > div.w-full.mt-2 > div > div > div.css-hlgwow > div.css-19bb58m, #ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(4) > div.w-full.mt-2 > div > div > div.css-1dyz3mf > div.css-19bb58m' ).click()
            # await asyncio.sleep(2)
            if index_kode_hs == 1:
                await asyncio.sleep(2)

            # if index_kode_hs == 3: return False

            try:
                kode_hs_locator = page.locator(f'//html/body/div[2]/div[2]/div[2]/div[1]/div/div[2]/div[4]/div[2]/div/div[2]/div/div[{index_kode_hs}]')
                await kode_hs_locator.wait_for(timeout=10000)
                if await kode_hs_locator.is_visible():
                    kode_hs_text = await kode_hs_locator.inner_text()
                    if jenis_hs == "HS Full":
                        kode_hs_text = kode_hs_text.replace('HS2022 - ','').replace(',','').replace('.','').replace('≤','').replace('≥','').replace('<','').replace('>','')
                else: kode_hs_text = None

                self.kode_hs_text = kode_hs_text
                await log_message('DEBUG', 'logs/debug.log', self.kode_hs_text)
            except TimeoutError: await log_message('ERROR', 'logs/error.log', f'Error pada select {kode_hs_text}')

            if kode_hs_text == None:
                await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(4) > div.w-full.mt-2 > div > div > div.css-hlgwow > div.css-19bb58m, #ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(4) > div.w-full.mt-2 > div > div > div.css-1dyz3mf > div.css-19bb58m' ).click()

            count = await page.locator('//html/body/div[2]/div[2]/div[2]/div[1]/div/div[2]/div[4]/div[2]/div/div[2]/div/div').count()
            if count != 0:
                last_index = count - 1
                locators = page.locator(f'//html/body/div[2]/div[2]/div[2]/div[1]/div/div[2]/div[4]/div[2]/div/div[2]/div/div[{last_index}]')
                await locators.scroll_into_view_if_needed()
                await locators.wait_for(state='visible')
                await asyncio.sleep(1)
            
            is_element_exists = await kode_hs_locator.evaluate('element => !!element')
            if not is_element_exists:
                return False

            await kode_hs_locator.click()
            await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(4) > div.w-full.mt-2 > div > div > div.css-1dyz3mf > div.css-19bb58m, #ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(4) > div.w-full.mt-2 > div > div > div.css-hlgwow > div.css-19bb58m').click()
            await asyncio.sleep(1)            
            return True

        except Exception as e:
            await log_message('ERROR', 'logs/error.log', f'Error _kode_hs: {e}')
            return False




    async def _pelabuhan(self, page, index_pelabuhan):
        try:
            if index_pelabuhan != 0 :
                await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(5) > div > div > div > div.css-1wy0on6 > div:nth-child(1)').click() #? X
            await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(5) > div > div > div > div.css-hlgwow > div.css-19bb58m').click() #? input pelabuhan
            
            # if index_pelabuhan == 3:
            #     return False

            try:
                pelabuhan_locator =  page.locator(f'#react-select-6-option-{index_pelabuhan}')
                await pelabuhan_locator.wait_for(timeout=3000)
                if await pelabuhan_locator.is_visible():
                    pelabuhan_text = await pelabuhan_locator.inner_text()
                else: pelabuhan_text = None

                self.pelabuhan_text = pelabuhan_text
                await log_message('DEBUG', 'logs/debug.log', self.pelabuhan_text)
            except TimeoutError: await log_message('ERROR', 'logs/error.log', f'error pada select {pelabuhan_text}')

            await asyncio.sleep(1)
            if await pelabuhan_locator.evaluate('element => !!element') is None:
                return False
            await pelabuhan_locator.click()
            await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(5) > div > div > div.css-t3ipsp-control > div.css-1dyz3mf > div.css-19bb58m').click()  # ? input pelabuhan close
            await asyncio.sleep(1)
            return True
        
        except Exception as e:
            await log_message('ERROR', 'logs/error.log', f'Error _pelabuhan: {e}')
            return False




    async def _negara(self, page, index_negara):
        try:
            if index_negara != 0:
                await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(6) > div > div > div > div.css-1wy0on6 > div:nth-child(1)').click()# ? X
            await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(6) > div > div > div > div.css-hlgwow > div.css-19bb58m').click() #? input negara

            if index_negara == 1:
                await asyncio.sleep(2)

            # if index_negara == 3: return False

            try:
                negara_locator =  page.locator(f'#react-select-7-option-{index_negara}')
                await negara_locator.wait_for(timeout=3000)
                if await negara_locator.is_visible():
                    negara_text = await negara_locator.inner_text()
                else: negara_text = None

                self.negara_text = negara_text
                await log_message('DEBUG', 'logs/debug.log', self.negara_text)
            except TimeoutError: await log_message('ERROR', 'logs/error.log', f'error pada select {negara_text}')

            await asyncio.sleep(1)
            if await negara_locator.evaluate('element => !!element') is None:
                return False    
            await negara_locator.click()
            await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(6) > div > div > div > div.css-1dyz3mf > div.css-19bb58m').click() # ? input neagara close
            await asyncio.sleep(1)
            
            return True
        
        except Exception as e:
            await log_message('ERROR', 'logs/error.log', f'Error _negara: {e}')
            return False




    async def _bulan(self, page, index_bulan):
        try:
            if index_bulan != 0:
                await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(7) > div > div > div > div.css-1wy0on6 > div:nth-child(1)').click() #? X
            await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(7) > div > div > div > div.css-hlgwow > div.css-19bb58m').click() #? input bulan
            
            if index_bulan < 12:
                try:
                    bulan_locator = page.locator(f'#react-select-3-option-{index_bulan}')
                    await bulan_locator.wait_for(timeout=3000)
                    if await bulan_locator.is_visible():
                        bulan_text = await bulan_locator.inner_text()
                    else: bulan_text = None

                    self.bulan_text = bulan_text
                except TimeoutError: await log_message('ERROR', 'logs/error.log', f'error pada select {bulan_text}')
                    

                if await bulan_locator.evaluate('element => !!element') is None:
                    return False    
                await bulan_locator.click()
                await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div:nth-child(7) > div > div > div.css-t3ipsp-control > div.css-1dyz3mf > div.css-19bb58m').click() # ? input bulan close
                await asyncio.sleep(1)
                return True
            
            else: return False
            
        except Exception as e:
            await log_message('ERROR', 'logs/error.log', f'Error _negara: {e}')
            return False




    async def menurut_kodehs(self, page):
        try:
            all_hs = ["HS 2 Digit", "HS Full"]
            for jenis_hs in all_hs:
                self.jenis_hs_text = jenis_hs
                await self._jenis_hs(page, jenis_hs)
                
                # ==tahun==
                index_tahun = 0
                while True:
                    tahun = await self._tahun(page, index_tahun)
                    if not tahun:
                        break
                    index_tahun += 1

                    # ==kode hs===
                    index_kode_hs = self.cusindex_hs
                    while True:
                        kode_hs = await self._kode_hs(page, index_kode_hs, jenis_hs)
                        if not kode_hs:
                            break
                        index_kode_hs += 1

                        check_data_kode_hs =  await self.check_data_table(page)
                        if check_data_kode_hs == True:

                        # ==pelabuhan==
                            pelabuhan_index = 0
                            while True:
                                pelabuhan = await self._pelabuhan(page, pelabuhan_index)
                                if not pelabuhan:
                                    break
                                pelabuhan_index += 1

                                check_data_pelabuhan =  await self.check_data_table(page)
                                if check_data_pelabuhan == True:

                                    # ==negara==
                                    index_negara = 0
                                    while True:
                                        negara = await self._negara(page, index_negara)
                                        if not negara:
                                            break
                                        index_negara += 1
                                        await log_message('DEBUG', 'logs/debug.log', f"{self.type_data_text} - {self.agregasi_text} - {self.tahun_text} - {self.jenis_hs_text} - {self.kode_hs_text} - {self.pelabuhan_text} - {self.negara_text}")

                                        check_data_bulan =  await self.check_data_table(page)
                                        if check_data_bulan == True:

                                            # ==bulan==
                                            index_bulan = 0
                                            while True:
                                                bulan = await self._bulan(page, index_bulan)
                                                if not bulan:
                                                    break
                                                index_bulan += 1
                                                
                                                # await log_message('DEBUG', 'logs/debug.log', f"{self.type_data_text} - {self.agregasi_text} - {self.tahun_text} - {self.jenis_hs_text} - {self.kode_hs_text} - {self.pelabuhan_text} - {self.negara_text} - {self.bulan_text}")
                                                check_table = await self.get_table(page)
                                                if check_table == True:

                                                    #==path==
                                                    type_data_json = self.type_data_text.replace(' ','_').replace('\\','_').lower()
                                                    agregasi_json = self.agregasi_text.replace(' ','_').replace('\\','_').lower()
                                                    pelabuhan_json = self.pelabuhan_text.replace(' ','_').replace('\\','_').lower()
                                                    jenis_hs_json = self.jenis_hs_text.replace(' ','_').replace('\\','_').lower()
                                                    negara_json = self.negara_text.replace(' ','_').replace('\\','_').lower()
                                                    kode_hs_json = self.kode_hs_text.replace(' ','_').replace('\\','_').lower()

                                                    filename = self.bulan_text

                                                    # ? list filename xslx
                                                    xlsx_list = [
                                                        f'{filename}_(us$).xlsx',
                                                        f'{filename}_(kg).xlsx'
                                                    ]

                                                    path_data_raw = [
                                                        f's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{type_data_json}/{agregasi_json}/{jenis_hs_json}/{self.tahun_text}/{kode_hs_json}/{pelabuhan_json}/{negara_json}/json/{filename.lower()}.json',
                                                        f's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{type_data_json}/{agregasi_json}/{jenis_hs_json}/{self.tahun_text}/{kode_hs_json}/{pelabuhan_json}/{negara_json}/xlsx/{filename}_(kg).xlsx',
                                                        f's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{type_data_json}/{agregasi_json}/{jenis_hs_json}/{self.tahun_text}/{kode_hs_json}/{pelabuhan_json}/{negara_json}/xlsx/{filename}_(us$).xlsx'
                                                    ]

                                                    data = {
                                                        'tipe_data' : self.type_data_text,
                                                        'agregasi' : self.agregasi_text,
                                                        'jenis_hs' : self.jenis_hs_text,
                                                        'tahun' : self.tahun_text,
                                                        'kode_hs' : self.kode_hs_text,
                                                        'pelabuhan' : self.pelabuhan_text,
                                                        'negara' : self.negara_text,
                                                        'bulan' : self.bulan_text,
                                                        'filename_xlsx' : xlsx_list,
                                                    }


                                                    try:
                                                        dir_xlsx = os.path.join('data', type_data_json, agregasi_json, jenis_hs_json, self.tahun_text, kode_hs_json, pelabuhan_json, negara_json, 'xlsx')
                                                        await self._get_files(page, dir_xlsx, filename)
                                                    except Exception as e:
                                                        await log_message('ERROR', 'logs/error.log', f'error get xlsx in menurut_kodehs == {e}')



                                                    try:
                                                        save_json = SaveJson(self.url_page, self.title_page, self.tahun_text, self.deskirpsi, '', '', data, path_data_raw, self.sub_title)
                                                        await save_json.save_json_local(f'{filename.lower()}.json', type_data_json, agregasi_json, jenis_hs_json, self.tahun_text, kode_hs_json, pelabuhan_json, negara_json, 'json' )
                                                    except Exception as e:
                                                        await log_message('ERROR', 'logs/error.log', f'error save {filename}.json' == {e})

                                                    local_paths = [
                                                        f"data/{type_data_json}/{agregasi_json}/{jenis_hs_json}/{self.tahun_text}/{kode_hs_json}/{pelabuhan_json}/{negara_json}/json/{filename.lower()}.json",
                                                        f"data/{type_data_json}/{agregasi_json}/{jenis_hs_json}/{self.tahun_text}/{kode_hs_json}/{pelabuhan_json}/{negara_json}/xlsx/{filename}_(kg).xlsx",
                                                        f"data/{type_data_json}/{agregasi_json}/{jenis_hs_json}/{self.tahun_text}/{kode_hs_json}/{pelabuhan_json}/{negara_json}/xlsx/{filename}_(us$).xlsx"
                                                    ]


                                                    if self.uploads3:
                                                        for local_path, s3_path in zip(local_paths, path_data_raw):
                                                            try:
                                                                print(f"Uploading to {s3_path}")
                                                                await upload_to_s3(local_path, s3_path)
                                                                await log_message('INFO', self._logs_folder_exim(), f's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{type_data_json}/{agregasi_json}/{jenis_hs_json}/{self.tahun_text}/{kode_hs_json}/{pelabuhan_json}/{negara_json}/json/{filename.lower()}.json')
                                                                await log_message('INFO', self._logs_folder_exim(), f's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{type_data_json}/{agregasi_json}/{jenis_hs_json}/{self.tahun_text}/{kode_hs_json}/{pelabuhan_json}/{negara_json}/json/{filename}_(kg).xlsx')
                                                                await log_message('INFO', self._logs_folder_exim(), f's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{type_data_json}/{agregasi_json}/{jenis_hs_json}/{self.tahun_text}/{kode_hs_json}/{pelabuhan_json}/{negara_json}/json/{filename}_(us$).xlsx')
                                                            except Exception as e:
                                                                print(f"Failed to upload {local_path} to {s3_path}: {e}")
                                                                log_message('ERROR', 'logs/error.log', f'error upload s3 menurut negara: {e}')

        except Exception as e:
            await log_message('ERROR', 'logs/error.log', f'error menurut_kodehs == {e}')





    async def menurut_negara(self, page):
        try:
            # ==tahun==
            index_tahun = 0
            while True:
                tahun = await self._tahun(page, index_tahun)
                if not tahun:
                    break

                index_tahun += 1

                # ==negara==
                index_negara = 0
                while True:
                    negara = await self._negara(page, index_negara)
                    if not negara:
                        break

                    index_negara += 1
                    await log_message('DEBUG', 'logs/debug.log', f"{self.type_data_text} - {self.agregasi_text} - {self.tahun_text} - {self.negara_text}")

                    check_data_negara =  await self.check_data_table(page)
                    if check_data_negara == True:

                        # ==bulan==
                        index_bulan = 0
                        while True:
                            bulan = await self._bulan(page, index_bulan)
                            if not bulan:
                                break
                            index_bulan += 1

                            check_data_bulan =  await self.check_data_table(page)
                            if check_data_bulan == True:

                                # await log_message('DEBUG', 'logs/debug.log', f"{self.type_data_text} - {self.agregasi_text} - {self.tahun_text} - {self.pelabuhan_text} - {self.bulan_text}")
                                check_table = await self.get_table(page)
                                if check_table == True:

                                    #===path===
                                    type_data_json = self.type_data_text.replace(' ','_').replace('\\','_').lower()
                                    agregasi_json = self.agregasi_text.replace(' ','_').replace('\\','_').lower()
                                    negara_json = self.negara_text.replace(' ','_').replace('\\','_').lower()

                                    
                                    filename = self.bulan_text

                                    # ? list filename xslx
                                    xlsx_list = [
                                        f'{filename}_(us$).xlsx',
                                        f'{filename}_(kg).xlsx'
                                    ]

                                    path_data_raw = [
                                        f's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{type_data_json}/{agregasi_json}/{self.tahun_text}/{negara_json}/json/{filename.lower()}.json',
                                        f's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{type_data_json}/{agregasi_json}/{self.tahun_text}/{negara_json}/xlsx/{filename}_(kg).xlsx',
                                        f's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{type_data_json}/{agregasi_json}/{self.tahun_text}/{negara_json}/xlsx/{filename}_(us$).xlsx'
                                    ]

                                    data = {
                                        'tipe_data' : self.type_data_text,
                                        'agregasi' : self.agregasi_text,
                                        'tahun' : self.tahun_text,
                                        'negara' : self.negara_text,
                                        'bulan' : self.bulan_text,
                                        'filename_xlsx' : xlsx_list,
                                    }

                                    try:
                                        dir_xlsx = os.path.join('data', type_data_json, agregasi_json, self.tahun_text, negara_json, 'xlsx')
                                        await self._get_files(page, dir_xlsx, filename)
                                    except Exception as e:
                                        await log_message('ERROR', 'logs/error.log', f'error get xlsx in menurut_negara == {e}')

                                    try:
                                        save_json = SaveJson(self.url_page, self.title_page, self.tahun_text, self.deskirpsi, '', '', data, path_data_raw, self.sub_title)
                                        await save_json.save_json_local(f'{filename.lower()}.json', type_data_json, agregasi_json, self.tahun_text, negara_json,  'json' )
                                    except Exception as e:
                                        await log_message('ERROR', 'logs/error.log', f'error save {filename}.json' == {e})


                                    local_paths = [
                                        f"data/{type_data_json}/{agregasi_json}/{self.tahun_text}/{negara_json}/json/{filename.lower()}.json",
                                        f"data/{type_data_json}/{agregasi_json}/{self.tahun_text}/{negara_json}/xlsx/{filename}_(kg).xlsx",
                                        f"data/{type_data_json}/{agregasi_json}/{self.tahun_text}/{negara_json}/xlsx/{filename}_(us$).xlsx"
                                    ]


                                    if self.uploads3:
                                        for local_path, s3_path in zip(local_paths, path_data_raw):
                                            try:
                                                print(f"Uploading to {s3_path}")
                                                await upload_to_s3(local_path, s3_path)
                                                await log_message('INFO', self._logs_folder_exim(), f's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{type_data_json}/{agregasi_json}/{self.tahun_text}/{negara_json}/json/{filename.lower()}.json' )
                                                await log_message('INFO', self._logs_folder_exim(), f's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{type_data_json}/{agregasi_json}/{self.tahun_text}/{negara_json}/json/{filename}_(kg).xlsx' )
                                                await log_message('INFO', self._logs_folder_exim(), f's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{type_data_json}/{agregasi_json}/{self.tahun_text}/{negara_json}/json/{filename}_(us$).xlsx' )
                                            except Exception as e:
                                                print(f"Failed to upload {local_path} to {s3_path}: {e}")
                                                log_message('ERROR', 'logs/error.log', f'error upload s3 menurut negara: {e}')
        except Exception as e:
            await log_message('ERROR', 'logs/error.log', f'error menurut_negara == {e}')




    async def menurut_pelabuhan(self, page):
        try:
            # ==tahun==
            index_tahun = 0
            while True:
                tahun = await self._tahun(page, index_tahun)
                if not tahun:
                    break

                index_tahun += 1

                # ==pelabuhan==
                pelabuhan_index = 0
                while True:
                    pelabuhan = await self._pelabuhan(page, pelabuhan_index)
                    if not pelabuhan:
                        break

                    pelabuhan_index += 1
                    await log_message('DEBUG', 'logs/debug.log', f"{self.type_data_text} - {self.agregasi_text} - {self.tahun_text} - {self.pelabuhan_text}")

                    check_data_pelabuhan =  await self.check_data_table(page)
                    if check_data_pelabuhan == True:

                        # ==bulan==
                        index_bulan = 0
                        while True:
                            bulan = await self._bulan(page, index_bulan)
                            if not bulan:
                                break
                            index_bulan += 1

                            check_data_bulan =  await self.check_data_table(page)
                            if check_data_bulan == True:

                                # await log_message('DEBUG', 'logs/debug.log', f"{self.type_data_text} - {self.agregasi_text} - {self.tahun_text} - {self.pelabuhan_text} - {self.bulan_text}")
                                check_table = await self.get_table(page)
                                if check_table == True:

                                    #===path===
                                    type_data_json = self.type_data_text.replace(' ','_').replace('\\','_').lower()
                                    agregasi_json = self.agregasi_text.replace(' ','_').replace('\\','_').lower()
                                    pelabuhan_json = self.pelabuhan_text.replace(' ','_').replace('\\','_').lower()

                                    
                                    filename = self.bulan_text

                                    # ? list filename xslx
                                    xlsx_list = [
                                        f'{filename}_(us$).xlsx',
                                        f'{filename}_(kg).xlsx'
                                    ]

                                    path_data_raw = [
                                        f's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{type_data_json}/{agregasi_json}/{self.tahun_text}/{pelabuhan_json}/json/{filename.lower()}.json',
                                        f's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{type_data_json}/{agregasi_json}/{self.tahun_text}/{pelabuhan_json}/xlsx/{filename}_(kg).xlsx',
                                        f's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{type_data_json}/{agregasi_json}/{self.tahun_text}/{pelabuhan_json}/xlsx/{filename}_(us$).xlsx'
                                    ]

                                    data = {
                                        'tipe_data' : self.type_data_text,
                                        'agregasi' : self.agregasi_text,
                                        'tahun' : self.tahun_text,
                                        'pelabuhan' : self.pelabuhan_text,
                                        'bulan' : self.bulan_text,
                                        'filename_xlsx' : xlsx_list,
                                    }


                                    try:
                                        dir_xlsx = os.path.join('data', type_data_json, agregasi_json, self.tahun_text, pelabuhan_json, 'xlsx')
                                        await self._get_files(page, dir_xlsx, filename)
                                    except Exception as e:
                                        await log_message('ERROR', 'logs/error.log', f'error get xlsx in menurut_pelabuhan == {e}')


                                    try:
                                        save_json = SaveJson(self.url_page, self.title_page, self.tahun_text, self.deskirpsi, '', '', data, path_data_raw, self.sub_title)
                                        await save_json.save_json_local(f'{filename.lower()}.json', type_data_json, agregasi_json, self.tahun_text, pelabuhan_json, 'json' )
                                        await log_message('INFO', self._logs_folder_exim() ,f's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{type_data_json}/{agregasi_json}/{self.tahun_text}/{pelabuhan_json}/json/{filename.lower()}.json' )
                                    except Exception as e:
                                        await log_message('ERROR', 'logs/error.log', f'error save {filename}.json' == {e})


                                    local_paths = [
                                        f"data/{type_data_json}/{agregasi_json}/{self.tahun_text}/{pelabuhan_json}/json/{filename.lower()}.json",
                                        f"data/{type_data_json}/{agregasi_json}/{self.tahun_text}/{pelabuhan_json}/xlsx/{filename}_(kg).xlsx",
                                        f"data/{type_data_json}/{agregasi_json}/{self.tahun_text}/{pelabuhan_json}/xlsx/{filename}_(us$).xlsx"
                                    ]
                                    
                                    if self.uploads3:
                                        for local_path, s3_path in zip(local_paths, path_data_raw):
                                            try:
                                                print(f"Uploading to {s3_path}")
                                                await upload_to_s3(local_path, s3_path)
                                                await log_message('INFO', self._logs_folder_exim() ,f's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{type_data_json}/{agregasi_json}/{self.tahun_text}/{pelabuhan_json}/json/{filename.lower()}.json')
                                                await log_message('INFO', self._logs_folder_exim() ,f's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{type_data_json}/{agregasi_json}/{self.tahun_text}/{pelabuhan_json}/json/{filename}_(kg).xlsx')
                                                await log_message('INFO', self._logs_folder_exim() ,f's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{type_data_json}/{agregasi_json}/{self.tahun_text}/{pelabuhan_json}/json/{filename}_(us$).xlsx')
                                            except Exception as e:
                                                print(f"Failed to upload {local_path} to {s3_path}: {e}")
                                                log_message('ERROR', 'logs/error.log', f'error upload s3 menurut pelabuhan: {e}')

        except Exception as e:
            await log_message('ERROR', 'logs/error.log', f'error menurut_pelabuhan == {e}')




    async def _close_bannerpage(self, page):
        """tutup popup banner pada saat masuk ke dalam page"""
        close_button = page.locator('//html/body/div[5]/div/div/div/div/div/div/div[2]/button')
        await close_button.wait_for(timeout=3000)
        if await close_button.count() > 0:
            await close_button.click()




    def _logs_folder_exim(self):
        if self.type_data_text == 'impor':
            path_exim = 'logs/impor/impor_info.log'
        elif self.type_data_text == 'ekspor':
            path_exim = 'logs/ekspor/ekspor_info.log'
        else:
            path_exim = 'logs/info.log'

        return path_exim




    async def get_table(self, page):
        try:
            await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div.w-full.py-4 > button').click()
            await asyncio.sleep(1)
            check_unduh_button = page.locator('#ss > div:nth-child(3) > div > div.w-full.flex.flex-row.mb-4 > button')
            if not await check_unduh_button.is_visible():
                return False
            else:
                return True
        except Exception as e:
            await log_message('ERROR', 'logs/error.log', f'error get_table == {e}')




    async def _get_files(self, page, download_path, base_filename):
        try:
            os.makedirs(download_path, exist_ok=True)

            name_dropdowns = ["Berat / Net Weight (KG)", "Nilai / Net Value (US $)"]
            
            await asyncio.sleep(2)
            for nama in name_dropdowns:
                await page.locator('//html/body/div[2]/div[2]/div[2]/div[1]/div/div[3]/div/div[2]/table/tbody/tr[2]/td[1]/div/div').click()
                # await page.get_by_role("button", name=nama, exact=True).click()
                button = page.locator(f'//*[@id="ss"]/div[3]/div/div[2]/table/tbody/tr[2]/td[1]/div/div[2]/div[contains(text(), "{nama}")]')
                await button.click()
                await button.click()
                
                await asyncio.sleep(1)
                async with page.expect_download() as download_info:
                    await page.locator("#ss").get_by_role("button", name="Unduh").click()
                    await asyncio.sleep(2)
                
                download = await download_info.value

                if nama == "Nilai / Net Value (US $)":
                    filename = f'{base_filename}_(us$).xlsx'
                elif nama == "Berat / Net Weight (KG)":
                    filename = f'{base_filename}_(kg).xlsx'

                file_path = os.path.join(download_path, filename)
                await download.save_as(file_path)
                await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div.w-full.py-4 > button').click()

        except Exception as e:
            log_message('ERROR', 'logs/error.log', f'error get xlsx files: {e}')




    async def check_data_table(self, page):
        try:
            await page.locator('#ss > div.mt-4.rounded-lg.bg-white.w-full.flex-col.justify-start.items-start.gap-4.inline-flex.p-4 > div.w-full.py-4 > button').click() #? buat_tabel_button
            await asyncio.sleep(1)
            teks_not_found = page.locator('//*[@id="ss"]/div[3]/div/div/div[2]/p[1]')
            try:
                if await teks_not_found.is_visible():
                    return False
                else:
                    return True
            except TimeoutError:
                await log_message('ERROR', 'logs/error.log', 'check data table unduh button tidak ditemukan')
                return False
        except Exception as e:
            await log_message('ERROR', 'logs/error.log', f'error check_data_table == {e}')





    async def get_data_exim_nasional(self, page, title_locator, button_unduh_selector, path_name):
        title_locator = page.locator(title_locator)
        title = await title_locator.inner_text()
        
        button_unduh_selector = page.locator(button_unduh_selector)

        try:
            async with page.expect_download() as download_info:
                await button_unduh_selector.click()
            download = await download_info.value

            #? item file json
            filename = title.replace(' ','_').lower()
            range_data = title.split(' ')[-1]
            path_name = path_name.lower().replace(' ','_')
            path_data_raw = [
                f'{self.path_s3}/{path_name}/json/{filename}.json',
                f'{self.path_s3}/{path_name}/xlsx/{filename}.xlsx'
            ]

            data = {
                'filename' : [f'{filename}.xlsx'] 
            }


            # == xlsx ==
            try:
                download_path_xlsx = f'data/{path_name}/xlsx'
                file_path = os.path.join(download_path_xlsx, f'{filename}.xlsx')
                await download.save_as(file_path)
            except Exception as e:
                await log_message('ERROR', 'logs/error.log', f'error get xlsx in get_data_maxim == {e}')


            # == json ==
            try:
                save_json = SaveJson(self.url_page, title, range_data, self.deskirpsi, '', '', data, path_data_raw)
                await save_json.save_json_local(f'{filename}.json', path_name, 'json' )
                await log_message('info', 'logs/info.log', f'{self.path_s3}/{path_name}/json/{filename}.json')
            except Exception as e:
                await log_message('ERROR', 'logs/error.log', f'error save {filename}.json == {e}')


            local_path_json = f'data/{path_name}/json/{filename}.json'
            local_path_xlsx = f'data/{path_name}/xlsx/{filename}.xlsx'

            #! upload s3    
            if self.uploads3:
                try:
                    await upload_to_s3(local_path_json, f'ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{path_name}/json/{filename}.json')
                    await upload_to_s3(local_path_xlsx, f'ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{path_name}/xlsx/{filename}.xlsx')
                except Exception as e:
                    log_message('ERROR', 'logs/error.log', f'errror upload s3 _get_data_exim_nasional == {e}')


        except Exception as e:
            await log_message('ERROR', 'logs/error.log', f'error get_data_exim_nasional: {e}')
