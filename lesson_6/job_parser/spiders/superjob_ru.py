import scrapy
from scrapy.http import HtmlResponse
from job_parser.items import JobParserItem


class SuperjobRuSpider(scrapy.Spider):
    name = 'superjob_ru'
    allowed_domains = ['superjob.ru']

    def __init__(self, vacancy=None):
        super(SuperjobRuSpider, self).__init__()
        self.start_urls = [f'https://krasnogorsk.superjob.ru/vacancy/search/?keywords={vacancy}']

    def parse(self, response):
        next_page = response.css('a.f-test-link-dalshe::attr(href)').extract_first()
        vacancy_links = response.css('a._6AfZ9::attr(href)').extract()
        for link in vacancy_links:
            yield response.follow(link,callback=self.vacancy_parse)
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.css('h1 ::text').extract()
        salary = response.xpath('//span[@class="_3mfro _2Wp8I PlM3e _2JVkc"]/text()').extract()
        vacancy_link = response.url
        site_scraping = self.allowed_domains[0]

        yield JobParserItem(name=name,salary=salary,vacancy_link=vacancy_link,site_scraping=site_scraping)
