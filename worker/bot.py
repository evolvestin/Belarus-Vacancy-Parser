import os
import re
import pickle
import random
import asyncio
import gspread
import _thread
import requests
import inst_text
import functions
from PIL import Image
from copy import copy
from time import sleep
from image import image
from GDrive import Drive
from typing import Union
from aiogram import types
from chrome import chrome
from bs4 import BeautifulSoup
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from selenium.webdriver.common.by import By
from datetime import datetime, timezone, timedelta
from functions import time_now, html_link, html_secure
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
# =================================================================================================================
stamp1 = time_now()


def vars_query(thread_bot, commands: Union[str, list], regex: str = '(.*?) = (.*?);'):
    commands = commands if type(commands) == list else [commands]
    data, response = [], {'_': commands}
    for command in thread_bot.get_my_commands(scope=None, language_code=None):
        data.append(command.description) if command.command in commands else None
    for line in '\n'.join(data).split('\n'):
        search = re.search(regex, line)
        response.update({search.group(1): search.group(2)}) if search else None
    return response, re.sub(r'\(\.\*\?\)', '{}', regex)


functions.environmental_files()
#channels = {'main': 396978030, 'instagram': 396978030}
channels = {'main': -1001404073893, 'instagram': -1001186786378}
tz, admins, unused_links = timezone(timedelta(hours=3)), [396978030, 470292601], []
worksheet = gspread.service_account('person2.json').open('Belarus-Vacancies').worksheet('main')
#Auth = functions.AuthCentre(ID_DEV=396978030, TOKEN=os.environ['TOKEN'], DEV_TOKEN=os.environ['DEV_TOKEN'])
Auth = functions.AuthCentre(ID_DEV=-1001312302092, TOKEN=os.environ['TOKEN'], DEV_TOKEN=os.environ['DEV_TOKEN'])

server, query_regex = vars_query(Auth.bot, 'vars')
server['post_id'] = int(server['post_id']) if server.get('post_id') else None
used_links, inst_username, google_folder_id = worksheet.col_values(1), None, None
server['date'] = datetime.fromisoformat(server['date']) if server.get('date') else None
bot, drive, dispatcher = Auth.async_bot, Drive('person2.json'), Dispatcher(Auth.async_bot)

print('STARTING server[date]', server['date'])
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}
for google_folder in drive.files(only_folders=True):
    if google_folder['name'] == 'sessions':
        folder_id = google_folder['id']
for google_file in drive.files(name_startswith='cookies', parents=google_folder_id):
    if os.environ['cookies'] in google_file['name']:
        drive.download_file(google_file['id'], 'cookies.pkl')
        search_username = re.search(r'user: (.*)', google_file['description'])
        inst_username = search_username.group(1) if search_username else None
# =================================================================================================================


def bold(text, md=False):
    return f'**{text}**' if md else f'<b>{text}</b>'


def italic(text, md=False):
    return f'__{text}__' if md else f'<i>{text}</i>'


async def edit_vars():
    commands = iter_commands(server, query_regex)
    commands.update({'enable': 'Включить постинг на канале', 'disable': 'Отключить постинг на канале'})
    list_commands = [types.BotCommand(command, description) for command, description in commands.items()]
    try:
        await bot.set_my_commands(list_commands)
    except IndexError and Exception as error:
        Auth.dev.message(text=f"{bold(f'Проблема с изменением переменных в боте @{Auth.username}')} "
                              f"\n\n{html_secure(server)}\n{html_secure(error)}")


def inst_handler(data: dict):
    array = [bold(f"👨🏻‍💻 {data['title']}", md=True)] if data.get('title') else []
    array.append(f"🏙 {data['short_place']}") if data.get('short_place') else None
    array.append(f"🏅 Опыт работы ➡ {data['experience']}") if data.get('experience') else None
    array.append(f"👨🏻‍🎓 Образование ➡ {data['education']}") if data.get('education') else None
    array.append(bold(f"💸 З/П {data['money']} руб.", md=True) + '\n') if data.get('money') else None
    array.extend([bold(line, md=True) for line in ['📘 Контакты', '💎 В Telegram канале', '🔗 Ссылка в профиле']])
    array.append(f"\n🔍 Пиши в поиске 🆔 {data['post_id']}") if data.get('post_id') else None
    return '\n'.join(array)


