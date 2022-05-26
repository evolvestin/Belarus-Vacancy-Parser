import os
import re
import emoji
import base64
import pickle
import random
import string
import asyncio
import gspread
import objects
import _thread
import requests
from SQL import SQL
from copy import copy
from io import BytesIO
from time import sleep
from GDrive import Drive
from typing import Union
from aiogram import types
from chrome import chrome
from telegraph import upload
from bs4 import BeautifulSoup
from aiogram.utils import executor
from db.emoji_gen import emojis_path
from PIL.ImageFont import FreeTypeFont
from aiogram.dispatcher import Dispatcher
from PIL import Image, ImageFont, ImageDraw
from selenium.webdriver.common.by import By
from statistics import median as median_function
from datetime import datetime, timezone, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from objects import code, html_link, html_secure, time_now
from selenium.webdriver.support import expected_conditions as ec
# =================================================================================================================
stamp1 = time_now()


def query(link: str, regex: str):
    soup = BeautifulSoup(requests.get(f'{link}?embed=1').text, 'html.parser')
    if soup.find('div', class_='tgme_widget_message_error') is None:
        raw = str(soup.find('div', class_='tgme_widget_message_text js-message_text')).replace('<br/>', '\n')
        return re.search(regex, BeautifulSoup(raw, 'html.parser').get_text(), flags=re.DOTALL)


def get_fonts():
    paths = {}
    for path in os.listdir('fonts'):
        search = re.search(r'(.*?)-(.*)\.ttf', path)
        if search:
            paths[search.group(1)] = paths.get(search.group(1), {})
            paths[search.group(1)][search.group(2)] = f'fonts/{path}'
    return paths


objects.environmental_files()
vars_post_id = os.environ['post']
vars_link = f'https://t.me/UsefullCWLinks/{vars_post_id}'
vars_search = query(vars_link, 'ID = (.*?) = ID.> (.*?) <.block = (.*?) = block')
worksheet = gspread.service_account('person2.json').open('growing').worksheet('main')
channels = {'main': -1001404073893, 'tiktok': -1001498374657, 'instagram': -1001186786378}
#channels = {'main': 396978030, 'tiktok': 396978030, 'instagram': 396978030}
tz, admins, font_paths, unused_links = timezone(timedelta(hours=3)), [396978030, 470292601], get_fonts(), []
Auth = objects.AuthCentre(ID_DEV=-1001312302092, TOKEN=os.environ['TOKEN'], DEV_TOKEN=os.environ['DEV_TOKEN'])
#Auth = objects.AuthCentre(ID_DEV=396978030, TOKEN=os.environ['TOKEN'], DEV_TOKEN=os.environ['DEV_TOKEN'])

block = vars_search.group(3) if vars_search else None
next_post_id = int(vars_search.group(1)) if vars_search else None
used_links, inst_username, google_folder_id = worksheet.col_values(1), None, None
bot, drive, dispatcher = Auth.async_bot, Drive('person2.json'), Dispatcher(Auth.async_bot)
last_date = datetime.fromisoformat(f'{vars_search.group(2)}+03:00') if vars_search else None
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


def font(size: int, family: str = 'OpenSans', weight: str = 'Regular'):
    font_type = font_paths.get(family, font_paths.get('OpenSans'))
    return ImageFont.truetype(font_type.get(weight, font_type.get('Regular')), size)


def width(text: str, size: int, family: str = 'OpenSans', weight: str = 'Regular'):
    emojis = emoji.emoji_list(text)
    emoji_size = size + (size * 0.4)
    indent = int(emoji_size + emoji_size * 0.11) * len(emojis)
    text = emoji.replace_emoji(text, replace='') if emojis else text
    return FreeTypeFont.getbbox(font(size, family, weight), text)[2] + indent


def google(link):
    global worksheet
    try:
        worksheet.insert_row([link], 1)
    except IndexError and Exception:
        worksheet = gspread.service_account('person2.json').open('growing').worksheet('main')
        worksheet.insert_row([link], 1)


