# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class dir_item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    dbcode = scrapy.Field()
    id = scrapy.Field()
    isparent = scrapy.Field()
    name = scrapy.Field()
    pid = scrapy.Field()
    wdcode = scrapy.Field()
    datasource = scrapy.Field()


class data_item(scrapy.Item):
    dbcode = scrapy.Field()
    code = scrapy.Field()
    data = scrapy.Field()
    dotcount = scrapy.Field()
    hasdata = scrapy.Field()
    strdata = scrapy.Field()
    zbcode = scrapy.Field()
    sjcode = scrapy.Field()
    regcode = scrapy.Field()
    datasource = scrapy.Field()
    pid = scrapy.Field()


class meta_item(scrapy.Item):
    cname = scrapy.Field()
    code = scrapy.Field()
    dotcount = scrapy.Field()
    exp = scrapy.Field()
    ifshowcode = scrapy.Field()
    memo = scrapy.Field()
    name = scrapy.Field()
    nodesort = scrapy.Field()
    sortcode = scrapy.Field()
    tag = scrapy.Field()
    unit = scrapy.Field()
    dbcode = scrapy.Field()
    datasource = scrapy.Field()
    type = scrapy.Field()
    pid = scrapy.Field()


class reg_item(scrapy.Item):
    code = scrapy.Field()
    name = scrapy.Field()


class data_analysis(scrapy.Item):
    doc_url = scrapy.Field()
    doc_title = scrapy.Field()
    doc_pub_source = scrapy.Field()
    doc_source = scrapy.Field()
    doc_pub_time = scrapy.Field()
    doc_content = scrapy.Field()
    doc_content_source = scrapy.Field()