def iter_commands(data: dict, var_format: str):
    commands, command_value, command_values = data.get('_', []), [], []
    for key, value in data.items():
        if key != '_':
            if len(f"{'n'.join(command_value)}\n{var_format.format(key, value)}") <= 256:
                command_value.append(var_format.format(key, value))
            else:
                command_values.append('\n'.join(command_value))
                command_value = [var_format.format(key, value)]
    else:
        command_values.append('\n'.join(command_value))
    return {command: value for command, value in zip(commands, command_values)}


def tg_handler(data: dict):
    picture = image(background=Image.open('logo.png'), return_link=True,
                    text=re.sub(r'\(.*?\)', '', data.get('title', 'Sample')).strip(),
                    font_family='Roboto', font_weight='Condensed', top_indent=100, top_indent_2=150)
    text = f"{html_link(picture, '​​')}️" if picture else ''
    text += f"👨🏻‍💻 {bold(data['title'])}\n" if data.get('title') else ''
    text += f"🏙 {data['short_place']}\n" if data.get('short_place') else ''
    text += f"🏅 Опыт работы ➡ {data['experience'].capitalize()}\n" if data.get('experience') else ''
    text += f"👨‍🎓 Образование ➡ {data['education'].capitalize()}\n" if data.get('education') else ''
    text += f"💸 {bold('З/П')} {data['money']} руб.\n" if data.get('money') else ''
    text += f"\n{bold('📔 Контакты')}\n"
    for key in ['org_name', 'contact', 'numbers']:
        text += f"{data[key]}\n" if data.get(key) else ''
    text += f"{data['email']} ➡ Резюме\n" if data.get('email') else ''
    text += f"\n{bold('🏘 Адрес')}\n{data['place']}\n" if data.get('place') else ''
    text += f"🚇 {data['underground']}\n" if data.get('underground') else ''
    map_link = f"http://maps.yandex.ru/?text={data['geo']}" if data.get('geo') else None
    text += f"\n📍 {html_link(map_link, 'На карте')}\n" if map_link else ''
    text += f"\n🔎 {html_link(data['link'], 'Источник')}\n" if data.get('link') else ''
    text += f"\n🆔 {italic(data['post_id'])}" if data.get('post_id') else ''
    text += f"\n{italic('💼ТЕГИ:')} #{' #'.join(data['tags'])}\n" if data.get('tags') else ''
    return {'text': text, 'image': picture}


async def inst_poster(username: str, description: str, image_path: str):
    response = 'Process crashed'
    try:
        driver = chrome(os.environ.get('local'))
        driver.set_window_size(500, 1200)
        driver.get(f'https://www.instagram.com/')
        input_xpath = "//input[@accept='image/jpeg,image/png,image/heic,image/heif,video/mp4,video/quicktime']"
        for cookie in pickle.load(open('cookies.pkl', 'rb')):
            driver.add_cookie(cookie)
        driver.get(f'https://www.instagram.com/{username}/')
        await asyncio.sleep(random.normalvariate(3, 1))
        driver.find_element(By.TAG_NAME, 'nav').find_elements(By.TAG_NAME, 'svg')[3].click()
        WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, "//div[@role='dialog']")))
        await asyncio.sleep(random.normalvariate(3, 1))
        driver.find_element(By.XPATH, input_xpath).send_keys(f'{os.getcwd()}/{image_path}')
        WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, "//div[@role='dialog']")))
        div = driver.find_element(By.XPATH, "//div[@role='dialog']")
        await asyncio.sleep(random.normalvariate(3, 1))
        div.find_elements(By.TAG_NAME, 'button')[1].click()
        WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, "//div[@role='tablist']")))
        await asyncio.sleep(random.normalvariate(3, 1))
        div.find_elements(By.TAG_NAME, 'button')[1].click()
        WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.TAG_NAME, 'textarea')))
        await asyncio.sleep(random.normalvariate(3, 1))
        driver.find_element(By.TAG_NAME, 'textarea').send_keys(description)
        await asyncio.sleep(random.normalvariate(3, 1))
        div.find_elements(By.TAG_NAME, 'button')[1].click()
        title = driver.find_element(By.XPATH, "//div[@role='dialog']").get_attribute('aria-label')
        while title == driver.find_element(By.XPATH, "//div[@role='dialog']").get_attribute('aria-label'):
            sleep(1)
        await asyncio.sleep(random.normalvariate(3, 1))
        for div in driver.find_elements(By.XPATH, "//div[@role='presentation' and not(@tabindex='-1')]"):
            div.find_element(By.TAG_NAME, 'button').click() if div.find_elements(By.TAG_NAME, 'button') else None
        await asyncio.sleep(random.normalvariate(3, 1))
        response = driver.find_element(By.TAG_NAME, 'article').find_element(By.TAG_NAME, 'a').get_attribute('href')
        driver.close()
    except IndexError and Exception:
        await Auth.dev.executive(None)
    return str(response)


