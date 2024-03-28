import scrapy
from ..items import ProductItem


class FixpriceSpider(scrapy.Spider):
    name = "fixprice"
    allowed_domains = ["fix-price.com"]
    start_urls = [
        "https://fix-price.com/catalog/kosmetika-i-gigiena/ukhod-za-polostyu-rta",
        "https://fix-price.com/catalog/kosmetika-i-gigiena/gigienicheskie-sredstva",
        "https://fix-price.com/catalog/krasota-i-zdorove/dlya-tela"
    ]

    def start_requests(self):
        """
        Метод вызова стартовых адресов из списка.
        Передает объект Request по каждому адресу в метод parse().
        """
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """
        Метод обратного вызова.
        Извлекает информацию о каждом товаре по каждой категории.
        """
        products = response.css('div.product__wrapper')
        for product in products:
            product_data = {
                'title': response.css('a.title::text').get(),
            }
        yield ProductItem(product_data)



        #     item = ProductItem()
        #     item['title'] = response.css('div.product__wrapper a.title::text').get()
        # yield item