def min_height(text: str, size: int, family: str = 'OpenSans', weight: str = 'Regular'):
    letter_heights = [FreeTypeFont.getbbox(font(size, family, weight), i, anchor='lt')[3] for i in list(text)]
    descender_heights = [FreeTypeFont.getbbox(font(size, family, weight), i, anchor='ls')[3] for i in list(text)]
    result = [element1 - element2 for (element1, element2) in zip(letter_heights, descender_heights)]
    if emoji.emoji_list(text):
        return max(result)
    return median_function(result) if result else 0


def height(text: str, size: int, family: str = 'OpenSans', weight: str = 'Regular'):
    emoji_size = size + (size * 0.4)
    response = int(emoji_size - emoji_size * 0.22) if emoji.emoji_list(text) else None
    if response is None:
        result = [FreeTypeFont.getbbox(font(size, family, weight), text, anchor=anchor)[3] for anchor in ['lt', 'ls']]
        response = result[0] - result[1]
    return response


def edit_vars():
    last_date_iso = re.sub(r'\+.*', '', last_date.isoformat(' ', 'seconds'))
    text = f"{code('Последний пост на канале с вакансиями')}\n" \
           f"{bold('ID =')} {next_post_id} {bold('= ID')}\n" \
           f"{bold('&#62;')} {code(last_date_iso)} {bold('&#60;')}\n" \
           f"{bold('block =')} {block} {bold('= block')}"
    try:
        Auth.bot.edit_message_text(text, -1001471643258, vars_post_id, parse_mode='HTML')
    except IndexError and Exception as error:
        Auth.dev.message(text=f"{bold('Проблема с изменением переменных на канале')} "
                              f"{vars_link}\n\n{html_secure(text)}\n{html_secure(error)}")


def inst_handler(data: dict):
    array = [bold(f"👨🏻‍💻 {data['title']}", md=True)] if data.get('title') else []
    array.append(f"🏙 {data['place']}") if data.get('place') else None
    array.append(f"🏅 Опыт работы ➡ {data['experience']}") if data.get('experience') else None
    array.append(f"👨🏻‍🎓 Образование ➡ {data['education']}") if data.get('education') else None
    array.append(bold(f"💸 З/П {data['money']} руб.", md=True)) if data.get('money') else None
    array.append(f"\n{bold('📘 Контакты', md=True)}")
    for key in ['org_name', 'contact', 'numbers']:
        array.append(data[key]) if data.get(key) else None
    array.append(f"{data['email']} ➡ Резюме") if data.get('email') else None
    if data.get('email') is None and data.get('numbers') is None:
        array.append(bold('🔋 Источник в нашем telegram канале ➡ Ссылка в профиле', md=True))
    array.append(f"🚇 {data['underground']}") if data.get('underground') else None
    return '\n'.join(array)


def checker(address: str, main_class: str, link_class: str, parser):
    global used_links, unused_links
    sleep(3)
    now, links = datetime.now(tz), []
    soup = BeautifulSoup(requests.get(address, headers=headers).text, 'html.parser')
    for link_div in soup.find_all('div', attrs={'class': main_class}):
        link = link_div.find('a', attrs={'class': link_class})
        links.append(link.get('href')) if link else None
    for link in links:
        if link not in used_links and link not in unused_links and (11 <= int(now.strftime('%H')) < 21):
            if (last_date + timedelta(hours=2)) < now and block != 'True':
                google(link)
                used_links.insert(0, link)
                poster(parser(link))
                Auth.dev.printer(f'{link} сделано')
                sleep(3)
            else:
                unused_links.append(link)


