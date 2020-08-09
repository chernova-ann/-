#1)Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex.ru/news
# Для парсинга использовать xpath. Структура данных должна содержать:
# * название источника,
# * наименование новости,
# * ссылку на новость,
# * дата публикации

# 2)Сложить все новости в БД

from lxml import html
import requests
from pprint import pprint
import re
import pandas as pd
from pymongo import MongoClient
import datetime

header = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 YaBrowser/20.7.3.101 Yowser/2.5 Yptp/1.23 Safari/537.36'}

params_dict = {"mail": {"host": "https://news.mail.ru",   # главная ссылка
                    "items": "//div[@class='js-module']//a[contains(@class, 'photo_full')]|//ul[@name='clb20268353']/li[@class='list__item']", # Контейнер с новостями
                    "link": ".//@href",
					"name": ".//text()",
					"time_news" : "//span[@class='note']/span[@datetime]/@datetime",
					"name_source": "//span[@class='note']/a//text()",
					"link_source": "//span[@class='note']/a/@href"					
                    },
				"yandex": {"host": "https://yandex.ru/news",
						"items": "//div[contains(@class, 'news-top-rubric-stories')][1]//article",
						"link": ".//a[@class='news-card__link']/@href",
						"name": ".//a[@class='news-card__link']//text()",
                        "name_source": ".//span[@class='mg-card-source__source']//text()",
                        "link_source": "//a[contains(@class, 'news-story__subtitle')]/@href",
                        "time_news": ".//span[@class='mg-card-source__time']//text()"
						},
				"lenta": {"host": "https://lenta.ru",
				         "items": "//div[@class='span4']/div[contains(@class, 'item')]//time",
                         "link": "./../@href",
						 "name": "./../text()",
                         "name_source": "LENTA.RU",
                         "time_news": "./@datetime"
                         }
				}

def full_link_func(host, arg_1, arg_2):
    if 'http' in arg_1:
        arg_2 = arg_1
    elif '/news' in arg_1:
        arg_2 = host + arg_1[5:]
    else: 
        arg_2 = host + arg_1
    return arg_2

def d_t_func(time_news):
    if '+03:00' in time_news:
        time_news = datetime.datetime.strptime(time_news[:19], "%Y-%m-%dT%H:%M:%S")
        time_news = time_news.strftime('%Y-%m-%d %H:%M')
    elif "вчера" in time_news:
        date_news = str(datetime.date.today() + datetime.timedelta(-1))
        time_news = datetime.datetime.strptime(date_news + time_news[8:], '%Y-%m-%d%H:%M')
        time_news = time_news.strftime('%Y-%m-%d %H:%M')
    elif time_news == None:
        time_news = None
    elif ',' in time_news:
        t_split = time_news.split(', ')
        t = str(datetime.datetime.strptime(t_split[0], ' %H:%M').time())
        d = str(datetime.date.today())
        time_news = datetime.datetime.strptime(d+t, '%Y-%m-%d%H:%M:%S')
        time_news = time_news.strftime('%Y-%m-%d %H:%M')
    else:
        date_news = str(datetime.date.today())
        time_news = datetime.datetime.strptime(date_news + time_news, '%Y-%m-%d%H:%M')
        time_news = time_news.strftime('%Y-%m-%d %H:%M')
    return time_news
         

def parse_news(source):
    response = requests.get(params_dict[source]['host'], headers=header)
    dom = html.fromstring(response.text)
    items = dom.xpath(params_dict[source]['items'])
    count = 1
    news = []
    full_link = None
    for item in items:
        new = {}
        new['count']= count
        link = item.xpath(params_dict[source]['link'])[0]
        full_link = full_link_func(params_dict[source]['host'], link, full_link)
        new['full_link'] = full_link
        new['name'] = item.xpath(params_dict[source]['name'])[0].replace('\xa0',' ')
        if source == 'mail':        
            new_response = requests.get(full_link, headers=header)
            new_dom = html.fromstring(new_response.text)
            time_news = new_dom.xpath(params_dict[source]['time_news'])[0]
            new['time_news'] = d_t_func(time_news)
            new['name_source'] = new_dom.xpath(params_dict[source]['name_source'])[0]
            new['link_source'] = new_dom.xpath(params_dict[source]['link_source'])[0]
        elif source == 'yandex':
            new['name_source'] = item.xpath(params_dict[source]['name_source'])[0]
            new_response = requests.get(full_link, headers=header)
            new_dom = html.fromstring(new_response.text)
            time_news = item.xpath(params_dict[source]['time_news'])[0]
            new['time_news'] = d_t_func(time_news)
            new['link_source'] = new_dom.xpath(params_dict[source]['link_source'])[0]
        else:    
            new['name_source'] = params_dict[source]['name_source']
            time_news = item.xpath(params_dict[source]['time_news'])[0]
            new['time_news'] = d_t_func(time_news)
            new['link_source'] = params_dict[source]['host']
        count += 1
        news.append(new)
    return news    


mail = pd.DataFrame(parse_news('mail'))
yandex = pd.DataFrame(parse_news('yandex'))
lenta = pd.DataFrame(parse_news('lenta'))

news_df = pd.concat([mail, yandex, lenta])

client = MongoClient('127.0.0.1', 27017)
news_db = client['news_db']
news = news_db.news

news_df.reset_index(inplace=True)
news.insert_many(news_df.to_dict('records'))



