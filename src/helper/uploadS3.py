import aiofiles
import s3fs
import logging

from .logging import log_message

logger = logging.getLogger(__name__)

async def upload_to_s3(local_path: str, raw_path: str):
    try:
        client_kwargs = {
            'key': 'GLZG2JTWDFFSCQVE7TSQ',
            'secret': 'VjTXOpbhGvYjDJDAt2PNgbxPKjYA4p4B7Btmm4Tw',
            'endpoint_url': 'http://10.12.1.149:8000',
            'anon': False
        }

        s3 = s3fs.S3FileSystem(**client_kwargs)

        async with aiofiles.open(local_path, 'rb') as local_file:
            file_content = await local_file.read()

        with s3.open(raw_path, 'wb') as s3_file:
            s3_file.write(file_content)

        if not s3.exists(raw_path):
            await log_message('ERROR', 'logs/error.log', 'File upload failed')

        #     print('File upload successfully')
        # else:
        #     print('File upload failed')

    except Exception as e:
        await log_message('ERROR', 'logs/error.log', f'error upload to s3 == {e}')