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
        # div с карточками продуктов
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
            'timestamp': '',
            'RPC': response.css('p.property span.value::text').get(),
            'url': response.css('div.description a.title::attr(href)').get(),
            'title': response.css('h1.title::text').get(),
            'marketing_tags': response.css('div.isSpecialPrice::text').get(default=""),
            'brand': response.css('p.property a.link::text').get(),
            'section': response.css('div.breadcrumbs span::text').getall()[:-1],
            'price_data': {
                'current': response.css('div.price-in-cart .special-price::text').get(),
                'original': response.css('div.price-in-cart .old-price::text').get(),
                'sale_tag': ''
            },
            'stock': {
                'in_stock': '',
                'count': ''
            },
            'assets': {
                'main_image': response.css('div.zoom-on-hover link::attr(href)').get(),
                'set_images': response.css('.product-images .swiper-slide link::attr(href)').getall(),
                'view360': '',
                'video': ''
            },
            'metadata': {
                'description': response.css('div.product-details div.description::text').get(),
                'SKU': response.css('p.property span.value::text').get(),
                'wigth': response.css('div.properties p.property span.value::text').getall()[3],
                'height': response.css('div.properties p.property span.value::text').getall()[-4],
                'length': response.css('div.properties p.property span.value::text').getall()[-3],
                'weight': response.css('div.properties p.property span.value::text').getall()[-2],
                'country': response.css('div.properties p.property span.value::text').getall()[-1]
            },
            'variants': ''

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
