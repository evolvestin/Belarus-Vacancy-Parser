import logging
from logging.handlers import RotatingFileHandler
from src.configs.main_config import Config


def setup_logger():
    file_handler = RotatingFileHandler(
        Config.LOG_FILE_PATH,
        maxBytes=20 * 1024 * 1024,
        backupCount=1,
        encoding='utf-8',
    )

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            file_handler
        ]
    )
    return logging.getLogger(__name__)
