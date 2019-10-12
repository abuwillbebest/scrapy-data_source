# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import pymysql
from .items import NovelItem, BookItem


class NovelPipeline():
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT'),
        )

    def open_spider(self, spider):
        self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8', port=self.port)
        self.cursor = self.db.cursor()

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        if isinstance(item, NovelItem):
            sql = '''insert into fiction.text(content) values("{}")'''.format(item['content'])
            self.cursor.execute(sql)
            content_id = self.cursor.lastrowid

            sql = "SELECT id FROM fiction.novel WHERE title = '{}'".format(item['bookname'])
            self.cursor.execute(sql)

            novel_id = int(self.cursor.fetchone()[0])
            sql = "insert into fiction.chapter(c_title, novel_id, content_id, words, ctime) " \
                  "values('{}', {}, {}, {}, '{}')".format(item['chapters'], novel_id, content_id,
                                                              item['words'], item['ctime'])

            self.cursor.execute(sql)

            self.db.commit()
            # self.db.rollback()
            return item

        if isinstance(item, BookItem):
            sql = '''insert into fiction.novel(`title`, `desc`, `author`, `noveltype`, `tags`) 
            values("{}", "{}", "{}", "{}", "{}")'''.format(item['title'], item['desc'], item['author'],
                                                           item['category'], item['tags'])
            self.cursor.execute(sql)

            self.db.commit()
            return item
