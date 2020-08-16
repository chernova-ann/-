# 2) Написать программу, которая собирает «Хиты продаж» с сайта техники mvideo и складывает данные в БД.
#    Магазины можно выбрать свои. Главный критерий выбора: динамически загружаемые товары
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
import time

chrome_options = Options()
chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome(options=chrome_options)

driver.get('https://www.mvideo.ru/')

time.sleep(5)
item_xpath = "//div[contains(text(), 'Хиты продаж')]/../../.."
next_button = "//a[contains(@class, 'sel-hits-button-next')]"
product_info = "//li[contains(@class, 'gallery-list-item')]//h4"

button = WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.XPATH, item_xpath + next_button)))

action = ActionChains(driver)
action.move_to_element(button)
action.perform()


while True:
    if button.is_displayed():
        button.click()
        time.sleep(2)
    else:
        break

products = driver.find_elements_by_xpath(item_xpath + product_info)

data_products = []

for product in products:
    data_products.append(product.get_attribute('data-product-info'))

client = MongoClient('127.0.0.1', 27017)
mvideo_db = client['mvideo']
hit_sail = mvideo_db.hit_sail

for product in data_products:
    item = {'product': product}
    hit_sail.insert_one(item)

for hit in hit_sail:
    print(hit)

driver.close()
