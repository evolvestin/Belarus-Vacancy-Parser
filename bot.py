import re
import sys
import tkn
import time
import _thread
import gspread
import telebot
import requests
import calendar
import traceback
import unicodedata
from time import sleep
from telebot import types
from telegraph import upload
from bs4 import BeautifulSoup
from datetime import datetime
from unidecode import unidecode
from collections import defaultdict
from PIL import Image, ImageFont, ImageDraw
from oauth2client.service_account import ServiceAccountCredentials

stamp1 = int(datetime.now().timestamp())
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds2 = ServiceAccountCredentials.from_json_keyfile_name('person2.json', scope)
client2 = gspread.authorize(creds2)
used = client2.open('growing').worksheet('main')
used_array = used.col_values(1)

keyboard = types.InlineKeyboardMarkup(row_width=2)
buttons = [types.InlineKeyboardButton(text='✅', callback_data='post'),
           types.InlineKeyboardButton(text='👀', callback_data='viewed')]
starting = ['title', 'place', 'tags', 'geo', 'money', 'org_name', 'schedule', 'employment', 'short_place',
            'experience', 'education', 'contact', 'numbers', 'description', 'email', 'metro', 'tag_picture']
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36'
                         ' (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}
emoji_list = '([💻🏙🏅🎓💸📔🚇💼🔋])'
emoji = {
    '💻': Image.open('emoji/comp.png'),
    '🏙': Image.open('emoji/city.png'),
    '🏅': Image.open('emoji/star.png'),
    '🎓': Image.open('emoji/edu.png'),
    '💸': Image.open('emoji/money.png'),
    '📔': Image.open('emoji/note.png'),
    '🚇': Image.open('emoji/metro.png'),
    '💼': Image.open('emoji/case.png'),
    '➡': Image.open('emoji/arrow.png'),
    '🔋': Image.open('emoji/empty.png')
}

unused_box = []
idMe = 396978030
color = (0, 0, 0)
idAndre = 470292601
idMain = tkn.idMain
idJobi = tkn.idJobi
idInstagram = tkn.idInstagram
keyboard.add(*buttons)
# =================================================================


def bold(txt):
    return '<b>' + str(txt) + '</b>'


def code(txt):
    return '<code>' + str(txt) + '</code>'


def italic(txt):
    return '<i>' + str(txt) + '</i>'


def under(txt):
    return '<u>' + str(txt) + '</u>'


def stamper(date):
    stack = int(calendar.timegm(time.strptime(date, '%d/%m/%Y %H:%M:%S')))
    return stack


def printer(printer_text):
    thread_name = str(thread_array[_thread.get_ident()]['name'])
    logfile = open('log.txt', 'a')
    log_print_text = thread_name + ' [' + str(_thread.get_ident()) + '] ' + printer_text
    logfile.write('\n' + re.sub('<.*?>', '', logtime(0)) + log_print_text)
    logfile.close()
    print(log_print_text)


def send_json(raw, name, error):
    json_text = ''
    if type(raw) is str:
        for character in raw:
            replaced = unidecode(str(character))
            if replaced != '':
                json_text += replaced
            else:
                try:
                    json_text += '[' + unicodedata.name(character) + ']'
                except ValueError:
                    json_text += '[???]'
    if len(error) <= 1000:
        if json_text != '':
            docw = open(name + '.json', 'w')
            docw.write(json_text)
            docw.close()
            doc = open(name + '.json', 'rb')
            bot.send_document(idMe, doc, caption=error)
            doc.close()
        else:
            bot.send_message(idMe, error, parse_mode='HTML')
    if 1000 < len(error) <= 4000:
        bot.send_message(idMe, error)
    if len(error) > 4000:
        separator = 4000
        splited_sep = len(error) // separator
        splited_mod = len(error) / separator - len(error) // separator
        if splited_mod != 0:
            splited_sep += 1
        for i in range(0, splited_sep):
            splited_error = error[i * separator:(i + 1) * separator]
            if len(splited_error) > 0:
                bot.send_message(idMe, splited_error, parse_mode='HTML')


def executive(new, logs):
    search = re.search('<function (\S+)', str(new))
    if search:
        function_name = search.group(1)
    else:
        function_name = 'None'
    exc_type, exc_value, exc_traceback = sys.exc_info()
    error_raw = traceback.format_exception(exc_type, exc_value, exc_traceback)
    error = 'Вылет ' + function_name + '\n'
    for i in error_raw:
        error += re.sub('<', '&#60;', str(i))
    send_json(logs, function_name, error)
    if logs == 0:
        sleep(100)
        thread_index = _thread.start_new_thread(new, ())
        thread_array[thread_index] = defaultdict(dict)
        bot.send_message(idMe, 'Запущен ' + bold(function_name), parse_mode='HTML')
        sleep(30)
        _thread.exit()


