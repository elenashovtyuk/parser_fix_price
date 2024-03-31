import scrapy
import urllib.parse
from ..items import ProductItem
from typing import List
import datetime

PRODUCT_MAX_COUNT = 70


class Category():
    def __init__(self):
        self.url: str = ""
        self.page_count: int = 0
        self.is_complete: bool = False
        self.product_urls: List[str] = []


class FixpriceSpider(scrapy.Spider):
    name = "fixprice"
    allowed_domains = ["fix-price.com"]
    start_urls = [
        "https://fix-price.com/catalog/kosmetika-i-gigiena/ukhod-za-polostyu-rta",
        "https://fix-price.com/catalog/kosmetika-i-gigiena/gigienicheskie-sredstva",
        "https://fix-price.com/catalog/krasota-i-zdorove/dlya-tela"
    ]

    cookies = {"locality": urllib.parse.quote(
        '{"city":"Екатеринбург","cityId":55,"longitude":60.597474,"latitude":56.838011,"prefix":"г"}')}

    categories = []
    for url in start_urls:
        new_category = Category()
        new_category.url = url
        categories.append(new_category)

    def start_requests(self):
        """
        Метод вызова стартовых адресов из списка.
        Передает объект Request по каждому адресу в метод parse().
        """
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                cookies=self.cookies,
                callback=self.parse_link
            )

    def parse_link(self, response):
        """
        Метод обратного вызова.
        Собирает ссылки на каждый товар из карточек товара.
        Передает их в метод parse_product для получения информации о продукте.
        """
        for index, category in enumerate(self.categories):
            if category.url != response.url.split('?')[0]:
                continue

        cards = response.css('div.product__wrapper')

        for card in cards:
            product_url = card.css(
                'div.product__wrapper a.title::attr(href)').get()
            self.categories[index].product_urls.append(
                urllib.parse.urljoin(
                    base='https://fix-price.com',
                    url=product_url
                )
            )
        if not self.categories[index].is_complete:
            if len(self.categories[index].product_urls) > PRODUCT_MAX_COUNT:
                self.categories[index].is_complete = True
            self.categories[index].page_count += 1
            next_pages = response.css(
                    'a[data-component="VPaginationItem"]::attr(href)').getall()
            if next_pages and self.categories[index].page_count < len(next_pages):
                yield response.follow(
                    next_pages[self.categories[index].page_count],
                    callback=self.parse_link)
            else:
                self.categories[index].is_complete = True

        if self.categories[index].is_complete:
            for url in self.categories[index].product_urls:
                yield scrapy.Request(url=url, callback=self.parse_product)

    def parse_product(self, response):
        """
        Метод обратного вызова.
        Извлекает информацию о каждом товаре c его страницы.
        Возвращает ее в виде объекта Item согласно заданному шаблону
        """
        widths_of_products = response.css('div.properties p.property span.value::text').getall()
        actual_width = ""
        if len(widths_of_products) > 2:
            actual_width = widths_of_products[2]

        heights_of_products = response.css('div.properties p.property span.value::text').getall()
        actual_height = ""
        if len(heights_of_products) > 3:
            actual_height = heights_of_products[3]

        length_of_products = response.css('div.properties p.property span.value::text').getall()
        actual_length = ""
        if len(length_of_products) > 4:
            actual_length = length_of_products[4]

        weights_of_products = response.css('div.properties p.property span.value::text').getall()
        actual_weight = ""
        if len(weights_of_products) > 5:
            actual_weight = weights_of_products[5]

        products_data = {
            'timestamp': datetime.datetime.now().timestamp(),

            'RPC': response.css('p.property span.value::text').get(),

            'url': response.css('div.description a.title::attr(href)').get(),

            'title': response.css('h1.title::text').get(),

            'marketing_tags': response.css(
                'div.isSpecialPrice::text').get(default=""),

            'brand': response.css('p.property a.link::text').get(),

            'section': response.css(
                'div.breadcrumbs span::text'
            ).getall()[:-1],

            'price_data': {

                'current': response.css(
                    'div.price-in-cart .special-price::text'
                ).get(),

                'original': response.css(
                    'div.price-in-cart .old-price::text'
                ).get(),

                'sale_tag': ''
            },

            'stock': {
                'in_stock': '',
                'count': ''
            },

            'assets': {

                'main_image': response.css(
                    'div.zoom-on-hover link::attr(href)'
                ).get(),

                'set_images': response.css(
                    '.product-images .swiper-slide link::attr(href)'
                ).getall(),

                'view360': '',
                'video': ''
            },
            'metadata': {

                '__description': response.css(
                    'div.product-details div.description::text'
                ).get(),

                'SKU': response.css(
                    'p.property span.value::text'
                ).get(),

                'width': actual_width,

                'height': actual_height,

                'length': actual_length,

                'weight': actual_weight,

                'country': response.css(
                    'div.properties p.property span.value::text'
                ).getall()[-1]
            },

            'variants': len(response.css(
                '.product-images .swiper-slide link::attr(href)'
            ).getall())

        }
        yield ProductItem(products_data)
