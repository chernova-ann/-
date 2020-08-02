# 1. Посмотреть документацию к API GitHub,
# разобраться как вывести список репозиториев для конкретного пользователя, сохранить JSON-вывод в файле *.json.
import requests
from pprint import pprint

main_link = 'https://api.github.com/users/'
user_name = 'chernova-ann/repos'
response = requests.get(main_link+user_name)
if response.ok:
   with open('response_git.json', 'wb') as f:
        f.write(response.content)
pprint(response.json()) #В полученном словаре обнаружила, что названия указаны в ключе 'name'. Пользователь + название репозитория - ключ 'full_name'

data = response.json()
count = 0
for i in range(len(data)):
   print(i + 1, data[i]['name'])
   count += 1
print(f'Всего {count} репозиториев')




