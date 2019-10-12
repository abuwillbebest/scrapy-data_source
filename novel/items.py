# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html


from scrapy import Item, Field


class NovelItem(Item):
    bookname = Field()
    author = Field()
    category = Field()
    chapters = Field()
    sequence = Field()
    content = Field()
    words = Field()
    ctime = Field()


class BookItem(Item):
    title = Field()
    desc = Field()
    author = Field()
    category = Field()
    tags = Field()