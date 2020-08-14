import scrapy
from spiders.items import data_analysis


class SjjdSpider(scrapy.Spider):
    name = 'sjjd'
    # allowed_domains = ['www.stats.gov.cn/tjsj/sjjd']
    start_urls = ['http://www.stats.gov.cn/tjsj/sjjd/index.html']

    def parse(self, response):
        """
        获取页码，拼接网页链接，拼接所有页面地址。调用页面文章列表函数。
        """
        page_str_css = 'div.main div.center div.center_list ul.center_list_cont li dl.fenye ::text'
        page_str = ''.join(response.css(page_str_css).getall())
        page_count = page_str[page_str.find('共')+1:page_str.find("页")]
        root_url = 'http://www.stats.gov.cn/tjsj/sjjd/'
        for i in range(int(page_count)):
            if i == 0:   # 第一页index.html 第二页index_1.html
                page_url = 'index.html'
            else:
                page_url = 'index_' + str(i) + '.html'
            url = root_url + page_url
            yield response.follow(url=url, callback=self.parse_doc_list)

    def parse_doc_list(self, response):
        """
        解析网页文章列表，调用文章内容解析函数。
        """
        doc_list_css = 'div.main div.center div.center_list ul.center_list_cont li span.cont_tit a::attr("href")'
        doc_url_list = response.css(doc_list_css).getall()
        for doc in doc_url_list:
            if doc.find('http') == -1:  # 统计局域外网站不处理
                doc_url = response.urljoin(doc)
                if doc_url is not None:
                    yield response.follow(url=doc_url, callback=self.parse_doc)

    def parse_doc(self, response):
        """
        解析网页文章标题、内容、来源、发布时间。
        """
        doc_title_css = 'div.center_xilan h2.xilan_tit ::text'
        doc_sub_info_css = 'div.center_xilan font.xilan_titf font ::text'
        doc_content_p_css = 'div.TRS_PreAppend p'
        doc_title = response.css(doc_title_css).get()
        doc_info = ''.join(response.css(doc_sub_info_css).getall())
        doc_real_source = doc_info[doc_info.find('来源')+3:doc_info.find('发布时间')]
        doc_pub_time = doc_info[doc_info.find('发布时间')+5:].replace('\n', '').replace('\t', '').replace('\xa0', '')
        doc_content = ''
        for content in response.css(doc_content_p_css):
            content_text = ''.join(content.css('::text').getall())
            if content_text != '':
                doc_content = doc_content + content_text + '\n'
        doc = data_analysis()
        doc['doc_url'] = response.url
        doc['doc_title'] = doc_title
        doc['doc_pub_source'] = '国家统计局'
        doc['doc_source'] = doc_real_source
        doc['doc_pub_time'] = doc_pub_time
        doc['doc_content'] = doc_content
        doc['doc_content_source'] = str(response.css('div.center').get())
        yield doc
