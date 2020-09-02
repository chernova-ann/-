# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Identity


def process_link(value):
   value = 'https://leroymerlin.ru' + value
   return value

def process_price(value):
    value = value.replace(' ', '')
    return int(value)

def process_character_value(value):
    return value.replace('\n', '').strip()


class LeroymerlinItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=Identity())
    price = scrapy.Field(input_processor=MapCompose(process_price))
    currency = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(input_processor=MapCompose(process_link))
    characteristics = scrapy.Field()
    charact_name = scrapy.Field(output_processor=Identity())
    charact_value = scrapy.Field(input_processor=MapCompose(process_character_value))
