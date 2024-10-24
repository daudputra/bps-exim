import json
import os
import aiofiles
from datetime import datetime

class SaveJson:

    def __init__(self, response, title, sub_title, range_data, create_data, tags, data, path_data_raw):
        self.response = response
        self.title = title
        self.sub_title = sub_title
        self.range_data = range_data
        self.create_data = create_data
        self.tags = tags
        self.data = data
        self.path_data_raw = path_data_raw


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
            "source": "karir.com",
            "title": self.title,
            "sub_title": self.sub_title,
            "range_data": self.range_data,
            "create_date": self.create_data,
            "update_date": "",
            "desc": "",
            "category": 'Lowongan',
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