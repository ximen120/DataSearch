# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from spiders.settings import ARANGODB_HOST, USER, PASSWD, ARANGODB_DB
from spiders.items import reg_item, data_item, meta_item, dir_item, data_analysis
from arango import ArangoClient


class SpidersPipeline:
    def __init__(self):
        self.connection = ArangoClient(hosts=ARANGODB_HOST)
        self.db = self.connection.db(ARANGODB_DB, username=USER, password=PASSWD)

    def process_item(self, item, spider):
        if isinstance(item, reg_item):
            tab_name = 'reg_item'
        elif isinstance(item, data_item):
            tab_name = 'data_item'
        elif isinstance(item, meta_item):
            tab_name = 'meta_item'
        elif isinstance(item, dir_item):
            tab_name = 'dir_item'
        elif isinstance(item, data_analysis):
            tab_name = 'data_analysis'
        col = self.db.collection(tab_name)
        try:
            col.insert(dict(item))
        except Exception as e:
            print(e)
        return item
