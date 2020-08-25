import scrapy
from scrapy.http import HtmlResponse
from job_parser.items import JobParserItem


class HhRuSpider(scrapy.Spider):
    name = 'hh_ru'
    allowed_domains = ['hh.ru']

    def __init__(self, vacancy=None):
        super(HhRuSpider, self).__init__()
        self.start_urls = [f'https://krasnogorsk.hh.ru/search/vacancy?area=1&st=searchVacancy&text={vacancy}']

    def parse(self, response:HtmlResponse):
        next_page = response.xpath("//a[contains(@class,'HH-Pager-Controls-Next')]/@href").extract_first()
        # vacansy_links = response.xpath("//a[@class='bloko-link HH-LinkModifier']/@href")
        vacansy_links = response.css('a.bloko-link.HH-LinkModifier::attr(href)').extract()
        for link in vacansy_links:
            yield response.follow(link,callback=self.vacansy_parse)
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def vacansy_parse(self, response:HtmlResponse):
        name = response.xpath('//h1/text()').extract_first()
        salary = response.xpath("//p[@class='vacancy-salary']/span/text()").extract()
        vacancy_link = response.url
        site_scraping = self.allowed_domains[0]
        yield JobParserItem(name=name,salary=salary,vacancy_link=vacancy_link,site_scraping=site_scraping)



