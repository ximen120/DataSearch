import scrapy


class ZcwjkSpider(scrapy.Spider):
    name = 'zcwjk'
    allowed_domains = ['sousuo.gov.cn']
    start_urls = ['http://sousuo.gov.cn/a.htm?t=zhengce']

    def parse(self, response):
        pass
