import gspread
from oauth2client.service_account import ServiceAccountCredentials
import unicodedata
from unidecode import unidecode
import traceback
import heroku3
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
import os
import random
import json
import copy
import sys
from collections import defaultdict

firsthelp = 1
tkn = '659292396:AAEeJKTEU4g2168cADrQx6QmN7IzSrJX_Ok'
bot = telebot.TeleBot(tkn)
idMe = 396978030
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# creds1 = ServiceAccountCredentials.from_json_keyfile_name('xstorage1.json', scope)
# client1 = gspread.authorize(creds1)
# data1 = client1.open('Boris').worksheet('users')

kek = os.listdir('/')
print(kek)
for i in kek:
    if i != 'lost+found':
        g = os.listdir('/' + i)
        print(i + '   ' + str(g))
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
    data = '<code>' + str(weekday) + ' ' + str(day) + '.' + str(month) + '.' + str(year) + \
           ' ' + str(hours) + ':' + str(minutes) + ':' + str(seconds) + '</code>'
    return data


def printer(printext):
    global stamp_creategooglerow
    thread_name = str(thread_array[_thread.get_ident()]['name'])
    logfile = open('log.txt', 'a')
    log_print_text = '\n' + re.sub('<.*?>', '', logtime(0)) + ' ' + thread_name + ' ' + printext
    logfile.write(log_print_text)
    logfile.close()
    print(log_print_text)
    if thread_name == 'creategooglerow':
        stamp_creategooglerow = int(datetime.now().timestamp())


def thread_name():
    return str(thread_array[_thread.get_ident()]['name']) + ' '


@bot.message_handler(func=lambda message: message.text)
def repeat_all_messages(message):
    for i in thread_array:
        print(feature.created_at)
        print(str(i) + ' ' + str(thread_array[i]['name']) + ' ' + str(thread_array[i]['function']))


def telepol():
    try:
        bot.polling(none_stop=True, timeout=60)
    except:
        bot.stop_polling()
        sleep(1)
        telepol()


def helper():
    while True:
        try:
            global firsthelp
            if firsthelp == 1:
                logfile = open('logs.txt', 'w')
                logfile.write('Начало записи лога ' + re.sub('<.*?>', '', logtime(0)))
                logfile.close()
                firsthelp = 0
            sleep(1)
            print(thread_name() + logtime(0))
            sleep(10)
        except IndexError and Exception as e:
            print(' вылет залупы ' + logtime(0))


def helper2():
    while True:
        try:
            sleep(2)
            print(thread_name() + 'начало')
            logfile = open('logs.txt', 'a')
            logfile.write('\n' + re.sub('<.*?>', '', logtime(0)) + ' начало')
            logfile.close()
            sleep(10)
        except IndexError and Exception as e:
            print(' вылет залупы ' + logtime(0))


def helper7():
    while True:
        try:
            global stamp_creategooglerow
            sleep(60)
            print(thread_name() + logtime(0))
            now = int(datetime.now().timestamp()) - 20 * 60
            if now > stamp_creategooglerow:
                bot.send_message(idMe, '<b>creategooglerow</b> не отвечает уже 20 минут', parse_mode='HTML')
            sleep(1200)
        except IndexError and Exception as e:
            print(' вылет залупы ' + logtime(0))


if __name__ == '__main__':
    array = [helper, helper2, helper7]
    thread_array = defaultdict(dict)
    for i in array:
        thread_id = _thread.start_new_thread(i, ())
        thread_start_name = re.findall('<.+?\s(.+?)\s.*>', str(i))
        thread_array[thread_id] = defaultdict(dict)
        thread_array[thread_id]['name'] = thread_start_name[0]
        thread_array[thread_id]['function'] = i
    telepol()
