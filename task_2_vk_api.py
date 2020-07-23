# 2. Изучить список открытых API.
# Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.
import requests
from pprint import pprint
# https://oauth.vk.com/blank.html
#access_token =

main_link = 'https://api.vk.com/method/users.get?v=5.52&access_token='
response_1 = requests.get(main_link)
if response_1.ok:
   with open('response_vk.json', 'wb') as f:
        f.write(response_1.content)
pprint(response_1.json())

main_link = 'https://api.vk.com/method/account.getProfileInfo?v=5.52&access_token='
response_2 = requests.get(main_link)
if response_2.ok:
   with open('response_vk.json', 'ab') as f:
        f.write(response_2.content)
pprint(response_2.json())


