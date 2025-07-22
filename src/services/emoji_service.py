import asyncio
import aiohttp
import aiosqlite
from pathlib import Path
from typing import List, Tuple
from src.configs.main_config import Config
from src.logger import setup_logger

logger = setup_logger()


class EmojiService:
    @staticmethod
    async def download_emoji_data() -> List[dict]:
        """Download emoji.json from the repository."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{Config.BASE_EMOJIS_STORAGE_URL}/emoji.json') as response:
                response.raise_for_status()
                return await response.json()

    @staticmethod
    async def download_emoji_image(image_name: str) -> Path:
        """Download an emoji image and save it locally."""
        image_path = Config.EMOJIS_DIR / image_name
        if not image_path.exists():
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{Config.BASE_EMOJIS_STORAGE_URL}/img-apple-160/{image_name}') as response:
                    response.raise_for_status()
                    image_path.write_bytes(await response.read())
        return image_path

    @staticmethod
    def unicode_to_emoji(unified: str) -> str:
        """Convert unified Unicode string (e.g., '1F600') to emoji character."""
        code_points = [int(cp, 16) for cp in unified.split('-')]
        return ''.join(chr(cp) for cp in code_points)

    @staticmethod
    async def setup_database() -> Tuple[aiosqlite.Connection, aiosqlite.Cursor]:
        """Set up the SQLite database and create the emoji table."""
        conn = await aiosqlite.connect(Config.EMOJIS_DB_PATH)
        cursor = await conn.cursor()
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS emojis (
                name TEXT,
                emoji TEXT,
                image_path TEXT
            )
        ''')
        await conn.commit()
        return conn, cursor

    @staticmethod
    async def fetch_and_store_emojis():
        """Main function to fetch emojis and store them in the database."""
        try:
            logger.info('Starting emoji fetch process')
            emoji_data = await EmojiService.download_emoji_data()
            conn, cursor = await EmojiService.setup_database()

            emoji_entries = []
            for emoji in emoji_data:
                name = emoji.get('name', '')
                unified = emoji.get('unified', '')
                image_name = emoji.get('image', '')
                has_apple_image = emoji.get('has_img_apple', False)

                if not has_apple_image or not image_name:
                    continue
                emoji_char = EmojiService.unicode_to_emoji(unified)
                emoji_entries.append((name, emoji_char, image_name))

            tasks = [EmojiService.download_emoji_image(entry[2]) for entry in emoji_entries]
            image_paths = await asyncio.gather(*tasks, return_exceptions=True)

            for (name, emoji_char, _), image_path in zip(emoji_entries, image_paths):
                if isinstance(image_path, Exception):
                    logger.error(f'Failed to download image for {name}: {image_path}')
                    continue
                await cursor.execute(
                    'INSERT INTO emojis (name, emoji, image_path) VALUES (?, ?, ?)',
                    (name, emoji_char, str(image_path))
                )

            await conn.commit()
            logger.info('Emoji fetch and store completed successfully')
        except Exception as e:
            logger.error(f'Error in fetch_and_store_emojis: {e}')
            raise