def prc_parser(link: str):
    data = {'link': link, 'tags': []}
    soup = BeautifulSoup(requests.get(link).text, 'html.parser')
    if soup.find('span', class_='hidden-vac-contact'):
        link += '?token=wykzQ7x5oq6kZWG7naOvHprT4vcZ1vdFFUSXoOfmKR10pPWq0ox5acYvr3wcfg00'
        soup = BeautifulSoup(requests.get(link).text, 'html.parser')

    place = soup.find('div', class_='job-address')
    tag_list = soup.find('div', class_='categories')
    money = soup.find('div', class_='vacancy__salary')
    short_place = soup.find('div', class_='vacancy__city')
    org_name = soup.find('div', class_='vacancy__org-name')
    underground = soup.find('div', class_='vacancy__metro')
    title_div = soup.find('div', class_='vacancy__title-wrap')
    geo = re.search('{"latitude":"(.*?)","longitude":"(.*?)","zoom"', str(soup))

    tags = tag_list.find_all('a') if tag_list else []
    title = title_div.find('h1') if title_div else None
    underground_list = underground.find_all('span', class_='nowrap') if underground else []
    search_money = re.search(r'(\d+)', re.sub(r'\s', '', money.get_text())) if money else None
    search_payroll = re.search(r'(\d+)-(\d+)', re.sub(r'\s', '', money.get_text())) if money else None
    underground_modded_list = [re.sub(r'\s+', ' ', un.get_text()).strip().capitalize() for un in underground_list]

    data['underground'] = ', '.join(underground_modded_list) or None
    data['money'] = f"{search_money.group(1)}" if search_money else None
    data['place'] = re.sub(r'\s+', ' ', place.get_text()).strip() if place else None
    data['geo'] = re.sub(r'\s', '', f"{geo.group(1)},{geo.group(2)}").strip() if geo else None
    data['money'] = f"{data['money']}+" if search_payroll and data['money'] else data.get('money')
    data['short_place'] = re.sub(r'\s+', ' ', short_place.get_text()).strip() if short_place else None
    data['org_name'] = re.sub(r'\s+', ' ', org_name.find('a').get_text()).strip() if org_name else None
    data['title'] = re.sub(r'\s+', ' ', re.sub('/', ' / ', title.get_text())).strip() if title else None

    for tag in tags:
        data['tags'].extend([t.strip() for t in re.sub(r'[\s_—-]+', '_', tag.get_text()).split('_/_')])

    for div in soup.find_all('div', class_='vacancy__item'):
        education = div.find('p', class_='vacancy__education')
        experience = div.find('p', class_='vacancy__experience')
        edu_text = re.sub(r'[оО]бразование', '', education.get_text()) if education else None
        exp_text = re.sub(r'[оО]пыт работы', '', experience.get_text()) if experience else None
        data['education'] = re.sub(r'\s+', ' ', edu_text).strip() if edu_text else data.get('education')
        data['experience'] = re.sub(r'\s+', ' ', exp_text).strip() if exp_text else data.get('experience')

    for div in soup.find_all('div', class_='org-info__item'):
        contact_div = div.find('div', class_='org-info__subtitle h4-like')
        contact_title = contact_div.get_text() if contact_div else None
        if contact_title in ['Электронная почта:', 'Номера телефонов:']:
            value = div.find('div', class_='org-info__contact-list')
            key = 'email' if contact_title == 'Электронная почта:' else 'numbers'
            data[key] = re.sub(r'[^\S\r\n]+', ' ', value.get_text('\n')).strip() if value else None
        elif contact_title == 'Контактное лицо:':
            value = div.find('div', attrs={'class': None})
            data['contact'] = re.sub(r'\s+', ' ', value.get_text()).strip() if value else None
    return data


