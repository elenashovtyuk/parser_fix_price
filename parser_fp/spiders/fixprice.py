import scrapy
import urllib.parse
from ..items import ProductItem
from typing import List


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

    # создаем список категорий
    # добавляем в него требуемые по ТЗ категории из start_urls
    # аттрибут url приравнивае к адресу категории
    # остальные аттрибуты оставляем дефолтными
    # номер страницы, наполненность, список товаров для категории
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
        # если категория не совпадает, ищем дальше
        for index, category in enumerate(self.categories):
            if category.url != response.url.split('?')[0]:
                continue

        # если совпадает, ищем div с карточками продуктов
        cards = response.css('div.product__wrapper')

        # из каждой карточки в div достаем ссылку на адрес страницы продукта
        for card in cards:
            product_url = card.css(
                'div.product__wrapper a.title::attr(href)').get()
            # добавляем ссылку на страницу продукта в список ссылок в Категории
            self.categories[index].product_urls.append(
                urllib.parse.urljoin(
                    base='https://fix-price.com',
                    url=product_url
                )
            )
        # если список ссылок страниц товаров не полон(<70),
        # то есть, параметр is_complete = False
        # парсим следующую страницу для Категории
        if not self.categories[index].is_complete:
            # проверяем кол-во урлов в списке урлов со страницами товаров
            # для текущей категории
            # если кол-ко больше 70,
            # то для параметра is_complete меняем флаг на True
            # то есть, список полон
            if len(self.categories[index].product_urls) > PRODUCT_MAX_COUNT:
                self.categories[index].is_complete = True
            # если же кол-во собраных страниц товаров меньше 70, то
            # переходим на следующую страницу категории и
            # собираем ссылки страниц товаров далее
            # также меняем аттрибут page_count  в  Категории(прибавляем 1)
            self.categories[index].page_count += 1
            # собираем ссылки на все следующие страницы
            next_pages = response.css(
                    'a[data-component="VPaginationItem"]::attr(href)').getall()
            # если следующие страницы есть и кол-во страниц
            # для Категории меньше кол-ва полученных
            # переходим на следующую страницу и повторяем для нее
            # все действия метода parse_link снова
            if next_pages and self.categories[index].page_count < len(next_pages):
                yield response.follow(
                    next_pages[self.categories[index].page_count],
                    callback=self.parse_link)
        # когда собрали достаточное кол-во страниц товаров для категории,
        # начинаем парсить их, собирать информацию о товарах
        if self.categories[index].is_complete:
            # передаем в метод parse_product объект Request по каждому адресу
            for url in self.categories[index].product_urls:
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

                'description': response.css(
                    'div.product-details div.description::text'
                ).get(),

                'SKU': response.css(
                    'p.property span.value::text'
                ).get(),

                'wigth': response.css(
                    'div.properties p.property span.value::text'
                ).getall()[3],

                'height': response.css(
                    'div.properties p.property span.value::text'
                ).getall()[-4],

                'length': response.css(
                    'div.properties p.property span.value::text'
                ).getall()[-3],

                'weight': response.css(
                    'div.properties p.property span.value::text'
                ).getall()[-2],

                'country': response.css(
                    'div.properties p.property span.value::text'
                ).getall()[-1]
            },

            'variants': ''

        }
        yield ProductItem(products_data)
