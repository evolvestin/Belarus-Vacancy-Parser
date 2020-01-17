import re
import sys
import tkn
import _thread
import gspread
import telebot
import requests
import geocoder
import traceback
from time import sleep
from telebot import types
from bs4 import BeautifulSoup
from datetime import datetime
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
calendar_list = {
    'января': '01',
    'февраля': '02',
    'марта': '03',
    'апреля': '04',
    'мая': '05',
    'июня': '06',
    'июля': '07',
    'августа': '08',
    'сентября': '09',
    'октября': '10',
    'ноября': '11',
    'декабря': '12'
}
number_list = {
    1: '1️⃣',
    2: '2️⃣',
    3: '3️⃣',
    4: '4️⃣',
    5: '5️⃣',
    6: '6️⃣',
    7: '7️⃣',
    8: '8️⃣',
    9: '9️⃣',
    10: '🔟'
}
idMe = 396978030
idAndre = 470292601
idMain = -1001404073893
keyboard.add(*buttons)
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


def executive(new, logs):
    search = re.search('<function (\S+)', str(new))
    if search:
        name = search.group(1)
    else:
        name = ''
    exc_type, exc_value, exc_traceback = sys.exc_info()
    error_raw = traceback.format_exception(exc_type, exc_value, exc_traceback)
    error = ''
    for i in error_raw:
        error += str(i)
    bot.send_message(idMe, 'Вылет ' + name + '\n' + error)
    if logs == 0:
        sleep(100)
        thread_id = _thread.start_new_thread(new, ())
        thread_array[thread_id] = defaultdict(dict)
        thread_array[thread_id]['name'] = name
        thread_array[thread_id]['function'] = new
        bot.send_message(idMe, 'Запущен ' + bold(name), parse_mode='HTML')
        sleep(30)
        _thread.exit()
    else:
        text = ''
        for character in logs:
            replaced = unidecode(str(character))
            if replaced != '':
                text += replaced
            else:
                try:
                    text += '[' + unicodedata.name(character) + ']'
                except ValueError:
                    text += '[???]'
        docw = open(name + '.json', 'w')
        docw.write(text)
        docw.close()
        doc = open(name + '.json', 'rb')
        bot.send_document(idMe, doc)
        doc.close()


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


def praca_quest(link, kind):
    pub_link = link
    req = requests.get(link)
    soup = BeautifulSoup(req.text, 'html.parser')

    growing = {}
    for i in starting:
        growing[i] = 'none'

    if soup.find('span', class_='hidden-vac-contact') is not None:
        link += '?token=wykzQ7x5oq6kZWG7naOvHprT4vcZ1vdFFUSXoOfmKR10pPWq0ox5acYvr3wcfg00'

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
        if growing['geo'] != 'none':
            text += '\n📍 <a href="http://maps.yandex.ru/?text=' + growing['geo'] + '">На карте</a>\n'
        text += '\n🔎 <a href="' + pub_link + '">Источник</a>\n'
    else:
        keys = keyboard
        text += code('-------------------\n')
        if growing['geo'] != 'none':
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
                poster(idMain, praca_quest(search.group(1), 'MainChannel'))
            else:
                doc_text = code('Не нашел в посте ссылку на вакансию')
                json_text = ''
                for character in logs:
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
            text = call.message.text + code('\n✅ опубликован ✅')
            bot.edit_message_text(chat_id=call.message.chat.id, text=text, message_id=call.message.message_id,
                                  reply_markup=None, parse_mode='HTML', disable_web_page_preview=True)

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
            if message.text.startswith('https://praca.by/vacancy/') and message.text.endswith('/'):
                poster(message.chat.id, praca_quest(message.text, 'Private'))
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
                    poster(idJobi, praca_quest(i, 'Jobi'))
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
    gain = [praca_checker]
    thread_array = defaultdict(dict)
    for i in gain:
        thread_id = _thread.start_new_thread(i, ())
        thread_start_name = re.findall('<.+?\s(.+?)\s.*>', str(i))
        thread_array[thread_id] = defaultdict(dict)
        thread_array[thread_id]['name'] = thread_start_name[0]
        thread_array[thread_id]['function'] = i
    telepol()
