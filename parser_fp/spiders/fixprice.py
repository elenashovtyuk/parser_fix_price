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
    data = []

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
        Собирает ссылки на каждый товар из карточек товара.
        Передает их в метод parse_product для получения информации о продукте.
        """
        # получаем div с карточками продуктов
        cards = response.css('div.product__wrapper')

        product_urls = []
        # из каждой карточки в div достаем ссылку на адрес страницы продукта
        for card in cards:
            product_url = card.css(
                'div.product__wrapper a.title::attr(href)').get()
            # и добавляем ее в список с ссылками product_urls
            product_urls.append(urllib.parse.urljoin(base='https://fix-price.com', url=product_url))

            # передаем в метод parse_product объект Request по каждому адресу
            for url in product_urls:
                yield scrapy.Request(url=url, callback=self.parse_product)

    def parse_product(self, response):
        """
        Метод обратного вызова.
        Извлекает информацию о каждом товаре c его страницы.
        Возвращает ее в виде объекта Item согласно заданному шаблону
        """
        products_data = {
            'title': response.css('h1.title::text').get()
        }
        yield ProductItem(products_data)






            # # если кол-во ссылок в списке меньше 70
            # #  то находим ссылку на следующую страницу и повторяем все действия метода parse_link
            # # для нее(если следующая страница есть)
            # if len(product_urls) < 70:
            #     next_page = card.css('a.next::attr(href)').get()
            #     if next_page:
            #         yield response.follow(next_page, callback=self.parse_link)
            # # в противном случае (если ссылок 70 и больше
