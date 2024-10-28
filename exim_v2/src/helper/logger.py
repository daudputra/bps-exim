import logging
import os
import colorlog

def setup_logging(log_file):
    """
    Setup logging configuration.
    :param log_file: Nama file untuk menyimpan log, termasuk foldernya.
    """
    log_folder = os.path.dirname(log_file)
    if log_folder and not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # Mendapatkan logger utama
    logger = logging.getLogger(log_file)

    if not logger.hasHandlers():
        # File Handler (untuk menyimpan log di file)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))

        # Console Handler (untuk menampilkan log di console dengan warna)
        console_handler = colorlog.StreamHandler()
        console_handler.setFormatter(colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        ))

        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

async def log_message(log_level, log_file, message):
    """
    Log a message to a specified file with the given log level.
    :param log_level: Level logging, seperti 'DEBUG', 'INFO', 'WARNING', 'ERROR', atau 'CRITICAL'.
    :param log_file: Nama file untuk menyimpan log, termasuk foldernya.
    :param message: Pesan yang ingin dicatat.
    """
    logger = setup_logging(log_file)
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    logger.log(level, message)