def logtime(stamp):
    if stamp == 0:
        stamp = int(datetime.now().timestamp())
    weekday = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%a')
    if weekday == 'Mon':
        weekday = 'Пн'
    elif weekday == 'Tue':
        weekday = 'Вт'
    elif weekday == 'Wed':
        weekday = 'Ср'
    elif weekday == 'Thu':
        weekday = 'Чт'
    elif weekday == 'Fri':
        weekday = 'Пт'
    elif weekday == 'Sat':
        weekday = 'Сб'
    elif weekday == 'Sun':
        weekday = 'Вс'
    day = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%d')
    month = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%m')
    year = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%Y')
    hours = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%H')
    minutes = datetime.utcfromtimestamp(int(stamp)).strftime('%M')
    seconds = datetime.utcfromtimestamp(int(stamp)).strftime('%S')
    data = code(str(weekday) + ' ' + str(day) + '.' + str(month) + '.' + str(year) +
                ' ' + str(hours) + ':' + str(minutes) + ':' + str(seconds)) + ' '
    return data


bot = telebot.TeleBot(tkn.tkn)
logfile_start = open('log.txt', 'w')
logfile_start.write('Начало записи лога ' + re.sub('<.*?>', '', logtime(0)))
logfile_start.close()

start_text = requests.get('https://t.me/UsefullCWLinks/' + str(tkn.start_link) + '?embed=1')
start = BeautifulSoup(start_text.text, 'html.parser')
start = str(start.find('div', class_='tgme_widget_message_text js-message_text'))
start = re.sub('(<b>|</b>|<code>|</code>|</div>)', '', start)
start_search = re.search('<br/>d: (.*) :d', start)

if start_search:
    last_date = stamper(start_search.group(1)) - 3 * 60 * 60
    start_message = bot.send_message(idMe, logtime(stamp1) + '\n' + logtime(0), parse_mode='HTML')
else:
    last_date = '\nОшибка с нахождением номера поста. ' + bold('Бот выключен')
    start_message = bot.send_message(idMe, logtime(stamp1) + '\n' + logtime(0) + last_date, parse_mode='HTML')
    _thread.exit()
# ====================================================================================


def timer(stack):
    if stack == 0:
        stack = int(datetime.now().timestamp())
    day = datetime.utcfromtimestamp(int(stack)).strftime('%d')
    month = datetime.utcfromtimestamp(int(stack)).strftime('%m')
    years = datetime.utcfromtimestamp(int(stack)).strftime('%Y')
    hours = datetime.utcfromtimestamp(int(stack)).strftime('%H')
    minutes = datetime.utcfromtimestamp(int(stack)).strftime('%M')
    seconds = datetime.utcfromtimestamp(int(stack)).strftime('%S')
    text = str(day) + '/' + str(month) + '/' + str(years) + ' ' + str(hours) + ':' + str(minutes) + ':' + str(seconds)
    return text


def hour():
    stack = int(datetime.now().timestamp())
    return int(datetime.utcfromtimestamp(int(stack) + 3 * 60 * 60).strftime('%H'))


def fonts(font_weight, font_size):
    if font_weight == 'regular':
        return ImageFont.truetype('fonts/Roboto-Regular.ttf', font_size)
    elif font_weight == 'bold':
        return ImageFont.truetype('fonts/Roboto-Bold.ttf', font_size)
    else:
        return ImageFont.truetype('fonts/RobotoCondensed-Bold.ttf', font_size)


def height_indent(row_text, font_weight, font_size):
    size = ImageFont.ImageFont.getsize(fonts(font_weight, font_size), row_text)
    text_height = size[1][1]
    return text_height


def width(emoji_parameter, row_text, font_weight, font_size):
    family = fonts(font_weight, font_size)
    if emoji_parameter:
        for f in emoji_parameter:
            if f in ['💻', '💸', '📔', '🔋']:
                family = fonts('bold', font_size)
    size = ImageFont.ImageFont.getsize(family, row_text)
    text_width = size[0][0]
    return text_width


def height(emoji_parameter, row_text, font_weight, font_size):
    family = fonts(font_weight, font_size)
    if emoji_parameter:
        for f in emoji_parameter:
            if f in ['💻', '💸', '📔', '🔋']:
                family = fonts('bold', font_size)
    size = ImageFont.ImageFont.getsize(family, row_text)
    text_height = size[0][1]
    return text_height


