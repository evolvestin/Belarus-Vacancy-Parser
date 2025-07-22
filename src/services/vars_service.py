import re
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat
from datetime import datetime
from src.configs.main_config import Config
from src.logger import setup_logger

logger = setup_logger()


class VarsService:
    MAX_DESCRIPTION_LENGTH: int = 256
    COMMAND_PREFIX: str = 'vars'
    VAR_FORMAT: str = '{}={};'

    @staticmethod
    async def load_vars(bot: Bot) -> None:
        vars_data: dict[str, str] = {}
        for admin_id in Config.ADMIN_IDS:
            try:
                commands: list[BotCommand] = await bot.get_my_commands(
                    scope=BotCommandScopeChat(chat_id=admin_id)
                )
                for command in commands:
                    if command.command.startswith(VarsService.COMMAND_PREFIX):
                        for key_value in command.description.split(';'):
                            key, value = VarsService._parse_var_line(key_value)
                            if key and value:
                                vars_data[key] = value
                break
            except Exception as e:
                logger.error(f'Error loading vars for admin {admin_id}: {e}')
        VarsService._apply_vars(vars_data)
        if not vars_data:
            await VarsService._save_default_vars(bot)

    @staticmethod
    def _parse_var_line(line: str) -> tuple[str, str]:
        match = re.match(r'(\w+)=(.+);', line.strip())
        return (match.group(1), match.group(2)) if match else (None, None)

    @staticmethod
    def _apply_vars(vars_data: dict[str, str]) -> None:
        try:
            Config.POST_ID = int(vars_data.get('post_id', Config.POST_ID))
            Config.BLOCK = vars_data.get('block', str(Config.BLOCK)).lower() == 'true'
            Config.INST_BLOCK = vars_data.get('inst_block', str(Config.INST_BLOCK)).lower() == 'true'
            Config.DATE = datetime.fromisoformat(vars_data['date']) if vars_data.get('date') else Config.DATE
        except (ValueError, KeyError) as e:
            logger.error(f'Error applying vars: {e}')

    @staticmethod
    async def _save_default_vars(bot: Bot) -> None:
        vars_dict: dict[str, str] = {
            'post_id': str(Config.POST_ID),
            'block': str(Config.BLOCK).lower(),
            'inst_block': str(Config.INST_BLOCK).lower(),
            'date': Config.DATE.isoformat()
        }
        await VarsService.save_vars(bot, vars_dict)

    @staticmethod
    async def save_vars(bot: Bot, vars_dict: dict[str, str]) -> None:
        commands: list[BotCommand] = []
        current_command: list[str] = []
        current_length: int = 0
        command_index: int = 1

        for key, value in vars_dict.items():
            var_line: str = VarsService.VAR_FORMAT.format(key, value)
            if current_length + len(var_line) + 1 > VarsService.MAX_DESCRIPTION_LENGTH:
                commands.append(BotCommand(
                    command=f'{VarsService.COMMAND_PREFIX}{command_index}',
                    description='\n'.join(current_command)
                ))
                current_command = [var_line]
                current_length = len(var_line) + 1
                command_index += 1
            else:
                current_command.append(var_line)
                current_length += len(var_line) + 1

        if current_command:
            commands.append(BotCommand(
                command=f'{VarsService.COMMAND_PREFIX}{command_index}',
                description='\n'.join(current_command)
            ))

        for admin_id in Config.ADMIN_IDS:
            try:
                await bot.set_my_commands(
                    commands=commands,
                    scope=BotCommandScopeChat(chat_id=admin_id)
                )
                logger.info(f'Variables saved to bot commands for admin {admin_id}')
            except Exception as e:
                logger.error(f'Error saving vars to commands for admin {admin_id}: {e}')

    @staticmethod
    async def update_var(bot: Bot, key: str, value: str) -> None:
        vars_dict: dict[str, str] = {
            key: value,
            'post_id': str(Config.POST_ID),
            'block': str(Config.BLOCK).lower(),
            'inst_block': str(Config.INST_BLOCK).lower(),
            'date': Config.DATE.isoformat(),
        }
        await VarsService.save_vars(bot, vars_dict)

    @staticmethod
    async def get_vars(bot: Bot) -> str:
        descriptions: list[str] = []
        for admin_id in Config.ADMIN_IDS:
            try:
                commands: list[BotCommand] = await bot.get_my_commands(
                    scope=BotCommandScopeChat(chat_id=admin_id)
                )
                for command in commands:
                    if command.command.startswith(VarsService.COMMAND_PREFIX):
                        descriptions.append(command.description)
            except Exception as e:
                logger.error(f'Error getting vars for admin {admin_id}: {e}')
        return '\n'.join(descriptions) if descriptions else 'No variables found'
