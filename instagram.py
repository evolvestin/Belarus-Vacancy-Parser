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


admins = eval(os.environ['admins'])


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