def image(text: str, return_link=False,
          background: Union[Image.open, Image.new] = None,
          font_size: int = 300, font_family: str = 'OpenSans', font_weight: str = 'Regular',
          original_width: int = 1000, original_height: int = 1000, text_align: str = 'center',
          left_indent: int = 50, top_indent: int = 50, left_indent_2: int = 0, top_indent_2: int = 0,
          text_color: tuple[int, int, int] = (0, 0, 0), background_color: tuple[int, int, int] = (256, 256, 256)):
    file_name = f"{''.join(random.sample(string.ascii_letters, 10))}.jpg"
    mask, family, spacing, response, coefficient, modal_height = None, font_family, 0, None, 0.6, 0
    original_width = background.getbbox()[2] if background and original_width == 1000 else original_width
    original_height = background.getbbox()[3] if background and original_height == 1000 else original_height
    db, original_scale = SQL(emojis_path), (original_width, original_height)
    original_height -= top_indent * 2 + top_indent_2
    original_width -= left_indent * 2 + left_indent_2
    size = font_size if font_size != 300 else original_width // 3
    background = copy(background) or Image.new('RGB', original_scale, background_color)
    while spacing < modal_height * coefficient or spacing == 0:
        skip, layers, heights, weights = False, [], [], []
        mask = Image.new('RGBA', original_scale, (0, 0, 0, 0))
        for line in text.strip().split('\n'):
            line_weight, layer_array = font_weight, []
            if line.startswith('**') and line.endswith('**'):
                line_weight, line = 'Bold', line.strip('**')
            if line.startswith('__') and line.endswith('__'):
                line_weight, line = 'Italic', line.strip('__')
            if line:
                for word in re.sub(r'\s+', ' ', line).strip().split(' '):
                    if width(word, size, family, line_weight) > original_width:
                        skip = True
                        break
                    if width(' '.join(layer_array + [word]), size, family, line_weight) > original_width:
                        weights.append(line_weight), layers.append(' '.join(layer_array))
                        heights.append(height(' '.join(layer_array), size, family, line_weight))
                        layer_array = [word]
                    else:
                        layer_array.append(word)
                else:
                    weights.append(line_weight), layers.append(' '.join(layer_array))
                    heights.append(height(' '.join(layer_array), size, family, line_weight))
            else:
                layers.append(''), heights.append(0), weights.append(line_weight)

        if skip:
            size -= 1
            continue

        layers_count = len(layers) - 1 if len(layers) > 1 else 1
        full_height = heights[0] - min_height(layers[0], size, family, weights[0])
        modal_height = max(heights) if emoji.emoji_list(text) else median_function(heights)
        full_height += sum([min_height(layers[i], size, family, weights[i]) for i in range(0, len(layers))])
        draw, aligner, emoji_size, additional_height = copy(ImageDraw.Draw(mask)), 0, size + (size * 0.4), 0
        spacing = (original_height - full_height) // layers_count
        if spacing > modal_height * coefficient:
            spacing = modal_height * coefficient
            aligner = (original_height - full_height - (spacing if len(layers) > 1 else 0) * layers_count) // 2
        for i in range(0, len(layers)):
            left = left_indent + left_indent_2
            emojis = [e['emoji'] for e in emoji.emoji_list(layers[i])]
            modded = (heights[i] - min_height(layers[i], size, family, weights[i]))
            chunks = [re.sub('&#124;', '|', i) for i in emoji.replace_emoji(layers[i], replace='|').split('|')]
            modded = modded if i != 0 or (i == 0 and layers_count == 0) else 0
            top = top_indent + top_indent_2 + aligner + additional_height - modded
            additional_height += heights[i] - modded + spacing
            if text_align == 'center':
                left += (original_width - width(layers[i], size, family, weights[i])) // 2

            for c in range(0, len(chunks)):
                chunk_width = width(chunks[c], size, family, weights[i])
                emoji_scale = (left + chunk_width + int(emoji_size * 0.055), int(top))
                text_scale = (left, top + heights[i] - height(chunks[c], size, family, weights[i]))
                draw.text(text_scale, chunks[c], text_color, font(size, family, weights[i]), anchor='lt')
                if c < len(emojis):
                    emoji_record = db.get_emoji(emojis[c])
                    if emoji_record:
                        emoji_image = BytesIO(base64.b64decode(emoji_record['data']))
                        foreground = Image.open(emoji_image).resize((int(emoji_size), int(emoji_size)), 3)
                    else:
                        foreground = Image.new('RGBA', (int(emoji_size), int(emoji_size)), (0, 0, 0, 1000))
                    try:
                        mask.paste(foreground, emoji_scale, foreground)
                    except IndexError and Exception:
                        mask.paste(foreground, emoji_scale)
                left += chunk_width + int(emoji_size + emoji_size * 0.11)
        size -= 1
    db.close()
    if mask:
        background.paste(mask, (0, 0), mask)
        background.save(file_name)
        if return_link:
            with open(file_name, 'rb') as file:
                response = f'https://telegra.ph{upload.upload_file(file)[0]}'
            os.remove(file_name)
        else:
            return file_name
    return response