def search_emoji(text):
    search = re.search(emoji_list, text)
    if search:
        array = [[search.group(1)]]
    else:
        array = [False]
    if '➡' in text:
        if array[0]:
            array[0].append('➡')
        else:
            array[0] = ['➡']
    array.append(re.sub(emoji_list, '', text))
    return array


def instagram_former(growing):
    for i in growing:
        if str(type(growing.get(i))) == "<class 'str'>":
            growing[i] = re.sub('➡', '—', growing.get(i))
    array = []
    if growing['title'] != 'none':
        array.append('💻' + growing['title'])
    if growing['place'] != 'none':
        array.append('🏙' + growing['place'])
    if growing['experience'] != 'none':
        array.append('🏅Опыт работы ➡ ' + growing['experience'])
    if growing['education'] != 'none':
        array.append('🎓Образование ➡ ' + growing['education'])
    if growing['money'] != 'none':
        more = ''
        if growing['money'][1] != 'none':
            more += '+'
        array.append('💸З/П ' + growing['money'][0] + more + ' руб.')
    array.append(' ')
    array.append('📔Контакты')
    if growing['org_name'] != 'none':
        array.append(growing['org_name'])
    if growing['contact'] != 'none':
        array.append(growing['contact'])
    if growing['numbers'] != 'none':
        numbers = growing['numbers'].split('\n')
        array.append(numbers[0])
    if growing['email'] != 'none':
        array.append(growing['email'] + ' ➡ Резюме')
    if growing['email'] == 'none' and growing['numbers'] == 'none':
        array.append('🔋Источник в нашем telegram канале ➡ Ссылка в профиле')
    if growing['metro'] != 'none':
        array.append('🚇' + growing['metro'])
    return array


def image(image_text):
    img = Image.open('logo.jpg')
    draw = ImageDraw.Draw(img)
    original_width = 1100
    original_height = 310
    left = 50
    if width(None, image_text, 'condensed', 100) <= original_width:
        more_font = 200
        while width(None, image_text, 'condensed', more_font) > original_width:
            more_font -= 1
        left += (original_width - width(None, image_text, 'condensed', more_font)) // 2
        top = 200 - height_indent(image_text, 'condensed', more_font)
        top += (original_height - height(None, image_text, 'condensed', more_font)) // 2
        draw.text((left, top), image_text, color, fonts('condensed', more_font))
    else:
        layer = 1
        drop_text = ''
        layer_array = []
        full_height = 0
        temp_text_array = re.sub('\s+', ' ', image_text.strip()).split(' ')
        for i in range(0, len(temp_text_array)):
            if width(None, temp_text_array[i], 'condensed', 100) <= original_width:
                if width(None, (drop_text + ' ' + temp_text_array[i]).strip(), 'condensed', 100) <= original_width:
                    drop_text = (drop_text + ' ' + temp_text_array[i]).strip()
                else:
                    if drop_text != '' and len(layer_array) < 3:
                        layer_array.append(drop_text)
                        full_height += height(None, drop_text, 'condensed', 100)
                    drop_text = ''
                    drop_text = (drop_text + ' ' + temp_text_array[i]).strip()
                if i == len(temp_text_array) - 1:
                    if drop_text != '' and len(layer_array) < 3:
                        layer_array.append(drop_text)
                        full_height += height(None, drop_text, 'condensed', 100)
        additional_height = 0
        indent_height = int(full_height / len(layer_array) + 0.15 * (full_height / len(layer_array)))
        mod = int((original_height - len(layer_array) * indent_height) / 2)
        for i in layer_array:
            text_position = (left + (original_width - width(None, i, 'condensed', 100)) // 2,
                             200 + mod + additional_height)
            additional_height += indent_height
            draw.text(text_position, i, color, fonts('condensed', 100))
            layer += 1
    img.save('bot_edited.jpg')
    doc = open('bot_edited.jpg', 'rb')
    uploaded = upload.upload_file(doc)
    uploaded_link = '<a href="https://telegra.ph' + uploaded[0] + '">​​</a>️'
    doc.close()
    return uploaded_link


