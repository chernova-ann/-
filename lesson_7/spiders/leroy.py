import scrapy
from scrapy.http import HtmlResponse
from leroymerlin.items import LeroymerlinItem
from scrapy.loader import ItemLoader

class LeroySpider(scrapy.Spider):
    name = 'leroy'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        super().__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response:HtmlResponse):
        next_page = response.xpath("//a[contains(@class,'next-paginator-button')]/@href").extract_first()
        ads_links = response.xpath("//product-card/@data-product-url")
        for link in ads_links:
            yield response.follow(link,callback=self.parse_ads)
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_ads(self,response:HtmlResponse):
        loader = ItemLoader(item=LeroymerlinItem(),response=response)
        loader.add_xpath('name',"//h1/text()")
        loader.add_xpath('photos',"//source[contains(@media, 'min-width: 1024px')]/@srcset")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('currency', "//meta[@itemprop='priceCurrency']/@content")
        loader.add_xpath('link', "//link[@itemprop='url']/@href")
        loader.add_xpath('charact_name', "//dl//dt/text()")
        loader.add_xpath('charact_value', "//dl//dd/text()")
        yield loader.load_item()



