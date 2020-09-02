# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
import scrapy


class LeroymerlinPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.leroymerlin

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

class LeroyPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1]['path'] for itm in results if itm[0]]
        return item

class LeroyCharactPipeline:
    def process_item(self, item, spider):
        if item['charact_name'] and item['charact_value']:
            item['characteristics'] = {}

            for name, val in zip(item['charact_name'], item['charact_value']):
                item['characteristics'][name] = val

        item.pop('charact_name')
        item.pop('charact_value')
        item['price'] = item['price'][0]
        item['link'] = item['link'][0]
        return item




