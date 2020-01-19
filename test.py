import re
import sys
import tkn
import _thread
import gspread
import telebot
import requests
import geocoder
import traceback
import unicodedata
from time import sleep
from telebot import types
from bs4 import BeautifulSoup
from datetime import datetime
from unidecode import unidecode
from collections import defaultdict
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
starting = ['title', 'place', 'geo', 'money', 'org_name', 'schedule', 'employment', 'short_place',
            'experience', 'education', 'contact', 'numbers', 'email', 'metro']
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36'
                         ' (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}
idMe = 396978030
idAndre = 470292601
keyboard.add(*buttons)
idMain = -1001404073893
idJobi = -1001272631426
# =================================================================


def bold(txt):
    return '<b>' + txt + '</b>'


def code(txt):
    return '<code>' + txt + '</code>'


def printer(printer_text):
    thread_name = str(thread_array[_thread.get_ident()]['name'])
    logfile = open('log.txt', 'a')
    log_print_text = thread_name + ' ' + printer_text
    logfile.write('\n' + re.sub('<.*?>', '', logtime(0)) + log_print_text)
    logfile.close()
    print(log_print_text)


def send_json(raw, name, doc_text):
    json_text = ''
    for character in raw:
        replaced = unidecode(str(character))
        if replaced != '':
            json_text += replaced
        else:
            try:
                json_text += '[' + unicodedata.name(character) + ']'
            except ValueError:
                json_text += '[???]'
    docw = open(name + '.json', 'w')
    docw.write(json_text)
    docw.close()
    doc = open(name + '.json', 'rb')
    bot.send_document(idMe, doc, caption=doc_text, parse_mode='HTML')
    doc.close()


def executive(new, logs):
    search = re.search('<function (\S+)', str(new))
    if search:
        name = search.group(1)
    else:
        name = 'None'
    exc_type, exc_value, exc_traceback = sys.exc_info()
    error_raw = traceback.format_exception(exc_type, exc_value, exc_traceback)
    error = 'Вылет ' + name + '\n'
    for i in error_raw:
        error += str(i)
    if logs == 0:
        bot.send_message(idMe, error)
        sleep(100)
        thread_id = _thread.start_new_thread(new, ())
        thread_array[thread_id] = defaultdict(dict)
        thread_array[thread_id]['name'] = name
        thread_array[thread_id]['function'] = new
        bot.send_message(idMe, 'Запущен ' + bold(name), parse_mode='HTML')
        sleep(30)
        _thread.exit()
    else:
        send_json(logs, name, error)


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


logfile_start = open('log.txt', 'w')
logfile_start.write('Начало записи лога ' + re.sub('<.*?>', '', logtime(0)))
logfile_start.close()
# bot = telebot.TeleBot('993071212:AAFbZvEx8IJaL1_8fWNDs4qdAJHNMKTnS7U')
bot = telebot.TeleBot(tkn.tkn)
start_message = bot.send_message(idMe, logtime(stamp1) + '\n' + logtime(0), parse_mode='HTML')
# ====================================================================================


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

    if growing['place'] != growing['short_place'] and growing['place'] != 'none':
        geo = geocoder.osm(growing['place'])
        if geo is not None:
            growing['geo'] = re.sub('[\[\]\s]', '', str(geo.latlng))

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
            growing['title'] = title.find('h1').get_text().strip()

    place = soup.find('div', class_='vacancy-address-text')
    if place is not None:
        metro = ''
        metro_array = place.find_all('span', class_='metro-station')
        for i in metro_array:
            metro += re.sub('\s+', ' ', i.get_text().capitalize().strip() + ', ')
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

    if growing['place'] != growing['short_place'] and growing['place'] != 'none':
        geo = geocoder.osm(growing['place'])
        if geo is not None:
            growing['geo'] = re.sub('[\[\]\s]', '', str(geo.latlng))

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
        growing['money'] = money_array

    org_name = soup.find('a', class_='vacancy-company-name')
    if org_name is not None:
        growing['org_name'] = re.sub('\s+', ' ', org_name.get_text().strip())

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
        text += '👨🏻‍💻 ' + bold(growing['title']) + '\n'
    if growing['short_place'] != 'none':
        text += '🏙 ' + growing['short_place'] + '\n'
    if growing['schedule'] != 'none':
        text += '📈 График ➡ ' + growing['schedule'].capitalize() + '\n'
    if growing['employment'] != 'none':
        text += '⏰ Занятость ➡ ' + growing['employment'].capitalize() + '\n'
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
        text += '🔎' + pub_link + '🔎'
    return [text, keys]


