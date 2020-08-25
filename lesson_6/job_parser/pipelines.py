# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import re
class JobParserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacansy

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        if spider.name == 'hhru':
            salary = item['salary']
            item['min_salary'],item['max_salary'],item['cur'] = self.process_salary(salary)
        else:
            salary = item['salary']
            item['min_salary'], item['max_salary'], item['cur'] = self.process_salary(salary)

        del item['salary']

        collection.insert_one(item)
        return item

    def process_salary(self, salary):
        cur = re.findall(r'\s(.[A-Zа-я]+)', salary)
        if '-' in salary:
            min_salary = int(''.join(re.findall('\d', salary.split('-')[0])))
            max_salary = int(''.join(re.findall('\d', salary.split('-')[1])))
        elif len(salary) == 1:
            min_salary, max_salary, currency = None, None, None
        elif len(salary) == 7:
            min_salary = int(salary[1].replace('\xa0', ''))
            max_salary = int(salary[3].replace('\xa0', ''))
            cur = salary[5]
        elif len(salary) == 4:
            min_salary = int(salary[0].replace('\xa0', ''))
            max_salary = int(salary[1].replace('\xa0', ''))
            cur = salary[3]
        elif 'от' in salary:
            min_salary = int(''.join(re.findall('\d', salary)))
            max_salary = None
        elif 'до ' in salary:
            min_salary = None
            max_salary = int(''.join(re.findall('\d', salary)))
        else:
            min_salary, max_salary, cur = None, None, None
        return min_salary, max_salary, cur