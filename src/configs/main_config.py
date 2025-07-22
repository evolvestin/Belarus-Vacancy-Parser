import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv
from root_path import ROOT_DIR

load_dotenv()


class Config:
    BOT_TOKEN: str = os.getenv('BOT_TOKEN')
    BASE_EMOJIS_STORAGE_URL: str = 'https://raw.githubusercontent.com/iamcal/emoji-data/master'
    ADMIN_IDS: list[int] = [int(id_) for id_ in os.getenv('ADMIN_IDS', '').split(',') if id_]

    # Stores from Telegram via vars_service
    POST_ID: int = 0
    BLOCK: bool = False
    INST_BLOCK: bool = False
    DATE: datetime = datetime.now(timezone(timedelta(hours=3)))

    CONFIGS_DIR: Path = ROOT_DIR.joinpath('src', 'configs')
    EMOJIS_DIR: Path = ROOT_DIR.joinpath('images', 'emojis')
    EMOJIS_DB_PATH: Path = ROOT_DIR.joinpath('db', 'emoji.db')
    LOG_FILE_PATH: Path = CONFIGS_DIR.joinpath('logs.txt')
    INSTAGRAM_SESSION_FILE_PATH: Path = CONFIGS_DIR.joinpath('instagram_session.json')

    @classmethod
    def init_dirs(cls) -> None:
        cls.EMOJIS_DIR.parent.mkdir(exist_ok=True)
        cls.EMOJIS_DIR.mkdir(exist_ok=True)
        cls.EMOJIS_DB_PATH.parent.mkdir(exist_ok=True)
        cls.CONFIGS_DIR.parent.mkdir(exist_ok=True)
        cls.CONFIGS_DIR.mkdir(exist_ok=True)

    @classmethod
    def set_default_vars(cls) -> None:
        cls.POST_ID = 0
        cls.BLOCK = False
        cls.INST_BLOCK = False
        cls.DATE = datetime.now(timezone(timedelta(hours=3)))


if not Config.BOT_TOKEN:
    raise ValueError('BOT_TOKEN not set in .env file')
