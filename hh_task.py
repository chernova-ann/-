from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import re
import pandas as pd
user_agent = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'}


def salary_func(salary):
    salary_currency = re.findall(r'\s(.[A-Zа-я]+)', salary)
    if '-' in salary:
        salary_min = int(''.join(re.findall('\d', salary.split('-')[0])))
        salary_max = int(''.join(re.findall('\d', salary.split('-')[1])))
    elif 'от' in salary:
        salary_min = int(''.join(re.findall('\d', salary)))
        salary_max = None
    elif 'до ' in salary:
        salary_min = None
        salary_max = int(''.join(re.findall('\d', salary)))
    else:
        salary_min, salary_max, salary_currency = None, None, None
    return salary_min, salary_max, salary_currency

vacancy = input('Введите название вакансии: ')
# source_job = input('Введите сайт hh или sj: ')

params_dict = {'hh': {'host': 'https://hh.ru',
                    'path': '/search/vacancy',
                    'params_url': {'clusters':'true', 'area':'1', 'search_field':'name', 'enable_snippets':'true', 'salary':'',
                                   'st':'searchVacancy', 'fromSearch':'true', 'text': vacancy, 'page': 0},
                    'vacancy_list_tag': 'div',
                    'vacancy_list_class': {'class':'vacancy-serp-item'},
                    'next_page_link_tag': 'a',
                    'next_page_link_class': {'class': 'HH-Pager-Controls-Next'},
                    'vacancy_name_tag': 'a',
                    'vacancy_name_class': {'class':'HH-LinkModifier'},
                    'vacancy_salary_tag': 'div',
                    'vacancy_salary_class': {'class': 'vacancy-serp-item__sidebar'},
                    'vacancy_link_class': {'class': 'HH-LinkModifier'},
                    'vacancy_employer_tag': 'a',
                    'vacancy_employer_class': {'class': 'bloko-link_secondary'},
                    'stop_word':'дальше'
                    },
               'sj': {'host': 'https://russia.superjob.ru' ,
                      'path': '/vacancy/search/',
                      'params_url': {'keywords': vacancy, 'geo%5Bt%5D%5B0%5D': 4, 'page': 1},  
                      'vacancy_list_tag': 'div',
                      'vacancy_list_class': {'class' : 'f-test-vacancy-item'},
                      'next_page_link_tag': 'span',
                      'next_page_link_class': {'class': '_3IDf-'},
                      'vacancy_name_tag': 'div',
                      'vacancy_name_class': {'class':'_3mfro PlM3e _2JVkc _3LJqf'},
                      'vacancy_salary_tag': 'span',
                      'vacancy_salary_class': {'class': 'f-test-text-company-item-salary'},
                      'vacancy_link_class': {'class': '_6AfZ9'},
                      'vacancy_employer_tag': 'span',
                      'vacancy_employer_class': {'class': 'f-test-text-vacancy-item-company-name'},
                      'stop_word': 'Дальше'
                      }
               }
               
def text_none(args):
    if args != None:
       args = args.getText()
    else:
        args = args
    return args 
    
def parse_vacancies(source):
    i = 0
    count = 0
    next_page = True
    vacancies = []
    while next_page == True:
        params_dict[source]['params_url']['page'] = i
        response = requests.get(params_dict[source]['host'] + params_dict[source]['path'], params=params_dict[source]['params_url'], headers=user_agent)
        soup = bs(response.text, 'lxml')
        vacancy_list = soup.find_all(params_dict[source]['vacancy_list_tag'], params_dict[source]['vacancy_list_class'])
        next_page_link = soup.find(params_dict[source]['next_page_link_tag'], params_dict[source]['next_page_link_class'])
        text_none(next_page_link)
        if len(vacancy_list) > 0:
            for vacancy in vacancy_list:
                vacancy_data = {}
#               vacancy_data['number'] = count
                vacancy_data['name'] = vacancy.find(params_dict[source]['vacancy_name_tag'], params_dict[source]['vacancy_name_class']).getText()
                salary = vacancy.find(params_dict[source]['vacancy_salary_tag'], params_dict[source]['vacancy_salary_class']).getText()
                salary_min, salary_max, salary_currency = salary_func(salary)
                vacancy_data['salary_min'] = salary_min
                vacancy_data['salary_max'] = salary_max
                vacancy_data['salary_currency'] = salary_currency
                vacancy_data['link'] = vacancy.find('a', params_dict[source]['vacancy_link_class'])['href']
                if not vacancy_data['link'].startswith(params_dict[source]['host']):
                    vacancy_data['link'] = params_dict[source]['host'] + vacancy_data['link']
                vacancy_data['source'] = params_dict[source]['host']
                employer = vacancy.find(params_dict[source]['vacancy_employer_tag'], params_dict[source]['vacancy_employer_class'])
                vacancy_data['employer'] = text_none(employer)
                vacancies.append(vacancy_data)
                count += 1
        else:
            print('Ничего не найдено')
        if next_page_link != params_dict[source]['stop_word'] or next_page_link == None:
           next_page = False
        else:
            i += 1
      # print(f'i += {i}')
      # print(f'{next_page}')
    return vacancies 
    #print(f'Счетчик: {count}')
    
hh_df = pd.DataFrame(parse_vacancies('hh'))
# print('hh обработан')
sj_df = pd.DataFrame(parse_vacancies('sj'))

vacancies_df = hh_df.append(sj_df, ignore_index = True)

print(vacancies_df)

