# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from spiders.settings import POSTGRES_DB, POSTGRES_PORT, POSTGRES_PW, POSTGRES_SERVER, POSTGRES_USER
from spiders.items import reg_item, data_item, meta_item, dir_item, data_analysis
import psycopg2


class SpidersPipeline:
    def __init__(self):
        self.connection = psycopg2.connect(
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PW,
            host=POSTGRES_SERVER,
            port=POSTGRES_PORT
        )
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        self.connection.close()

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
        item_list = item.fields.keys()
        insert_sql = """insert into {0}({1}) values ({2})""".format(tab_name,
                                                                    ', '.join(item_list),
                                                                    ', '.join(['%s'] * len(item.fields.keys())))
        value = []
        for key in item_list:
            value.append(item[key])
        try:
            self.cursor.execute(insert_sql, tuple(value))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            # print('数据插入失败')
            # print(e)
        return item
