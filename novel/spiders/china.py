# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http.response.html import HtmlResponse
from ..items import NovelItem, BookItem
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Join, Compose, MapCompose
import time


class NovelLoader(ItemLoader):
    default_output_processor = TakeFirst()


class DescLoader(NovelLoader):
    tags_in = MapCompose(lambda s: s.strip())
    tags_out = Compose(Join(), lambda s: s.replace('  ', ' '), lambda s: s.strip())
    desc_out = Compose(Join(), lambda s: s.replace('\r', '').replace('\n', '').replace(' ', ''))
    title_out = Compose(Join(), lambda s: s.replace('\r', '').replace('\n', '').replace(' ', ''))


class ContentLoader(NovelLoader):
    content_in = MapCompose(lambda s: s.strip())
    content_out = Compose(Join('|'))
    words_out = Compose(lambda s: s[0])
    ctime_out = Compose(lambda s: s[1], lambda s: str2timestamp(s))


def str2timestamp(timestr: str):
    timeArray = time.strptime(timestr, "%Y-%m-%d %H:%M:%S")
    timeStamp = int(time.mktime(timeArray))
    return timeStamp


class ChinaSpider(CrawlSpider):
    name = 'china'
    allowed_domains = ['book.zongheng.com']
    start_urls = ['http://book.zongheng.com/store/c1/c0/b0/u21/p1/v0/s1/t0/u0/i1/ALL.html']
    # start_urls = ['http://book.zongheng.com/book/844165.html']

    rules = (
        Rule(LinkExtractor(allow=r'/book/\d+\.html', restrict_xpaths='//div[@class="bookname"]/a'),
             callback='book_parse_item', follow=True),
        Rule(LinkExtractor(allow=r'/chapter/\d+/\d+\.html',
                           restrict_xpaths='//div[@class="btn-group"]/a[@class="btn read-btn"]'),
             callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'/chapter/\d+/\d+\.html',
                           restrict_xpaths='//div[@class="chap_btnbox"]/a[@class="nextchapter"]'),
             callback='parse_item', follow=True),
    )

    def parse_item(self, response: HtmlResponse):
        loader = ContentLoader(item=NovelItem(), response=response)
        loader.add_xpath('bookname', '//div[@class="reader_crumb"]/a[3]/text()')
        loader.add_xpath('author', '//div[@class="bookinfo"]/a/text()')
        loader.add_xpath('category', '//div[@class="reader_crumb"]/a[2]/text()')
        loader.add_xpath('chapters', '//div[@class="title_txtbox"]/text()')
        loader.add_xpath('content', '//div[@class="content"]/p/text()')
        loader.add_xpath('words', '//div[@class="bookinfo"]/span/text()')
        loader.add_xpath('ctime', '//div[@class="bookinfo"]/span/text()')

        yield loader.load_item()

    def book_parse_item(self, response: HtmlResponse):
        loader = DescLoader(item=BookItem(), response=response)
        loader.add_xpath('title', '//div[@class="book-name"]/text()')
        loader.add_xpath('desc', '//div[@class="book-dec Jbook-dec hide"]/p/text()')
        loader.add_xpath('author', '//div[@class="au-name"]/a/text()')
        loader.add_xpath('category', '//div[@class="book-label"]/a[@class="label"]/text()')
        loader.add_xpath('tags', '//div[@class="book-label"]/span//text()')

        yield loader.load_item()
