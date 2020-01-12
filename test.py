import re
import sys
import _thread
import telebot
import requests
import traceback
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime

bot = telebot.TeleBot('993071212:AAFbZvEx8IJaL1_8fWNDs4qdAJHNMKTnS7U')
idAndre = 470292601
idMe = 396978030

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


def bold(txt):
    return '<b>' + txt + '</b>'


def code(txt):
    return '<code>' + txt + '</code>'


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


bot.send_message(idMe, 'запуск')


@bot.message_handler(func=lambda message: message.text)
def repeat_all_messages(message):
    try:
        if message.chat.id == idMe or message.chat.id == idAndre:
            if message.text.startswith('https://praca.by/vacancy/'):
                req = requests.get(message.text)
                soup = BeautifulSoup(req.text, 'html.parser')
                if soup.find('span', class_='hidden-vac-contact') is not None:
                    req = requests.get(message.text +
                                       '?token=wykzQ7x5oq6kZWG7naOvHprT4vcZ1vdFFUSXoOfmKR10pPWq0ox5acYvr3wcfg00')
                    soup = BeautifulSoup(req.text, 'html.parser')
                growing = {}
                starting = ['title', 'place', 'tags', 'money', 'org_name', 'schedule', 'employment', 'short_place',
                            'experience', 'education', 'contact', 'numbers', 'description', 'email', 'metro']
                for i in starting:
                    growing[i] = 'none'

                title = soup.find('h1', class_='vacancy__title')
                if title is not None:
                    growing['title'] = title.get_text().strip()

                place = soup.find('div', class_='job-address')
                if place is not None:
                    growing['place'] = re.sub('\s+', ' ', place.get_text().strip())

                short_place = soup.find('div', class_='vacancy__city')
                if short_place is not None:
                    growing['short_place'] = re.sub('\s+', ' ', short_place.get_text().strip())

                metro = soup.find('div', class_='vacancy__metro')
                if metro is not None:
                    metro_array = metro.find_all('span', class_='nowrap')
                    metro = ''
                    for i in metro_array:
                        metro += re.sub('\s+', ' ', i.get_text().capitalize().strip() + ', ')
                    growing['metro'] = metro[:-2]

                tag_list = soup.find('div', class_='categories')
                if tag_list is not None:
                    tags = tag_list.find_all('a')
                    tag_array = []
                    for i in tags:
                        tag = re.sub('[\s-]', '_', i.get_text())
                        tag_array.append(re.sub('_/_', ' #', tag))
                    growing['tags'] = tag_array

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

                description = soup.find('div', class_='description')
                if description is not None:
                    description = description.find_all(['p', 'ul'])
                    tempering = []
                    main = ''
                    for i in description:
                        lists = i.find_all('li')
                        if len(lists) != 0:
                            text = ''
                            for g in lists:
                                point = ''
                                if lists.index(g) + 1 < 10:
                                    point = number_list[lists.index(g) + 1]
                                text += point + ' ' + re.sub('\n', '', g.get_text().capitalize()) + '\n'
                        else:
                            text = ''
                            temp = i.get_text().strip()
                            if temp.endswith(':'):
                                text += '\n📃 ' + bold(temp) + '\n'
                            else:
                                tempering.append(temp)
                        main += text
                    main = main[:-1]
                    if len(tempering) > 0:
                        main += '\n\n'
                    for i in tempering:
                        main += i + '\n'
                    growing['description'] = main

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
                if growing['description'] != 'none':
                    text += growing['description'] + '\n'
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
                if growing['tags'] != 'none':
                    for i in growing['tags']:
                        text += '#' + i + ' '
                    text = text[:-1]
            else:
                text = bold('нахуй иди ДОЛБАЕБ)')

            bot.send_message(message.chat.id, text, parse_mode='HTML')
    except IndexError:
        executive(repeat_all_messages, 1)


def telepol():
    try:
        bot.polling(none_stop=True, timeout=60)
    except:
        bot.stop_polling()
        sleep(1)
        telepol()


if __name__ == '__main__':
    telepol()
