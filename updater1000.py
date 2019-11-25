import gspread
from oauth2client.service_account import ServiceAccountCredentials
import telebot
from telebot import types
import urllib3
import re
import requests
import time
from time import sleep
import datetime
from datetime import datetime
import _thread
import random
import copy
from SQL import SQLighter
from bs4 import BeautifulSoup


stamp1 = int(datetime.now().timestamp())
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds1 = ServiceAccountCredentials.from_json_keyfile_name('xstorage1.json', scope)
client1 = gspread.authorize(creds1)
data1 = client1.open('eustorage').worksheet('old')

bot = telebot.TeleBot('659292396:AAEeJKTEU4g2168cADrQx6QmN7IzSrJX_Ok')
idMe = 396978030
ignore = str(data1.cell(1, 1).value)
old = str(data1.cell(2, 1).value)
old = old.split('/')
cock = int(old[1])
old = int(old[0])
ignore = ignore.split('/')
adress = 'https://t.me/ChatWarsAuction/'

# ====================================================================================


def log(stamp):
    if stamp == 0:
        stamp = int(datetime.now().timestamp())
    day = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%d')
    month = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%m')
    year = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%Y')
    hours = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%H')
    minutes = datetime.utcfromtimestamp(int(stamp)).strftime('%M')
    seconds = datetime.utcfromtimestamp(int(stamp)).strftime('%S')
    message = str(day) + '.' + str(month) + '.' + str(year) + ' ' + str(hours) + ':' \
        + str(minutes) + ':' + str(seconds)
    return message


# ====================================================================================
bot.send_message(idMe, '🧐\n<code>' + log(stamp1) + '  -  ' + log(0) + '</code>', parse_mode='HTML')


def former(text, id):
    goo = []
    soup = BeautifulSoup(text.text, 'html.parser')
    is_post_not_exist = str(soup.find('div', class_='tgme_widget_message_error'))
    if str(is_post_not_exist) == str(None):
        string = str(soup.find('div', class_='tgme_widget_message_text js-message_text'))
        string = re.sub(' (dir|class|style)=\\"\w+[^\\"]+\\"', '', string)
        string = re.sub('(<b>|</b>|<i>|</i>|<div>|</div>)', '', string)
        string = re.sub('/', '&#47;', string)
        string = re.sub('(<br&#47;>)', '/', string)

        drop_time = soup.find('time', class_='datetime')
        stamp = int(time.mktime(datetime.strptime(str(drop_time['datetime']), '%Y-%m-%dT%H:%M:%S+00:00').timetuple()))
        stamp_now = int(datetime.now().timestamp()) - 36 * 60 * 60

        if stamp <= stamp_now:
            goo.append(str(id) + '/' + string)
        else:
            goo.append('active')
    else:
        goo.append('false')
    return goo


def checker():
    while True:
        try:
            global data1
            global old
            global cock
            print(log(0))
            creds1 = ServiceAccountCredentials.from_json_keyfile_name('xstorage1.json', scope)
            client1 = gspread.authorize(creds1)
            data1 = client1.open('eustorage').worksheet('old')
            col = 1000
            cell_list = data1.range('A' + str(cock) + ':A' + str(cock + col))
            cock += col
            i = 1
            while (i % (col + 1)) != 0 and old >= 5:
                sleep(0.05)
                text = requests.get(adress + str(old) + '?embed=1')
                print('работаю ' + adress + str(old))
                if str(old) not in ignore:
                    goo = former(text, old)
                    if goo[0] == 'active':
                        print(adress + str(old) + ' Активен, ничего не делаю')
                    elif goo[0] == 'false':
                        print(adress + str(old) + ' Форму не нашло')
                        old -= 1
                    else:
                        cell_list[i - 1].value = goo[0]
                        old -= 1
                        i += 1
                else:
                    print(adress + str(old) + ' В черном списке, пропускаю')
                    old -= 1
            if i > 1:
                string = str(old) + '/' + str(cock)
                try:
                    data1.update_cells(cell_list)
                    data1.update_cell(2, 1, string)
                except:
                    creds1 = ServiceAccountCredentials.from_json_keyfile_name('xstorage1.json', scope)
                    client1 = gspread.authorize(creds1)
                    data1 = client1.open('eustorage').worksheet('old')
                    data1.update_cells(cell_list)
                    data1.update_cell(2, 1, string)
        except Exception as e:
            bot.send_message(idMe, 'вылет checker\n' + str(e))
            sleep(0.9)


def telepol():
    try:
        bot.polling(none_stop=True, timeout=60)
    except:
        bot.stop_polling()
        sleep(1)
        telepol()


if __name__ == '__main__':
    _thread.start_new_thread(checker, ())
    telepol()