def tg_handler(data: dict):
    logo = Image.open('logo.png')
    picture = image(text=data.get('title', 'Sample'), return_link=True, background=logo,
                    original_width=logo.getbbox()[2], original_height=logo.getbbox()[3],
                    font_family='Roboto', font_weight='Condensed', top_indent=100, top_indent_2=150)
    if any(data.get(key) is None for key in ['money', 'title', 'short_place']):
        return {'text': None, 'image': picture}
    elif re.search('водитель|яндекс|такси|уборщи', data['title'].lower()):
        return {'text': None, 'image': picture}
    elif data.get('org_name') and re.search('доброном', data['org_name'].lower()):
        return {'text': None, 'image': picture}
    elif data.get('experience') and re.search('6', data['experience']):
        return {'text': None, 'image': picture}
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
    text += f'\n🆔 {italic(next_post_id)}'
    text += f"\n{italic('💼ТЕГИ:')} #{' #'.join(data['tags'])}\n" if data.get('tags') else ''
    return {'text': text, 'image': picture}


def poster(data: dict):
    global last_date, next_post_id
    tg = tg_handler(data)
    if tg.get('text'):
        message = Auth.bot.send_message(channels['main'], tg['text'], parse_mode='HTML')
        next_post_id = message.message_id + 1
        message_date = datetime.fromtimestamp(message.date, tz)
        inst_path = image(inst_handler(data) or 'Sample', text_align='left', font_family='Roboto',
                          background_color=(254, 230, 68), original_width=1080, original_height=1080)
        tt_path = image(inst_handler(data) or 'Sample', text_align='left', font_family='Roboto',
                        background_color=(254, 230, 68), original_width=1080, original_height=1920)
        for path, channel in [(inst_path, 'instagram'), (tt_path, 'tiktok')]:
            with open(path, 'rb') as picture:
                Auth.bot.send_photo(channels[channel], picture)
            with open(path, 'rb') as picture:
                Auth.bot.send_document(channels[channel], picture)
            os.remove(path)
        if last_date < message_date:
            last_date = message_date
            edit_vars()
    else:
        text = f"{html_link(tg['image'], '​​') if tg.get('image') else ''}️Что-то пошло не так: &#123;\n"
        for key, value in data.items():
            selected = ['link', 'money', 'title', 'short_place']
            text += f"{' ' * 6}{objects.under(bold(key)) if key in selected else key}: {html_secure(value)}\n"
        Auth.bot.send_message(admins[0], f'{text}&#125;', parse_mode='HTML')


def inst_poster(username: str, description: str, image_path: str):
    driver = chrome(os.environ.get('local'))
    driver.set_window_size(500, 1200)
    driver.get(f'https://www.instagram.com/')
    input_xpath = "//input[@accept='image/jpeg,image/png,image/heic,image/heif,video/mp4,video/quicktime']"
    for cookie in pickle.load(open('cookies.pkl', 'rb')):
        driver.add_cookie(cookie)
    driver.get(f'https://www.instagram.com/{username}/')
    driver.find_element(By.TAG_NAME, 'nav').find_elements(By.TAG_NAME, 'svg')[3].click()
    WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, "//div[@role='dialog']")))
    driver.find_element(By.XPATH, input_xpath).send_keys(f'{os.getcwd()}/{image_path}')
    WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, "//div[@role='dialog']")))
    div = driver.find_element(By.XPATH, "//div[@role='dialog']")
    div.find_elements(By.TAG_NAME, 'button')[1].click()
    WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, "//div[@role='tablist']")))
    div.find_elements(By.TAG_NAME, 'button')[1].click()
    WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.TAG_NAME, 'textarea')))
    driver.find_element(By.TAG_NAME, 'textarea').send_keys(description)
    div.find_elements(By.TAG_NAME, 'button')[1].click()
    title = driver.find_element(By.XPATH, "//div[@role='dialog']").get_attribute('aria-label')
    while title == driver.find_element(By.XPATH, "//div[@role='dialog']").get_attribute('aria-label'):
        sleep(1)
    for div in driver.find_elements(By.XPATH, "//div[@role='presentation' and not(@tabindex='-1')]"):
        div.find_element(By.TAG_NAME, 'button').click() if div.find_elements(By.TAG_NAME, 'button') else None
    link = driver.find_element(By.TAG_NAME, 'article').find_element(By.TAG_NAME, 'a').get_attribute('href')
    driver.close()
    return link


