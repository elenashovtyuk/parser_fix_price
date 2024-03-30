import json


class ParserFpPipeline:

    def process_item(self, item, spider):
        for value in item:
            line = json.dumps(dict(item)) + "\n"
            self.file.write(line)
            return item

    def open_spider(self, spider):
        self.file = open('data.json', 'w', encoding='utf-8')

    def close_spider(self, spider):
        self.file.close()
