from telegram import Bot
import os
from datetime import datetime

class Erris:

    # ? inisialisasi bot
    def __init__(self, chat_id: str = None) -> None:
        BOT_TOKEN = '7352287207:AAGrFDiD8ucw-ANNGmP0rEJ_aaBdlKIfBVI'

        if chat_id is None:
            CHAT_ID = '6627739598'
        else:
            CHAT_ID = chat_id

        self.chat_id = CHAT_ID
        self.bot = Bot(token=BOT_TOKEN)
        

    
    # ? send message function
    async def send_message(self, message:str, show_dir: bool = False, show_datetime: bool = False):

        # ? additional info
        additional_info = "\n\n<====INFO====>"
        if show_dir:
            directory_location = os.path.dirname(os.path.abspath(__file__))
            additional_info += f'\npath : {directory_location}'

        if show_datetime:
            additional_info += f'\ndatetime : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'

        if show_dir == False and show_datetime == False:
            additional_info = ""

        # ? jika message adalah list
        if isinstance(message, list):
            message_list = '\n\n'.join(map(str, message))
            message_list += additional_info
            await self.bot.send_message(chat_id=self.chat_id, text=message_list)


        else:
            message += additional_info
            await self.bot.send_message(chat_id=self.chat_id, text=message)
