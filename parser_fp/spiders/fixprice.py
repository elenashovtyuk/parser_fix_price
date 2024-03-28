import scrapy
import urllib.parse
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
            yield scrapy.Request(url=url, callback=self.parse_link)

    def parse_link(self, response):
        """
        Метод обратного вызова.
        Извлекает ссылки на каждый товар из карточек товара.
        """
        # получаем div с карточками продуктов
        cards = response.css('div.product__wrapper')

        product_urls = []
        # из каждой карточки в div достаем ссылку на адрес страницы продукта
        for card in cards:
            product_url = response.css(
                'div.product__wrapper a.title::attr(href)').get()
            # и добавляем ее в список с ссылками product_urls
            product_urls.append(urllib.parse.urljoin(base='https://fix-price.com', url=product_url))
            # далее передаем объект Request по каждому адресу(по каждой ссылке на отдельный товар
            # в метод обратного вызова parse_product
            for url in product_urls:
                yield scrapy.Request(url=url, callback=self.parse_product)

    def parse_product(self, response):
        """
        Метод обратного вызова.
        Извлекает информацию о каждом товаре c его страницы.
        """
        #data_products = []

        products_data = {
            'title': response.css('h1.title::text').get()
        }
        yield ProductItem(products_data)






 # next_page = response.css('a.next::attr(href)').get()
        # yield response.follow(next_page, callback=self.parse_product)
        #     # если же кол-во ссылок достигло 70, то работаем с каждой ссылкой
        #     # для получения информации о каждом продукте в следующем методе
        #     # - parse_product
        #     # for url in self.product_urls:
        #     #     yield scrapy.Request(url=url, callback=self.parse_product)
