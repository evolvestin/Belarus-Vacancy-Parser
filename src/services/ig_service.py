import os
import json
import random
import instagrapi
from dotenv import load_dotenv
from instagrapi.exceptions import BadPassword, LoginRequired, ClientError
from src.configs.main_config import Config
from src.configs.ig_tags import INSTAGRAM_CITY_TAGS, INSTAGRAM_BELARUS_TAGS
from src.logger import setup_logger


logger = setup_logger()
load_dotenv()


class InstagramService:
    CLIENT: instagrapi.Client = None
    USERNAME: str = os.getenv('INSTAGRAM_LOGIN')
    PASSWORD: str = os.getenv('INSTAGRAM_PASSWORD')

    POST_BASE_DESCRIPTION = (
        f'Найти вакансию можно в нашем Telegram канале (ссылка в шапке профиля @{USERNAME}) '
        f'по №{{post_id}} (воспользуйтесь поиском по каналу)\n\n🆔 {{post_id}}\n\n'
    )
    POST_MAX_TAGS = 30
    POST_MAX_DESCRIPTION_LENGTH = 2000

    @classmethod
    def login_to_instagram(cls) -> None:
        cls.CLIENT = instagrapi.Client()
        if Config.INSTAGRAM_SESSION_FILE_PATH.exists():
            try:
                logger.info('Загрузка сессии Instagram')
                with Config.INSTAGRAM_SESSION_FILE_PATH.open('r', encoding='utf-8') as f:
                    session = json.load(f)
                cls.CLIENT.set_settings(session)
                cls.CLIENT.get_timeline_feed()
                logger.info('✅ Сессия Instagram успешно загружена.')
                return
            except Exception as e:
                logger.warning(f'⚠️ Не удалось загрузить сессию: {e}. Попытка войти снова.')

        try:
            logger.info(f'Попытка входа в Instagram под логином: {cls.USERNAME}...')
            cls.CLIENT.login(username=cls.USERNAME, password=cls.PASSWORD)
            with Config.INSTAGRAM_SESSION_FILE_PATH.open('w', encoding='utf-8') as f:
                json.dump(cls.CLIENT.get_settings(), f)
            logger.info('✅ Успешный вход в Instagram. Сессия сохранена.')
        except BadPassword:
            logger.error('❌ Неверный логин или пароль Instagram.')
        except LoginRequired:
            logger.error('❌ Требуется вход: проверьте учётные данные или статус аккаунта.')
        except ClientError as e:
            logger.error(f'❌ Ошибка клиента Instagram: {e}')
        except Exception as e:
            logger.error(f'❌ Неизвестная ошибка при входе в Instagram: {e}')

    @classmethod
    def generate_post_description(cls, post_id: int | str, vacancy_tags: list[str], city: str = None) -> str:
        tags = [tag.lower() for tag in vacancy_tags]
        description = cls.POST_BASE_DESCRIPTION.format(post_id=post_id)

        if city:
            city = city.lower().replace('ё', 'е')
            if city not in INSTAGRAM_CITY_TAGS:
                city = None

        city_tags = INSTAGRAM_CITY_TAGS.get(city, [])
        available_slots = cls.POST_MAX_TAGS - len(tags)
        if available_slots > 0:
            sample_city_tags = random.sample(city_tags, min(available_slots, len(city_tags)))
            tags.extend(sample_city_tags)
            available_slots -= len(sample_city_tags)

        if available_slots > 0:
            sample_tags = random.sample(INSTAGRAM_BELARUS_TAGS, min(available_slots, len(INSTAGRAM_BELARUS_TAGS)))
            tags.extend(sample_tags)

        for tag in tags:
            candidate = f' #{tag}'
            if len(description) + len(candidate) <= cls.POST_MAX_DESCRIPTION_LENGTH:
                description += candidate
            else:
                break
        return description

