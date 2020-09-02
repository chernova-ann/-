# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstagramItem(scrapy.Item):
    _id = scrapy.Field()
    user_id = scrapy.Field()
    username = scrapy.Field()
    photo = scrapy.Field()
    follow_type = scrapy.Field()
    follow_id = scrapy.Field()
    user_name = scrapy.Field()
    full_name = scrapy.Field()
