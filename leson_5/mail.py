# 1) Написать программу, которая собирает входящие письма из своего или тестового почтового ящика
# и сложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
# Логин тестового ящика: study.ai_172@mail.ru
# Пароль тестового ящика: NextPassword172

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from pymongo import MongoClient
import pandas as pd

#from pprint import pprint

chrome_options = Options()
chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome(options=chrome_options)

driver.get('https://e.mail.ru')
print('выполнено')

time.sleep(2)
username = driver.find_element_by_name("username")
username.send_keys('study.ai_172@mail.ru')
username.send_keys(Keys.RETURN)
print('выполнено')

time.sleep(2)
password = driver.find_element_by_name("password")
password.send_keys('NextPassword172')
password.send_keys(Keys.ENTER)

last = None
time.sleep(10)
urls = set()

while True:
    letters = driver.find_elements_by_class_name("js-letter-list-item")
    for letter in letters:
        urls.add(letter.get_attribute('href'))
    if letters[-1] != last:
        last = letters[-1]
        actions = ActionChains(driver)
        actions.move_to_element(letters[-1])
        actions.perform()
    else:
        break
    time.sleep(2)

urls = list(urls)

print(len(urls)) # на почте 204 письма - письма с регистрацией 78 штук хранятся в одном письме, и еще 7 штук хранятся в одном письме. В итоге собирается 2 письма.
                 # Не могу понять как открыть каждое письмо с регистрацией.
data_mail = []

for url in urls:
    data = {}
    driver.get(url)
    data['from'] = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, "//div[@class='letter__author']/span"))).text
    data['theme'] = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'thread__subject'))).text
    data['date'] = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'letter__date'))).text
    data['body'] = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'letter__body'))).text
    data_mail.append(data)
    time.sleep(2)
    driver.back()

data_df = pd.DataFrame(data_mail)

client = MongoClient('127.0.0.1', 27017)
mail_db = client['mail_ru']
mail_info = mail_db.mail_info

data_df.reset_index(inplace=True)
mail_info.insert_many(data_df.to_dict('records'))

driver.close()


