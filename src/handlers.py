from aiogram import Router
from aiogram.filters import Command, BaseFilter
from aiogram.types import Message
from src.services.emoji_service import EmojiService
from src.services.vars_service import VarsService
from src.configs.main_config import Config
from src.logger import setup_logger

router = Router()
logger = setup_logger()


class IsAdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in Config.ADMIN_IDS


@router.message(IsAdminFilter(), Command('fetch_emojis'))
async def fetch_emojis_command(message: Message) -> None:
    try:
        await message.answer('Starting emoji fetch process...')
        await EmojiService.fetch_and_store_emojis()
        await message.answer('Emojis fetched and stored successfully!')
    except Exception as e:
        logger.error(f'Error in fetch_emojis_command: {e}')
        await message.answer('An error occurred while fetching emojis.')


@router.message(IsAdminFilter(), Command('vars'))
async def vars_command(message: Message) -> None:
    try:
        vars_text: str = await VarsService.get_vars(message.bot)
        await message.answer(vars_text, parse_mode='HTML')
    except Exception as e:
        logger.error(f'Error in vars_command: {e}')
        await message.answer('An error occurred while fetching variables.')


@router.message(IsAdminFilter(), Command('inst'))
async def inst_command(message: Message) -> None:
    try:
        new_value: str = 'true' if not Config.INST_BLOCK else 'false'
        await VarsService.update_var(message.bot, 'inst_block', new_value)
        Config.INST_BLOCK = new_value == 'true'
        text: str = f"Вакансии в Instagram {'не ' if Config.INST_BLOCK else ''}публикуются"
        await message.answer(text, parse_mode='HTML')
    except Exception as e:
        logger.error(f'Error in inst_command: {e}')
        await message.answer('An error occurred while toggling Instagram posting.')


@router.message(IsAdminFilter(), Command('toggle'))
async def toggle_command(message: Message) -> None:
    try:
        new_block_value: str = 'true' if not Config.BLOCK else 'false'
        new_inst_block_value: str = new_block_value
        await VarsService.update_var(message.bot, 'block', new_block_value)
        await VarsService.update_var(message.bot, 'inst_block', new_inst_block_value)
        Config.BLOCK = new_block_value == 'true'
        Config.INST_BLOCK = new_inst_block_value == 'true'
        text: str = f"Вакансии {'не ' if Config.BLOCK else ''}публикуются"
        await message.answer(text, parse_mode='HTML')
    except Exception as e:
        logger.error(f'Error in toggle_command: {e}')
        await message.answer('An error occurred while toggling posting.')
