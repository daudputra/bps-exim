from src.controller.main_controller import Controller

import asyncio
import argparse

async def main(**kwargs):
    con = Controller('https://bps.go.id/id/exim', 's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional', **kwargs)
    await con.main_controller()

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Script untuk menjalankan Controller dengan argumen.")
    parser.add_argument('--data', type=str, help="Data yang ingin diproses: 'import' atau 'ekspor'. jika ingin mengambil keduanya dalam 1 proses tidak perlu menggunakan --data")
    parser.add_argument('--headless',  action='store_true', help="Running Chromium dengan mode headless")
    parser.add_argument('--indexhs', type=int, default=1, help="set index kode HS")
    parser.add_argument('--miniwin', action='store_true', help="set chromium dalam mode windows kecil")
    parser.add_argument('--nos3', action='store_false', dest='uploads3', help="Tidak mengupload data ke S3")
    parser.add_argument('--agr', type=str, help="pilih tipe agregasi yang ingin di ambil: [pelabuhan, negara, kodehs]")
    
    
    args = parser.parse_args()
    kwargs = vars(args)
    

    asyncio.run(main(**kwargs))


    
#     Traceback (most recent call last):
#   File "/app/main.py", line 1, in <module>
#     from src.controller.main_controller import Controller
#   File "/app/src/controller/main_controller.py", line 1, in <module>
#     from src.helper.save_json import SaveJson
#   File "/app/src/helper/save_json.py", line 3, in <module>
#     import aiofiles
# ModuleNotFoundError: No module named 'aiofiles'