def prc_parser(link: str):
    data = {'link': link}
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
    data['tags'] = [re.sub('_/_', ' #', re.sub(r'[\s_—-]+', '_', tag.get_text())).strip() for tag in tags]

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
    global next_post_id
    try:
        if message['chat']['id'] == channels['main'] and message['message_id'] + 1 > next_post_id:
            await asyncio.sleep(60)
            if message['message_id'] + 1 > next_post_id:
                next_post_id = message['message_id'] + 1
                edit_vars()
    except IndexError and Exception:
        await Auth.dev.async_except(message)


@dispatcher.message_handler()
async def repeat_all_messages(message: types.Message):
    global block
    try:
        if message['chat']['id'] in admins:
            if message['text'].lower().startswith(('/enable', '/disable')):
                if message['text'].lower().startswith('/disable'):
                    text, new_block = f"Посты на канале {bold('не')} публикуются", 'True'
                else:
                    text, new_block = 'Посты на канале публикуются в штатном режиме', 'False'
                if block != new_block:
                    block = new_block
                    edit_vars()
                await bot.send_message(message['chat']['id'], text, parse_mode='HTML')

            elif message['text'].lower().startswith('/test'):
                inst_text = 'Все вакансии и удобный поиск по ним, а также вся контактная информация в нашем ' \
                            'Telegram канале (ссылка в шапке профиля). #работа_в_минске #Вакансии_Минск ' \
                            '#удаленная_работа_по_всей_беларуси #работа #вакансии_в_минске #работа_РБ ' \
                            '#вакансии #удаленная_работа'
                data = prc_parser('https://praca.by/vacancy/460578/')
                inst_path = image(inst_handler(data) or 'Sample', text_align='left', font_family='Roboto',
                                  background_color=(254, 230, 68), original_width=1080, original_height=1080)
                inst_poster(inst_username, inst_text, inst_path)
                os.remove(inst_path)
                await bot.send_message(message['chat']['id'], 'все ок', parse_mode='HTML')

            elif message['text'].lower().startswith('/reboot'):
                text, _ = Auth.logs.reboot()
                await bot.send_message(message['chat']['id'], text, parse_mode='HTML')

            elif message['text'].lower().startswith('/pic'):
                subbed = re.sub('/pic', '', message['text']).strip()
                await bot.send_message(message['chat']['id'], image(subbed), parse_mode='HTML')
    except IndexError and Exception:
        await Auth.dev.async_except(message)


def prc_checker():
    while True:
        try:
            checker(parser=prc_parser, address='https://praca.by/search/vacancies/',
                    link_class='vac-small__title-link', main_class='vac-small__column vac-small__column_2')
        except IndexError and Exception:
            Auth.dev.thread_except()


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


def start(stamp):
    try:
        if os.environ.get('local'):
            threads = []
            Auth.dev.printer(f'Запуск бота локально за {time_now() - stamp} сек.')
        else:
            threads = [prc_checker, auto_reboot] if vars_search and inst_username else []
            alert = '' if vars_search and inst_username else f"\n{bold('Скрипты не запущены')}"
            Auth.dev.start(stamp, alert)
            Auth.dev.printer(f'Бот запущен за {time_now() - stamp} сек.')

        for thread_element in threads:
            _thread.start_new_thread(thread_element, ())
        executor.start_polling(dispatcher, allowed_updates=objects.allowed_updates)
    except IndexError and Exception:
        Auth.dev.thread_except()


if os.environ.get('local'):
    start(stamp1)
