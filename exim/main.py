from src.controller.main_controller import Controller
from src.controller.main import Controller

import asyncio
import argparse

async def main(**kwargs):
    con = Controller('https://bps.go.id/id/exim', 's3://ai-pipeline-raw-data/data/data_statistics/bps/data_ekspor_impor_nasional', **kwargs)
    # await con.main_controller()
    await con.mainc()

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Script untuk menjalankan Controller dengan argumen.")
    parser.add_argument('--data', type=str, help="Set data yang ingin diproses [impor, ekspor]")
    parser.add_argument('--headless',  action='store_true', help="Running Chromium dengan mode headless")
    parser.add_argument('--jenishs', type=str, default=["HS 2 Digit", "HS Full"],  help="set jenis hs yang ingin diambil [digit, full]")
    parser.add_argument('--indexhs', type=int, default=1, help="Set index kode HS")
    parser.add_argument('--miniwin', action='store_true', help="Set chromium dalam mode windows kecil")
    parser.add_argument('--s3', action='store_true', dest='uploads3', help="mengupload data ke S3")
    parser.add_argument('--agr', type=str, help="Pilih tipe agregasi yang ingin di ambil: [pelabuhan, negara, kodehs]")
    
    args = parser.parse_args()
    kwargs = vars(args)


    asyncio.run(main(**kwargs))