def poster(id_forward, array):
    bot.send_message(id_forward, array[0], reply_markup=array[1], parse_mode='HTML', disable_web_page_preview=True)


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
            if (message.text.startswith('https://praca.by/vacancy/') and message.text.endswith('/')) or \
                    (message.text.startswith('https://jobs.tut.by/vacancy/') and message.text.endswith('/')):
                site_search = re.search('tut\.by|hh\.ru', message.text)
                if site_search:
                    post = tut_quest(message.text)
                else:
                    post = praca_quest(message.text)
                poster(idMain, former(post[1], 'Private', post[0]))
            elif message.text.startswith('/base'):
                doc = open('log.txt', 'rt')
                bot.send_document(message.chat.id, doc)
                doc.close()
            else:
                bot.send_message(message.chat.id, bold('ссылка не подошла, пошел нахуй'), parse_mode='HTML')
    except IndexError and Exception:
        executive(repeat_all_messages, str(message))


def praca_checker():
    while True:
        try:
            global used
            global creds2
            global client2
            global used_array
            sleep(3)
            printer('работаю')
            text = requests.get('https://praca.by/search/vacancies/')
            soup = BeautifulSoup(text.text, 'html.parser')
            posts_raw = soup.find_all('div', class_='vac-small__column vac-small__column_2')
            posts = []
            for i in posts_raw:
                link = i.find('a', class_='vac-small__title-link')
                if link is not None:
                    posts.append(link.get('href'))
            for i in posts:
                if i not in used_array:
                    try:
                        used.insert_row([i], 1)
                    except:
                        creds2 = ServiceAccountCredentials.from_json_keyfile_name('person2.json', scope)
                        client2 = gspread.authorize(creds2)
                        used = client2.open('growing').worksheet('main')
                        used.insert_row([i], 1)
                    used_array.insert(0, i)
                    post = praca_quest(i)
                    poster(idMain, former(post[1], 'Jobi', post[0]))
                    printer(i + ' сделано')
                    sleep(3)
        except IndexError and Exception:
            executive(praca_checker, 0)


def tut_checker():
    while True:
        try:
            global used
            global creds2
            global client2
            global used_array
            sleep(3)
            text = requests.get('https://jobs.tut.by/search/vacancy?order_by=publication_time&clusters=true&area=16&'
                                'currency_code=BYR&enable_snippets=true&only_with_salary=true', headers=headers)
            soup = BeautifulSoup(text.text, 'html.parser')
            posts_raw = soup.find_all('div', class_='vacancy-serp-item')
            posts = []
            for i in posts_raw:
                link = i.find('a', class_='bloko-link')
                if link is not None:
                    posts.append(link.get('href'))
            for i in posts:
                if i not in used_array:
                    try:
                        used.insert_row([i], 1)
                    except:
                        creds2 = ServiceAccountCredentials.from_json_keyfile_name('person2.json', scope)
                        client2 = gspread.authorize(creds2)
                        used = client2.open('growing').worksheet('main')
                        used.insert_row([i], 1)
                    used_array.insert(0, i)
                    post = praca_quest(i)
                    poster(idMain, former(post[1], 'Jobi_tut', post[0]))
                    printer(i + ' сделано')
                    sleep(3)
        except IndexError and Exception:
            executive(praca_checker, 0)


def telepol():
    try:
        bot.polling(none_stop=True, timeout=60)
    except:
        bot.stop_polling()
        sleep(1)
        telepol()


if __name__ == '__main__':
    gain = [tut_checker, praca_checker]
    thread_array = defaultdict(dict)
    for i in gain:
        thread_id = _thread.start_new_thread(i, ())
        thread_start_name = re.findall('<.+?\s(.+?)\s.*>', str(i))
        thread_array[thread_id] = defaultdict(dict)
        thread_array[thread_id]['name'] = thread_start_name[0]
        thread_array[thread_id]['function'] = i
    telepol()