@dispatcher.channel_post_handler()
async def detector(message: types.Message):
    global server
    try:
        if message['chat']['id'] == channels['main'] and message['message_id'] + 1 > server['post_id']:
            await asyncio.sleep(60)
            if message['message_id'] + 1 > server['post_id']:
                server['post_id'] = message['message_id'] + 1
                await edit_vars()
    except IndexError and Exception:
        await Auth.dev.async_except(message)


@dispatcher.message_handler()
async def repeat_all_messages(message: types.Message):
    global server
    try:
        if message['chat']['id'] in admins:
            if message['text'].lower().startswith('/reboot'):
                text, _ = Auth.logs.reboot()
                await bot.send_message(message['chat']['id'], text, parse_mode='HTML')

            elif message['text'].lower().startswith('/vars'):
                commands = iter_commands(server, query_regex)
                await bot.send_message(message['chat']['id'], '\n'.join(commands.values()), parse_mode='HTML')

            elif message['text'].lower().startswith('/pic'):
                link = image(background=Image.open('logo.png'), return_link=True,
                             text=re.sub('/[pP][iI][cC]', '', message['text'], 1).strip(),
                             font_family='Roboto', font_weight='Condensed', top_indent=100, top_indent_2=150)
                await bot.send_message(message['chat']['id'], f"{html_link(link, '​​')}️", parse_mode='HTML')

            elif message['text'].lower().startswith(('/enable', '/disable')):
                if message['text'].lower().startswith('/disable'):
                    text, block = f"Посты на канале {bold('не')} публикуются", 'True'
                else:
                    text, block = 'Посты на канале публикуются в штатном режиме', 'False'
                if server['block'] != block:
                    server['block'] = block
                    await edit_vars()
                await bot.send_message(message['chat']['id'], text, parse_mode='HTML')

            elif message['text'].lower().startswith('/test'):
                data = prc_parser('https://praca.by/vacancy/460578/')
                data['post_id'] = copy(server['post_id'])
                inst_path = image(inst_handler(data) or 'Sample', text_align='left', font_family='Roboto',
                                  background_color=(254, 230, 68), original_width=1080, original_height=1080)
                inst_description = inst_text.generator(post_id=data.get('post_id', 0),
                                                       place=data.get('short_place', ''),
                                                       vacancy_tags=data.get('tags', []))
                inst_link = await inst_poster(inst_username, inst_description, inst_path)
                Auth.bot.send_message(admins[0], text=inst_link)
                os.remove(inst_path)
                await bot.send_message(message['chat']['id'], 'все ок', parse_mode='HTML')
    except IndexError and Exception:
        await Auth.dev.async_except(message)


def auto_reboot():
    reboot = None
    while True:
        try:
            sleep(30)
            date = datetime.now(tz)
            if date.strftime('%H') == '01' and date.strftime('%M') == '59':
                reboot = True
                while date.strftime('%M') == '59':
                    sleep(1)
                    date = datetime.now(tz)
            if reboot:
                reboot = None
                text, _ = Auth.logs.reboot()
                Auth.dev.printer(text)
        except IndexError and Exception:
            Auth.dev.thread_except()


