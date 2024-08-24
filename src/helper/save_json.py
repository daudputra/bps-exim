import json
import os
import aiofiles
from datetime import datetime

class SaveJson:

    def __init__(self, response, title, range_data:int, desc, tags:list, category, data, path_data_raw=[], sub_title=""):
        self.response = response
        self.title = title
        self.range_data = range_data
        self.desc = desc
        self.tags = tags
        self.category = category
        self.data = data
        self.path_data_raw = path_data_raw
        self.sub_title = sub_title


    async def save_json_local(self, filename, *folders):
        directory = os.path.join('data', *folders)
        
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, filename)
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as json_file:
            data = self.mapping()
            await json_file.write(json.dumps(data, ensure_ascii=False))


    def mapping(self):
        data_json = {
            "link": self.response,
            "tags": self.tags,
            "source": "bps",
            "title": self.title,
            "sub_title": self.sub_title,
            "range_data": self.range_data,
            "create_date": "",
            "update_date": "",
            "desc": self.desc,
            "category": self.category,
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