def instagram_image(text_array):
    background = Image.new('RGB', (1080, 1080), (254, 230, 68))
    img = Image.new('RGBA', (1080, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    original_height = 980
    original_width = 980
    layer_array = []
    more_font = 200
    height_coefficient = False
    while height_coefficient is False:
        while len(layer_array) != len(text_array):
            for t in text_array:
                array = search_emoji(t)
                emoji_factor = 0
                if array[0]:
                    emoji_factor += int(more_font + more_font * 0.35) * len(array[0])
                if width(array[0], array[1], 'regular', more_font) + emoji_factor <= original_width:
                    layer_array.append(array)
                else:
                    temp_text_array = re.sub('\s+', ' ', array[1]).split(' ')
                    array = [array[0]]
                    drop_text = ''
                    for i in range(0, len(temp_text_array)):
                        if width(array[0], (drop_text + ' ' + temp_text_array[i]).strip(), 'regular', more_font) \
                                + emoji_factor <= original_width:
                            drop_text = (drop_text + ' ' + temp_text_array[i]).strip()
                        else:
                            if drop_text != '' and len(array) < 3:
                                array.append(drop_text)
                            else:
                                break
                            drop_text = temp_text_array[i]
                        if i == len(temp_text_array) - 1:
                            if drop_text != '' and len(array) < 3:
                                array.append(drop_text)
                                layer_array.append(array)
                            else:
                                break
            if len(layer_array) != len(text_array):
                more_font -= 1
                layer_array.clear()
        layer_count = 0
        additional_height = 0
        for i in layer_array:
            layer_count += len(i) - 1
        indent_height = int(more_font + 0.15 * more_font)
        if layer_count * indent_height <= original_height:
            mod = 50 + int((original_height - layer_count * indent_height) / 2)
            pic = mod + int(0.1 * more_font)
            previous_arrow_array = None
            for array in layer_array:
                for i in array:
                    if array.index(i) != 0:
                        left = 0
                        arrow_split = False
                        family = fonts('regular', more_font)
                        if array[0]:
                            for f in array[0]:
                                if f in ['💻', '💸', '📔', '🔋']:
                                    family = fonts('bold', more_font)
                                if f in ['💻', '🏙', '🏅', '🎓', '💸', '📔', '🚇', '💼', '🔋']:
                                    left += int(more_font + more_font * 0.35)
                                    if array.index(i) == 1:
                                        foreground = emoji[f].resize((more_font, more_font), Image.ANTIALIAS)
                                        background.paste(foreground, (50, pic + additional_height), foreground)
                                if f == '➡':
                                    arrow_split = True
                        if arrow_split is False:
                            text_position = (50 + left, mod + additional_height)
                            draw.text(text_position, i, color, family)
                        else:
                            text = i
                            arrow_indent = 50 + left
                            arrow_array = i.split('➡')
                            foreground = emoji['➡'].resize((more_font, more_font), Image.ANTIALIAS)
                            if len(arrow_array) > 1:
                                text = arrow_array[1]
                                previous_arrow_array = arrow_array
                                text_position = (arrow_indent, mod + additional_height)
                                arrow_indent += width(array[0], arrow_array[0], 'regular', more_font)
                                draw.text(text_position, arrow_array[0], color, family)
                                if text != '':
                                    background.paste(foreground, (arrow_indent, pic + additional_height), foreground)
                            if len(arrow_array) == 1 and previous_arrow_array:
                                if previous_arrow_array[0] == '' and previous_arrow_array[1] == '':
                                    background.paste(foreground, (arrow_indent, pic + additional_height), foreground)
                                    previous_arrow_array = None
                                elif previous_arrow_array[1] == '':
                                    background.paste(foreground, (arrow_indent, pic + additional_height), foreground)
                                    arrow_indent += int(more_font * 0.35)
                                    previous_arrow_array = None
                                else:
                                    arrow_indent -= more_font
                            text_position = (arrow_indent + more_font, mod + additional_height)
                            draw.text(text_position, text, color, family)
                        additional_height += indent_height
            height_coefficient = True
        else:
            more_font -= 1
            layer_array.clear()

    background.paste(img, (0, 0), img)
    background.save('bot_edited.png')
    doc = open('bot_edited.png', 'rb')
    bot.send_photo(idInstagram, doc)
    doc = open('bot_edited.png', 'rb')
    bot.send_document(idInstagram, doc)


def praca_quest(link):
    pub_link = link
    req = requests.get(link)
    soup = BeautifulSoup(req.text, 'html.parser')

    growing = {}
    for i in starting:
        growing[i] = 'none'

    if soup.find('span', class_='hidden-vac-contact') is not None:
        link += '?token=wykzQ7x5oq6kZWG7naOvHprT4vcZ1vdFFUSXoOfmKR10pPWq0ox5acYvr3wcfg00'
        req = requests.get(link)
        soup = BeautifulSoup(req.text, 'html.parser')

    title = soup.find('h1', class_='vacancy__title')
    if title is not None:
        growing['title'] = title.get_text().strip()

    place = soup.find('div', class_='job-address')
    if place is not None:
        growing['place'] = re.sub('\s+', ' ', place.get_text().strip())

    short_place = soup.find('div', class_='vacancy__city')
    if short_place is not None:
        growing['short_place'] = re.sub('\s+', ' ', short_place.get_text().strip())

    tag_list = soup.find('div', class_='categories')
    if tag_list is not None:
        tags = tag_list.find_all('a')
        tag_array = []
        for i in tags:
            tag = re.sub('[\s-]', '_', i.get_text())
            tag_array.append(re.sub('_/_', ' #', tag))
        growing['tags'] = tag_array

    geo_search = re.search('{"latitude":"(.*?)","longitude":"(.*?)","zoom"', str(soup))
    if geo_search:
        growing['geo'] = re.sub('\s', '', geo_search.group(1)) + ',' + re.sub('\s', '', geo_search.group(2))

    metro = soup.find('div', class_='vacancy__metro')
    if metro is not None:
        metro_array = metro.find_all('span', class_='nowrap')
        metro = ''
        for i in metro_array:
            metro += re.sub('\s+', ' ', i.get_text().capitalize().strip() + ', ')
        growing['metro'] = metro[:-2]

    money = soup.find('div', class_='vacancy__salary')
    if money is not None:
        money = re.sub('\s', '', money.get_text())
        search_gold = re.search('(\d+)', money)
        search = re.search('ивыше', money)
        money_array = []
        more = 'none'
        if search_gold:
            money_array.append(search_gold.group(1))
        if search:
            more = 'more'
        money_array.append(more)
        growing['money'] = money_array

    org_name = soup.find('div', class_='org-info__item org-info__name')
    if org_name is not None:
        growing['org_name'] = re.sub('\s+', ' ', org_name.find('a').get_text().strip())

    items = soup.find_all('div', class_='vacancy__item')
    for i in items:
        schedule = i.find('i', class_='pri-schedule')
        if schedule is not None:
            schedule = i.find('div', class_='vacancy__desc').get_text().strip()
            growing['schedule'] = re.sub('\s+', ' ', schedule)

        employment = i.find('i', class_='pri-employment')
        if employment is not None:
            employment = i.find('div', class_='vacancy__desc').get_text().strip()
            growing['employment'] = re.sub('\s+', ' ', employment)

        experience = i.find('p', class_='vacancy__experience')
        if experience is not None:
            experience = re.sub('Опыт работы', '', experience.get_text())
            growing['experience'] = re.sub('\s+', ' ', experience.strip())

        education = i.find('p', class_='vacancy__education')
        if education is not None:
            education = re.sub('.бразование', '', education.get_text())
            growing['education'] = re.sub('\s+', ' ', education.strip())

        contact = i.find('div', class_='vacancy__term')
        if contact.get_text() == 'Контактное лицо:':
            growing['contact'] = re.sub('\s+', ' ', i.find('div', class_='vacancy__desc').get_text().strip())
        if contact.get_text() == 'Электронная почта:':
            if i.find('div', class_='vacancy__desc') is not None:
                growing['email'] = re.sub('\s+', ' ', i.find('div', class_='vacancy__desc').get_text().strip())
        if contact.get_text() == 'Номера телефонов:':
            number_array = i.find_all('span', class_='nowrap')
            number = ''
            for g in number_array:
                number += re.sub('\s+', ' ', g.get_text().strip()) + '\n'
            growing['numbers'] = number[:-1]
    return [pub_link, growing]


def tut_quest(pub_link):
    req = requests.get(pub_link, headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')

    growing = {}
    for i in starting:
        growing[i] = 'none'

    title = soup.find('div', class_='vacancy-title')
    if title is not None:
        if title.find('h1') is not None:
            tag = ''
            headline = re.sub('\s+', ' ', title.find('h1').get_text())
            growing['title'] = headline
            headline = re.sub('/', ' / ', headline)
            headline = re.sub('\(.*?\)|[+.,/]|г\.', '', headline.lower())
            headline = re.sub('e-mail', 'email', re.sub('\s+', ' ', headline))
            headline = re.sub('[\s-]', '_', headline.strip().capitalize())
            for i in re.split('(_)', headline):
                if len(tag) <= 20:
                    tag += i
            if tag.endswith('_'):
                tag = tag[:-1]
            growing['tags'] = [tag]

    place = soup.find('div', class_='vacancy-address-text')
    if place is not None:
        metro = ''
        metro_array = place.find_all('span', class_='metro-station')
        for i in metro_array:
            metro += re.sub('\s+', ' ', i.get_text().strip() + ', ')
        if metro != '':
            growing['metro'] = metro[:-2]
        growing['place'] = re.sub(metro, '', re.sub('\s+', ' ', place.get_text()).strip())

    short_place = soup.find_all('span')
    if short_place is not None:
        for i in short_place:
            if str(i).find('vacancy-view-raw-address') != -1:
                search = re.search('<!-- -->(.*?)<!-- -->', str(i))
                if search:
                    growing['short_place'] = re.sub('\s+', ' ', search.group(1).capitalize().strip())
                    break
        if growing['short_place'] == 'none':
            short_place = soup.find('div', class_='vacancy-company')
            if short_place is not None:
                short_place = short_place.find('p')
                if short_place is not None:
                    growing['short_place'] = re.sub('\s+', ' ', short_place.get_text().capitalize().strip())

    geo_search = re.search('{"lat": (.*?), "lng": (.*?), "zoom"', str(soup))
    if geo_search:
        growing['geo'] = re.sub('\s', '', geo_search.group(1)) + ',' + re.sub('\s', '', geo_search.group(2))

    money = soup.find('p', class_='vacancy-salary')
    if money is not None:
        money_array = []
        money = re.sub('\s', '', money.get_text().lower())
        search_ot = re.search('от(\d+)', money)
        search_do = re.search('до(\d+)', money)
        if search_do:
            money_array.append(search_do.group(1))
            money_array.append('none')
        elif search_ot:
            money_array.append(search_ot.group(1))
            money_array.append('more')
        else:
            money_array = 'none'
        growing['money'] = money_array

    org_name = soup.find('a', {'data-qa': 'vacancy-company-name'})
    if org_name is not None:
        growing['org_name'] = re.sub('\s+', ' ', org_name.get_text().strip())

    description = soup.find('div', class_='g-user-content')
    if description is not None:
        description = description.find_all(['p', 'ul', 'strong'])
        tempering = []
        main = ''
        prev = ''
        for i in description:
            text = ''
            lists = i.find_all('li')
            if len(lists) != 0:
                for g in lists:
                    text += '🔹 ' + re.sub('\n', '', g.get_text().capitalize()) + '\n'
            else:
                temp = i.get_text().strip()
                if prev != temp:
                    if temp.endswith(':'):
                        text += '\n✅ ' + bold(temp) + '\n'
                    else:
                        tempering.append(temp)
                prev = temp
            main += text
        main = main[:-1]
        if len(tempering) > 0:
            main += '\n\n'
        for i in tempering:
            main += i + '\n'
        growing['description'] = main

    numbers = ''
    items = soup.find_all(['p', 'a', 'span'])
    for i in items:
        search = re.search('data-qa="vacancy-view-employment-mode"', str(i))
        if search:
            schedule_text = ''
            schedule = i.find('span')
            if schedule is not None:
                schedule_text = re.sub('\s+', ' ', schedule.get_text().strip())
                growing['schedule'] = re.sub('график', '', schedule_text).strip().capitalize()
            employment = re.sub('\s+', ' ', i.get_text().lower())
            employment = re.sub(',|занятость|' + schedule_text, '', employment).strip().capitalize()
            growing['employment'] = employment

        search = re.search('data-qa="vacancy-experience"', str(i))
        if search:
            growing['experience'] = re.sub('\s+', ' ', i.get_text().strip())

        search = re.search('data-qa="vacancy-contacts__fio"', str(i))
        if search:
            growing['contact'] = re.sub('\s+', ' ', i.get_text().strip())

        search = re.search('data-qa="vacancy-contacts__email"', str(i))
        if search:
            growing['email'] = re.sub('\s+', ' ', i.get_text().strip())

        search = re.search('data-qa="vacancy-contacts__phone"', str(i))
        if search:
            if numbers.find(re.sub('\s+', ' ', i.get_text().strip())) == -1:
                numbers += re.sub('\s+', ' ', i.get_text().strip()) + '\n'
    if numbers != '':
        growing['numbers'] = numbers[:-1]
    return [pub_link, growing]


def former(growing, kind, pub_link):
    text = ''
    if growing['title'] != 'none':
        text_to_image = re.sub('/', ' / ', growing['title'])
        text_to_image = re.sub('\(.*?\)|[+.,]|г\.', '', text_to_image)
        text_to_image = re.sub('e-mail', 'email', re.sub('\s+', ' ', text_to_image))
        growing['tag_picture'] = image(re.sub('[\s-]', ' ', text_to_image.strip()))
        text = growing['tag_picture'] + '👨🏻‍💻 ' + bold(growing['title']) + '\n'
    if growing['short_place'] != 'none':
        text += '🏙 ' + growing['short_place'] + '\n'
    if growing['experience'] != 'none':
        text += '🏅 Опыт работы ➡ ' + growing['experience'].capitalize() + '\n'
    if growing['education'] != 'none':
        text += '👨‍🎓 Образование ➡ ' + growing['education'].capitalize() + '\n'
    if growing['money'] != 'none':
        more = ''
        if growing['money'][1] != 'none':
            more += '+'
        text += '💸 ' + bold('З/П ') + growing['money'][0] + more + ' руб.' + '\n'
    text += bold('\n📔 Контакты\n')
    if growing['org_name'] != 'none':
        text += growing['org_name'] + '\n'
    if growing['contact'] != 'none':
        text += growing['contact'] + '\n'
    if growing['numbers'] != 'none':
        text += growing['numbers'] + '\n'
    if growing['email'] != 'none':
        text += growing['email'] + ' ➡ Резюме\n'
    if growing['place'] != 'none':
        text += bold('\n🏘 Адрес\n') + growing['place'] + '\n'
    if growing['metro'] != 'none':
        text += '🚇 ' + growing['metro'] + '\n'

    if kind == 'MainChannel':
        keys = None
        if growing['geo'].lower() != 'none':
            text += '\n📍 <a href="http://maps.yandex.ru/?text=' + growing['geo'] + '">На карте</a>\n'
        text += '\n🔎 <a href="' + pub_link + '">Источник</a>\n'
    else:
        keys = keyboard
        text += code('-------------------\n')
        if growing['geo'].lower() != 'none':
            text += '📍http://maps.yandex.ru/?text=' + growing['geo'] + '\n'
        text += '🔎' + pub_link + '🔎\n'
        text += code('-------------------\n')

    if growing['tags'] != 'none':
        text += italic('\n💼ТЕГИ: ')
        for i in growing['tags']:
            text += '#' + re.sub('_+', '_', i) + ' '
        text = text[:-1] + '\n'

    if growing['short_place'] == 'none' or growing['money'] == 'none' or growing['title'] == 'none':
        text = pub_link

    if growing['title'] != 'none':
        search_restricted = re.search('водитель|яндекс|такси|уборщи', growing['title'].lower())
        if search_restricted:
            text = pub_link

    if growing['org_name'] != 'none':
        search_restricted = re.search('доброном', growing['org_name'].lower())
        if search_restricted:
            text = pub_link

    if growing['experience'] != 'none':
        search_restricted = re.search('6', growing['experience'].capitalize())
        if search_restricted:
            text = pub_link

    return [text, keys, pub_link, growing]


def poster(id_forward, array):
    global last_date
    if array[0] != array[2]:
        message = bot.send_message(id_forward, array[0], reply_markup=array[1], parse_mode='HTML')
        instagram_image(instagram_former(array[3]))
        if id_forward == idMain:
            if last_date < message.date:
                last_date = message.date
                start_editing = code('Последний пост на канале jobsrb\n') + \
                    bold('d: ') + code(timer(last_date + 3 * 60 * 60)) + bold(' :d')
                try:
                    bot.edit_message_text(start_editing, -1001471643258, tkn.start_link, parse_mode='HTML')
                except Exception as e:
                    error = '<b>Проблемы с измением стартового ' \
                            'сообщения на канале @UsefullCWLinks</b>\n\n' + start_editing + '\n' + str(e)
                    bot.send_message(idMe, error, parse_mode='HTML', disable_web_page_preview=True)
    else:
        text = array[3]['tag_picture'] + 'Что-то пошло не так: {\n' + under(bold('link')) + ': ' + array[2] + '\n'
        for i in array[3]:
            if i == 'short_place' or i == 'money' or i == 'title':
                text += under(bold(i)) + ': ' + re.sub('<', '&#60;', str(array[3].get(i))) + '\n'
            elif i != 'description':
                text += str(i) + ': ' + re.sub('<', '&#60;', str(array[3].get(i))) + '\n'
        bot.send_message(idMe, text + '}', parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    try:
        if call.data == 'post':
            search = re.search('🔎(.*?)🔎', call.message.text)
            if search:
                site_search = re.search('tut\.by|hh\.ru', search.group(1))
                if site_search:
                    post = tut_quest(search.group(1))
                else:
                    post = praca_quest(search.group(1))
                poster(idMain, former(post[1], 'MainChannel', post[0]))
                text = call.message.text + code('\n✅ опубликован ✅')
                bot.edit_message_text(chat_id=call.message.chat.id, text=text, message_id=call.message.message_id,
                                      reply_markup=None, parse_mode='HTML', disable_web_page_preview=True)
            else:
                send_json(call.message.text, 'callbacks', code('Не нашел в посте ссылку на вакансию'))

        elif call.data == 'viewed':
            text = call.message.text + code('\n👀 просмотрен 👀')
            bot.edit_message_text(chat_id=call.message.chat.id, text=text, message_id=call.message.message_id,
                                  reply_markup=None, parse_mode='HTML', disable_web_page_preview=True)
    except IndexError and Exception:
        executive(callbacks, str(call))


@bot.message_handler(func=lambda message: message.text)
def repeat_all_messages(message):
    try:
        if message.chat.id == idMe or message.chat.id == idAndre:
            if message.text.startswith('https://praca.by/vacancy/') or message.text.startswith('https://'):
                site_search = re.search('tut\.by|hh\.ru', message.text)
                if site_search:
                    post = tut_quest(message.text)
                else:
                    post = praca_quest(message.text)
                poster(message.chat.id, former(post[1], 'Private', post[0]))
            elif message.text.startswith('/pic'):
                subbed = re.sub('/pic', '', message.text).strip()
                bot.send_message(message.chat.id, image(subbed), parse_mode='HTML')
            elif message.text.startswith('/base'):
                doc = open('log.txt', 'rt')
                bot.send_document(message.chat.id, doc)
                doc.close()
            else:
                bot.send_message(message.chat.id, bold('ссылка не подошла, пошел нахуй'), parse_mode='HTML')
    except IndexError and Exception:
        executive(repeat_all_messages, str(message))


def googler(link):
    global used
    global creds2
    global client2
    try:
        used.insert_row([link], 1)
    except IndexError and Exception:
        creds2 = ServiceAccountCredentials.from_json_keyfile_name('person2.json', scope)
        client2 = gspread.authorize(creds2)
        used = client2.open('growing').worksheet('main')
        used.insert_row([link], 1)


def checker(address, main_sep, link_sep, quest):
    global used_array
    global unused_box
    sleep(3)
    time_now = stamper(timer(0))
    text = requests.get(address, headers=headers)
    soup = BeautifulSoup(text.text, 'html.parser')
    posts_raw = soup.find_all('div', class_=main_sep)
    posts = []
    for i in posts_raw:
        link = i.find('a', class_=link_sep)
        if link is not None:
            posts.append(link.get('href'))
    for i in posts:
        if i not in used_array and i not in unused_box and (11 <= hour() < 21):
            if (last_date + 120 * 60) < time_now:
                googler(i)
                used_array.insert(0, i)
                post = quest(i)
                poster(idMain, former(post[1], 'MainChannel', post[0]))
                printer(i + ' сделано')
                sleep(3)
            else:
                unused_box.append(i)


def praca_checker():
    while True:
        try:
            checker('https://praca.by/search/vacancies/', 'vac-small__column vac-small__column_2',
                    'vac-small__title-link', praca_quest)
        except IndexError and Exception:
            executive(praca_checker, 0)


def tut_checker():
    while True:
        try:
            global unused_box
            checker('https://jobs.tut.by/search/vacancy?order_by=publication_time&clusters=true&area=16&'
                    'currency_code=BYR&enable_snippets=true&only_with_salary=true', 'vacancy-serp-item',
                    'bloko-link', tut_quest)
            if len(unused_box) > 0 and (11 <= hour() < 21):
                if (last_date + 122 * 60) < stamper(timer(0)):
                    site_search = re.search('tut\.by|hh\.ru', unused_box[0])
                    if site_search:
                        post = tut_quest(unused_box[0])
                    else:
                        post = praca_quest(unused_box[0])
                    googler(unused_box[0])
                    poster(idMain, former(post[1], 'MainChannel', post[0]))
                    printer(unused_box[0] + ' сделано')
                    unused_box.pop(0)
                    sleep(3)

        except IndexError and Exception:
            executive(tut_checker, 0)


def telepol():
    try:
        bot.polling(none_stop=True, timeout=60)
    except IndexError and Exception:
        bot.stop_polling()
        sleep(1)
        telepol()


if __name__ == '__main__':
    gain = []
    if tkn.floater == 1:
        gain = [tut_checker, praca_checker]
    elif tkn.idMain == idMe:
        gain = [tut_checker]
    thread_array = defaultdict(dict)
    for thread_element in gain:
        thread_id = _thread.start_new_thread(thread_element, ())
        thread_start_name = re.findall('<.+?\s(.+?)\s.*>', str(thread_element))
        thread_array[thread_id] = defaultdict(dict)
        thread_array[thread_id]['name'] = thread_start_name[0]
    telepol()
