# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json


class ParserFpPipeline:

    def process_item(self, item, spider):
        for value in item:
            line = json.dumps(dict(item)) + "\n"
            self.file.write(line)
            return item

    def open_spider(self, spider):
        self.file = open('fix.json', 'w')

    def close_spider(self, spider):
        self.file.close()
