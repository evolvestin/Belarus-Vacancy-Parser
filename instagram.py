import os
import re
import pickle
import random
import string
from time import sleep
from typing import Union
from chrome import chrome
from functions import AuthCentre
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def tags_generator():
    cities_list, generated_tags = [], {}
    for city in [('None', 'None'), ('витебск', 'витебске'), ('могилев', 'могилеве'),
                 ('гродно', 'гродно'), ('брест', 'бресте'), ('минск', 'минске'), ('гомель', 'гомеле')]:
        cities_list.append(city[0]) if city[0] != 'None' else None
        city_tags, generated = [city[0]] if city[0] != 'None' else [], [('работа', 'мечты')]
        for place in [('беларусь', 'беларуси')] + [city if city[0] != 'None' else None]:
            if place:
                for action in ['заработок', 'работа', 'вакансии']:
                    generated.extend([(place if type(place) == str else place[0], action),
                                      (action, 'в', place if type(place) == str else place[1])])
        for tag in generated:
            if len(tag) == 2:
                city_tags.extend([f'{tag[0]}{tag[1]}', f'{tag[0]}_{tag[1]}', f'{tag[1]}{tag[0]}'])
            elif len(tag) == 3:
                city_tags.extend([f'{tag[0]}{tag[1]}{tag[2]}', f'{tag[0]}_{tag[1]}_{tag[2]}'])
        city_tags.extend(['работа', 'деньги', 'заработок'])
        generated_tags[city[0]] = city_tags
    return generated_tags, cities_list


admins = eval(os.environ['admins'])
gen_tags, cities = tags_generator()
text = 'Найти вакансию можно в нашем Telegram канале ' \
       '(ссылка в шапке профиля) по №{0} (воспользуйтесь поиском по каналу)\n\nID {0}\n\n'


def generator(post_id: Union[int, str], place: str, vacancy_tags: list):
    tags, response = [], text.format(post_id)
    for tag in vacancy_tags:
        tags.append(tag.lower())
        modified = re.sub('_', '', tag).lower()
        tags.append(modified) if modified != tag.lower() else None
    for city in cities:
        if city in re.sub('ё', 'е', place.lower()):
            break
    else:
        city = 'None'
    city_tags = gen_tags.get(city, [])
    len_city_tags = len(city_tags) if len(city_tags) <= 30 - len(tags) else 30 - len(tags)
    tags.extend(random.sample(city_tags, len_city_tags))
    for tag in random.sample(tags, len(tags)):
        if len(response) + len(tag) + 2 <= 2000:
            response += f' #{tag}'
    return response


def test(auth: AuthCentre):
    def wait_provider(delay: int = 3):
        sleep(delay + random.normalvariate(3, 1))
        file_name = f"{''.join(random.sample(string.ascii_letters, 10))}.png"
        try:
            with open('text.txt', 'w') as file:
                file.write(str(driver.page_source))
            with open('text.txt', 'rb') as file:
                auth.bot.send_document(admins[0], file)
        except IndexError and Exception:
            auth.dev.executive(None)
        try:
            driver.save_screenshot(file_name)
            with open(file_name, 'rb') as file:
                auth.bot.send_photo(admins[0], file)
        except IndexError and Exception:
            auth.dev.executive(None)
        try:
            os.remove(file_name), os.remove('text.txt')
        except IndexError and Exception:
            auth.dev.executive(None)

    try:
        driver = chrome(os.environ.get('local'))
        driver.set_window_size(1000, 1200)
        driver.get('https://www.google.com/')
        wait_provider(4)
        driver.close()
    except IndexError and Exception:
        auth.dev.executive(None)


def poster(auth: AuthCentre, username: str, description: str, image_path: str, debug: bool = False):
    def wait_provider(delay: int = 3):
        sleep(delay + random.normalvariate(3, 1))
        if debug:
            file_name = f"{''.join(random.sample(string.ascii_letters, 10))}.png"
            try:
                with open('text.txt', 'w') as file:
                    file.write(str(driver.page_source))
                with open('text.txt', 'rb') as file:
                    auth.bot.send_document(admins[0], file)
            except IndexError and Exception:
                auth.dev.executive(None)
            try:
                driver.save_screenshot(file_name)
                with open(file_name, 'rb') as file:
                    auth.bot.send_photo(admins[0], file)
            except IndexError and Exception:
                auth.dev.executive(None)
            try:
                os.remove(file_name), os.remove('text.txt')
            except IndexError and Exception:
                auth.dev.executive(None)

    response = 'Process crashed'
    try:
        driver = chrome(os.environ.get('local'))
        driver.set_window_size(1000, 1200)
        driver.get(f'https://www.instagram.com/{username}/')
        wait_provider(15)  # for screenshot
        input_xpath = "//input[@accept='image/jpeg,image/png,image/heic,image/heif,video/mp4,video/quicktime']"
        for cookie in pickle.load(open('cookies.pkl', 'rb')):
            driver.add_cookie(cookie)
        wait_provider(15)  # for screenshot 2
        driver.get(f'https://www.instagram.com/{username}/')
        wait_provider(30)
        driver.find_elements(By.TAG_NAME, 'svg')[6].click()
        WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, "//div[@role='dialog']")))
        wait_provider(1)
        driver.find_element(By.XPATH, input_xpath).send_keys(f'{os.getcwd()}/{image_path}')
        WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, "//div[@role='dialog']")))
        div = driver.find_element(By.XPATH, "//div[@role='dialog']")
        wait_provider(1)
        div.find_elements(By.TAG_NAME, 'button')[1].click()
        WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, "//div[@role='tablist']")))
        wait_provider(1)
        div.find_elements(By.TAG_NAME, 'button')[1].click()
        WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.TAG_NAME, 'textarea')))
        wait_provider(1)
        driver.find_element(By.TAG_NAME, 'textarea').send_keys(description)
        wait_provider(1)
        if debug is False:
            div.find_elements(By.TAG_NAME, 'button')[1].click()
            wait_provider(15)
            driver.get(f'https://www.instagram.com/{username}/')
            wait_provider(5)
            response = driver.find_element(By.TAG_NAME, 'article').find_element(By.TAG_NAME, 'a').get_attribute('href')
        driver.close()
    except IndexError and Exception:
        auth.dev.executive(None)
    return str(response)
