import scrapy
import json
from spiders.items import dir_item, data_item, meta_item, reg_item


class StatsDataSpider(scrapy.Spider):
    name = 'stats_data'
    allowed_domains = ['data.stats.gov.cn']
    start_urls = ['http://data.stats.gov.cn/']

    def parse(self, response):
        """
        爬取的数据种类在dbcode字典中，其中前三个为国家数据，需要默认赋值地区为国家，后面为分地区数据，从数据中获取地区。
        本方法的主要目的是拼接指标分类访问地址，然后回调dir_parse，获取指标分类信息。
        获取根节点目录的地址：http://data.stats.gov.cn/easyquery.htm?id=zb&dbcode=hgyd&wdcode=zb&m=getTree。替换其中的dbcode即可
        """
        dbcode = {
            'hgyd': '月度数据',
            'hgjd': '季度数据',
            'hgnd': '年度数据',
            'fsyd': '分省月度数据',
            'fsjd': '分省季度数据',
            'fsnd': '分省年度数据',
            'csyd': '主要城市月度价格',
            'csnd': '主要城市年度数据',
            'gatyd': '港澳台月度数据',
            'gatnd': '港澳台年度数据',
            'gjyd': '主要国家（地区）月度数据',
            'gjydsdj': '三大经济体月度数据',
            'gjydsc': '国际市场月度商品价格',
            'gjnd': '主要国家（地区）年度数据',
        }
        url_zb = 'http://data.stats.gov.cn/easyquery.htm'
        form_data = {'id': 'zb', 'dbcode': 'dbname', 'wdcode': 'zb', 'm': 'getTree'}
        for db in dbcode.keys():
            form_data['dbcode'] = db
            yield scrapy.FormRequest(url_zb, formdata=form_data, method='POST',
                                     callback=self.dir_parse)

    def dir_parse(self, response):
        """
        本方法的目的为获取指标分类，非叶子节点则重复获取分类，
        叶子节点则除前三个默认地区是国家，直接请求数据外，其他均需要回调reg_parse请求对应的地区信息。
        请求下级目录的地址：http://data.stats.gov.cn/easyquery.htm?id=A02&dbcode=hgyd&wdcode=zb&m=getTree
        请求数据的地址：http://data.stats.gov.cn/easyquery.htm
        m: QueryData
        dbcode: fsnd
        rowcode: zb
        colcode: sj
        wds: [{"wdcode":"reg","valuecode":"110000"}]
        dfwds: [{"wdcode":"zb","valuecode":"A0201"}，{"wdcode":"sj","valuecode":"2015-"}]
        请求地区的地址：http://data.stats.gov.cn/easyquery.htm
        m: getOtherWds
        dbcode: fsnd
        rowcode: zb
        colcode: sj
        wds: [{"wdcode":"zb","valuecode":"A0201"}]
        """
        res = json.loads(response.text)
        for zb_dir in res:
            doc = dir_item()
            for key in zb_dir.keys():
                if key == 'isParent':
                    doc['isparent'] = zb_dir[key]
                else:
                    doc[key] = str(zb_dir[key])
            doc['datasource'] = '国家统计局'
            if doc['isparent']:
                url_zb_t = str('http://data.stats.gov.cn/easyquery.htm')
                form_data = dict({'id': 'zb', 'dbcode': 'dbname', 'wdcode': 'zb', 'm': 'getTree'})
                form_data['id'] = doc['id']
                form_data['dbcode'] = doc['dbcode']
                yield scrapy.FormRequest(url_zb_t, formdata=form_data, method='POST',
                                         callback=self.dir_parse)
            else:
                if doc['dbcode'] in ['hgyd', 'hgjd', 'hgnd']:
                    regcode = '000000'
                    url1 = 'http://data.stats.gov.cn/easyquery.htm?m=QueryData&dbcode='
                    url2 = str(doc['dbcode']) + '&rowcode=zb&colcode=sj&wds=[]&dfwds=[{"wdcode":"zb","valuecode":"'
                    url3 = str(doc['id']) + '"},{"wdcode":"sj","valuecode":"1900-"}]'
                    url_data = url1 + url2 + url3
                    yield response.follow(url=url_data, callback=self.data_parse, meta={'regcode': regcode,
                                                                            'dbcode': doc['dbcode'], 'pid': doc['id']})
                else:
                    url4 = 'http://data.stats.gov.cn/easyquery.htm?m=getOtherWds&dbcode='
                    url5 = str(doc['dbcode']) + '&rowcode=zb&colcode=sj&wds=[]&dfwds: [{"wdcode":"zb","valuecode":"' \
                           + str(doc['id']) +'"]'
                    url_reg = url4 + url5
                    yield response.follow(url=url_reg, callback=self.reg_parse, meta={'dbcode': doc['dbcode'],
                                                                                      'zbcode': doc['id']})
            yield doc

    def reg_parse(self, response):
        zbcode = response.meta['zbcode']
        dbcode = response.meta['dbcode']
        res = json.loads(response.text)
        for regs in res['returndata']:
            if not regs['issj']:
                for reg in regs['nodes']:
                    regmeta = reg_item()
                    regmeta['code'] = reg['code']
                    regmeta['name'] = reg['name']
                    yield regmeta
                    url6 = 'http://data.stats.gov.cn/easyquery.htm?m=QueryData&dbcode='
                    url7 = str(dbcode) + '&rowcode=zb&colcode=sj&wds=[{"wdcode":"reg","valuecode":"' + str(reg['code'])
                    url8 = '"}]&dfwds=[{"wdcode":"zb","valuecode":"' + str(zbcode)
                    url9 = '"},{"wdcode":"sj","valuecode":"1900-"}]'
                    url_reg_data = url6 + url7 + url8 + url9
                    yield response.follow(url=url_reg_data, callback=self.data_parse,
                                          meta={'regcode': reg['code'], 'dbcode': dbcode, 'pid': zbcode})

    def data_parse(self, response):
        """
        本方法的目的是为了解析指标元数据、时间元数据、地区元数据，以及具体的统计指标数据。
        :param response:
        :return:
        """
        regcode = response.meta['regcode']
        dbcode = response.meta['dbcode']
        pid = response.meta['pid']
        res = json.loads(response.text)
        for datas in res['returndata']['datanodes']:
            dt = data_item()
            if datas['data']['hasdata']:
                dt['dbcode'] = dbcode
                dt['regcode'] = regcode
                dt['pid'] = pid
                dt['datasource'] = '国家统计局'
                dt['code'] = datas['code']
                dt['data'] = datas['data']['data']
                dt['dotcount'] = datas['data']['dotcount']
                dt['hasdata'] = datas['data']['hasdata']
                dt['strdata'] = datas['data']['strdata']
                for meta in datas['wds']:
                    if meta['wdcode'] == 'zb':
                        dt['zbcode'] = meta['valuecode']
                    elif meta['wdcode'] == 'sj':
                        dt['sjcode'] = meta['valuecode']
                yield dt

        for metas in res['returndata']['wdnodes']:
            if metas['wdcode'] == 'zb':
                m_type = 'zb'
            elif metas['wdcode'] == 'sj':
                m_type = 'sj'
            elif metas['wdcode'] == 'reg':
                m_type = 'reg'
            for zb_meta in metas['nodes']:
                zm = meta_item()
                for key in zb_meta.keys():
                    zm[key] = str(zb_meta[key])
                zm['dbcode'] = dbcode
                zm['datasource'] = '国家统计局'
                zm['type'] = m_type
                if m_type == 'zb':
                    zm['pid'] = pid
                else:
                    zm['pid'] = ''
                yield zm
