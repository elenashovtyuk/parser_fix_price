import scrapy


class FixpriceSpider(scrapy.Spider):
    name = "fixprice"
    allowed_domains = ["fix-price.com"]
    start_urls = ["https://fix-price.com"]

    def parse(self, response):
        pass
