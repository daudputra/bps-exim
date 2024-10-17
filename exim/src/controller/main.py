from src.helper.save_json import SaveJson
from src.helper.uploadS3 import upload_to_s3
from src.helper.logging import log_message
from src.helper.func import Func


from playwright.async_api import async_playwright

import asyncio
import os
import traceback


class Controller:

    def __init__(self, url_page, path_s3, headless=True, miniwin=False, uploads3=False, **kwargs) -> None:
        self.path_s3 = path_s3
        self.url_page = url_page
        self.headless = headless
        self.miniwin = miniwin
        self.uploads3 = uploads3
        self.type_data = kwargs.get('data', None)
        self.cusindex_hs = kwargs.get('indexhs', 1)
        self.cusagregasi = kwargs.get('agr', None)
        self.cusjenishs = kwargs.get('jenishs', None)

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



    async def mainc(self):

        async with async_playwright() as pw:
            viewports = {'width': 500, 'height': 500} if self.miniwin and not self.headless else None
            
            try:
                #? launch chromium
                browser = await pw.chromium.launch(headless=self.headless)
                context = await browser.new_context(viewport=viewports) 
                page = await context.new_page()
                await page.goto(self.url_page, timeout=1800000)
                await asyncio.sleep(5)

                #? tutup banner
                await Func.close_bannerpage(page)

                await asyncio.sleep(5)

                #? donwload data export import nasional
                await self.get_data_exim_nasional(page, '//html/body/div[2]/div[2]/div[2]/div[2]/div/div[1]/div/div[1]/h4', '//html/body/div[2]/div[2]/div[2]/div[2]/div/div[1]/div/div[1]/button', 'Data Ekspor Impor Nasional Bulanan') #Bulanan 
                await self.get_data_exim_nasional(page, '//html/body/div[2]/div[2]/div[2]/div[2]/div/div[2]/div/div/div/div[1]/h4', '//html/body/div[2]/div[2]/div[2]/div[2]/div/div[2]/div/div/div/div[1]/button', 'Data Ekspor Impor Nasional HS 2 Digit') #HS 2 digit

                #? json item
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
                    await Func.click_exim(page, type_data)

                    self.type_data_text = type_data
                    print(f'Data : {self.type_data_text}')



            except Exception as e:
                print(e)
            except TimeoutError:
                print('Timeout')
            finally:
                if browser:
                    await browser.close()





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
                if self.uploads3 == True:
                    await log_message('info', 'logs/info.log', f'{self.path_s3}/{path_name}/json/{filename}.json')
            except Exception as e:
                await log_message('ERROR', 'logs/error.log', f'error save {filename}.json == {e}')


            local_path_json = f'data/{path_name}/json/{filename}.json'
            local_path_xlsx = f'data/{path_name}/xlsx/{filename}.xlsx'

            #! upload s3    
            if self.uploads3 == True :
                try:
                    await upload_to_s3(local_path_json, f'ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{path_name}/json/{filename}.json')
                    await upload_to_s3(local_path_xlsx, f'ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional/{path_name}/xlsx/{filename}.xlsx')
                except Exception as e:
                    await log_message('ERROR', 'logs/error.log', f'errror upload s3 _get_data_exim_nasional == {e}')


        except Exception as e:
            await log_message('ERROR', 'logs/error.log', f'error get_data_exim_nasional: {e}')