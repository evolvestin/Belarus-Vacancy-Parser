import asyncio
from aiogram import Bot, Dispatcher
from src.handlers import router
from src.logger import setup_logger
from src.configs.main_config import Config
from src.services.vars_service import VarsService

logger = setup_logger()


async def main() -> None:
    logger.info('Starting bot')
    Config.init_dirs()
    bot: Bot = Bot(token=Config.BOT_TOKEN)
    await VarsService.load_vars(bot)
    dispatcher: Dispatcher = Dispatcher()
    dispatcher.include_router(router)
    await dispatcher.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