async def site_handlers():
    async def site_handler(address: str, main_class: str, link_class: str, parser):
        global used_links, unused_links, worksheet
        now, links = datetime.now(tz), []
        soup = BeautifulSoup(requests.get(address, headers=headers).text, 'html.parser')
        for link_div in soup.find_all('div', attrs={'class': main_class}):
            link = link_div.find('a', attrs={'class': link_class})
            links.append(link.get('href')) if link else None
        for link in links:
            if link not in used_links and link not in unused_links and (11 <= int(now.strftime('%H')) < 21):
                if (server['date'] + timedelta(hours=2)) < now and server['block'] != 'True':
                    try:
                        link_range = worksheet.range(f'A{len(used_links) + 1}:A{len(used_links) + 1}')
                    except IndexError and Exception as error:
                        if 'exceeds grid limits' in str(error):
                            worksheet.add_rows(1000)
                            worksheet.delete_rows(1, 1000)
                            used_links = worksheet.col_values(1)
                            link_range = worksheet.range(f'A{len(used_links) + 1}:A{len(used_links) + 1}')
                            sleep(5)
                        else:
                            service_account = gspread.service_account('person2.json')
                            Auth.dev.message(text=f'Ошибка в вакансиях\n{html_secure(error)}')#
                            worksheet = service_account.open('Belarus-Vacancies').worksheet('main')
                            link_range = worksheet.range(f'A{len(used_links) + 1}:A{len(used_links) + 1}')
                        #else:
                        #   raise error
                    link_range[0].value = link
                    worksheet.update_cells(link_range)
                    used_links.append(link)
                    data = parser(link)
                    data['post_id'] = copy(server['post_id'])
                    await poster(data)
                    Auth.dev.printer(f'Обработано: {link}')
                else:
                    unused_links.append(link)
        sleep(30)

    async def poster(data: dict):
        global server
        tg = tg_handler(data)
        if any(data.get(key) is None for key in ['money', 'title', 'short_place']):
            data['Причина'] = 'Отсутствуют поля'
        elif re.search('водитель|яндекс|такси|уборщи', data['title'].lower()):
            data['Причина'] = 'Неподходящая деятельность'
        elif data.get('org_name') and re.search('доброном', data['org_name'].lower()):
            data['Причина'] = f"{'Добро'}ном"
        elif data.get('experience') and re.search('6', data['experience']):
            data['Причина'] = 'Слишком много опыта'

        if data.get('Причина'):
            text = f"{html_link(tg['image'], '​​') if tg.get('image') else ''}️Не опубликовано: &#123;\n"
            for key, value in data.items():
                selected = ['link', 'money', 'title', 'Причина', 'short_place']
                text += f"{' ' * 6}{functions.under(bold(key)) if key in selected else key}: {html_secure(value)}\n"
            await bot.send_message(admins[0], f'{text}&#125;', parse_mode='HTML')
        else:
            message = await bot.send_message(channels['main'], tg['text'], parse_mode='HTML')
            server['post_id'] = message['message_id'] + 1
            message_date = datetime.fromtimestamp(message['date'], tz)
            inst_path = image(inst_handler(data) or 'Sample', text_align='left', font_family='Roboto',
                              background_color=(254, 230, 68), original_width=1080, original_height=1080)
            inst_description = inst_text.generator(post_id=data.get('post_id', 0),
                                                   place=data.get('short_place', ''),
                                                   vacancy_tags=data.get('tags', []))
            inst_link = await inst_poster(inst_username, inst_description, inst_path)
            with open(inst_path, 'rb') as picture:
                Auth.bot.send_photo(channels['instagram'], picture, caption=inst_link)
            with open(inst_path, 'rb') as picture:
                Auth.bot.send_document(channels['instagram'], picture)
            os.remove(inst_path)
            if server['date'] < message_date:
                print('date', server['date'], 'message_date', message_date)
                server['date'] = message_date
                await edit_vars()

    while True:
        try:
            await site_handler(parser=prc_parser, main_class='vac-small__column vac-small__column_2',
                               address='https://praca.by/search/vacancies/', link_class='vac-small__title-link')
        except IndexError and Exception:
            Auth.dev.async_except()


def start(stamp):
    def set_async_thread():
        loop = asyncio.new_event_loop()
        for async_element in async_threads:
            loop.create_task(async_element())
        loop.run_forever()
    try:
        alert, threads, async_threads = f"\n{bold('Скрипты не запущены')}", [auto_reboot], []
        if os.environ.get('local'):
            threads = []
            Auth.dev.printer(f'Запуск бота локально за {time_now() - stamp} сек.')
        else:
            if all(server.get(key) for key in ['date', 'block', 'post_id']) and inst_username:
                alert, async_threads = '', [site_handlers]
            Auth.dev.start(stamp, alert)
            Auth.dev.printer(f'Бот запущен за {time_now() - stamp} сек.')

        for thread_element in threads:
            _thread.start_new_thread(thread_element, ())
        _thread.start_new_thread(set_async_thread, ()) if async_threads else None
        executor.start_polling(dispatcher, allowed_updates=functions.allowed_updates)
    except IndexError and Exception:
        Auth.dev.thread_except()


if os.environ.get('local'):
    start(stamp1)
