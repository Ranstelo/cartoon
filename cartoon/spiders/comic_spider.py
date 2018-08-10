import scrapy
from scrapy import Selector
from cartoon.items import CartoonItem
import re
import time

class ComicSpider(scrapy.Spider):
    name='comic'

    def __init__(self):
        self.server_img = 'http://n.1whour.com/'
        self.server_link = 'http://comic.kukudm.com'
        self.allowed_domains = ['comic.kukudm.com']
        self.start_urls = ['http://comic.kukudm.com/comiclist/3/']
        self.pattern_img = re.compile(r'\+"(.+)\'><span')

    def start_requests(self):

        yield scrapy.Request(url=self.start_urls[0],callback=self.parse1)

    def parse1(self, response):

        hxs = Selector(response)
        items = []
        urls = hxs.xpath('//dd/a[1]/@href').extract() # 章节url
        dir_names = hxs.xpath('//dd/a[1]/text()').extract() # 章节名称
        for index in range(len(urls)):
            item = CartoonItem()

            item["link_url"] = self.server_link + urls[index]
            item["dir_name"] = dir_names[index]
            items.append(item)
        for item in items:
            print("="*100)
            print(item)
            yield scrapy.Request(url=item["link_url"],meta={"item":item},callback=self.parse2)

    def parse2(self, response):
        item = response.meta['item']
        item['link_url'] = response.url
        hxs = Selector(response)
        pre_img_url = hxs.xpath('//script/text()').extract()
        img_url = [self.server_img + re.findall(self.pattern_img, pre_img_url[0])[0]]
        item["img_url"] = img_url
        yield item
        page_num = hxs.xpath('//td[@valign="top"]/text()').re(u'共(\d+)页')[0]
        pre_link = item['link_url'][:-5]
        for each_link in range(2, int(page_num) + 1):
            new_link = pre_link + str(each_link) + '.htm'
            # 根据本章节其他页码的链接发送Request请求，用于解析其他页码的图片链接，并传递item
            yield scrapy.Request(url=new_link, meta={'item': item}, callback=self.parse3)

    def parse3(self, response):
        item = response.meta['item']
        # 获取该页面的链接
        item['link_url'] = response.url
        hxs = Selector(response)
        pre_img_url = hxs.xpath('//script/text()').extract()
        # 注意这里返回的图片地址,应该为列表,否则会报错
        img_url = [self.server_img + re.findall(self.pattern_img, pre_img_url[0])[0]]
        # 将获取的图片链接保存到img_url中
        item['img_url'] = img_url
        # 返回item，交给item pipeline下载图片
        yield item



