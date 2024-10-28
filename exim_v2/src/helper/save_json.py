import json
import os
import aiofiles
from pathlib import Path
from datetime import datetime

class SaveJson:

    def __init__(self, range_data, data, path_data_raw, desc):
        self.range_data = range_data
        self.data = data
        self.path_data_raw = path_data_raw
        self.desc = desc


    async def save_json_local(self, filename, folder_path):
        directory = Path(os.path.normpath(os.path.join("data", folder_path)))
        
        directory.mkdir(parents=True, exist_ok=True)
        
        file_path = directory / filename
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as json_file:
            data = self.mapping()
            await json_file.write(json.dumps(data, ensure_ascii=False))


    def mapping(self):
        data_json = {
            "link": "https://www.bps.go.id/id/exim",
            "tags": "",
            "source": "bps",
            "title": "Data Ekspor Impor Nasional",
            "sub_title": "Data Ekspor Impor",
            "range_data": self.range_data,
            "create_date": "",
            "update_date": "",
            "desc": self.desc,
            "category": '',
            "sub_category": "",
            "path_data_raw": self.path_data_raw,
            "crawling_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "crawling_time_epoch": int(datetime.now().timestamp()),
            "table_name": "",
            "country_name": "Indonesia",
            "level": "Nasional",
            "stage": "Crawling data",
            "data" : self.data
            }
        return data_json