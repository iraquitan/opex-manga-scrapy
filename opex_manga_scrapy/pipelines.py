# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

import datetime
import pymongo
from scrapy.exceptions import DropItem


class OpexMangaScrapyPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWriterPipeline(object):
    def open_spider(self, spider):
        self.file = open('items.json', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


class MongoPipeline(object):

    collection_name = 'opex_chapters'

    def __init__(self, mongo_uri, mongo_db, mongo_user, mongo_pw):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_user = mongo_user
        self.mongo_pw = mongo_pw

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items'),
            mongo_user=crawler.settings.get('MONGO_USER'),
            mongo_pw=crawler.settings.get('MONGO_PW')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri
                                          .replace('user', self.mongo_user)
                                          .replace('password', self.mongo_pw))
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        coll = self.db[self.collection_name]
        d_item = dict(item)
        chapter = d_item.get('chapter', None)
        if chapter:
            chapter = int(chapter)
        page = d_item.get('page', None)
        if page:
            page = int(page)
        n_pages = d_item.get('n_pages', None)
        if n_pages:
            n_pages = int(n_pages)
        if d_item['images'] is None:
            raise DropItem("Page image not loaded.")

        chapter = {

        }

        chapter_page = {
            'number': page,
            'image_url': d_item['image_urls'][0],
            'image': d_item['images'][0],
        }
        cursor = coll.find({'chapter': chapter})
        if cursor.count() != 0:  # Update
            pg_cur = coll.find({'pages': {'number': chapter_page['number']}})
            if pg_cur.count() > 0:
                raise DropItem("Page already added.")
            coll.update_one(
                {"chapter": chapter},
                {
                    "$push": {
                        "pages": chapter_page,
                    },
                    "$set": {
                        "last_modified": datetime.datetime.utcnow()
                    }
                }
            )
        else:  # Insert
            title = self.title,
            ch_title = "Chapter {}".format(self.chapter),
            ch_number = self.chapter, n_pages = len(pages),
            page = page_num, req_url = self.start_urls[0],
            image_urls = image_urls
            chapter_item = {
                'title': d_item['title'],
                'chapters': [chapter],
                'req_url': d_item['req_url'],
                'n_pages': n_pages,
                'pages': [chapter_page],
                'date_added': datetime.datetime.utcnow(),
                'last_modified': datetime.datetime.utcnow(),

            }
            chapter_item = {
                'title': d_item['title'],
                'chapter': chapter,
                'req_url': d_item['req_url'],
                'n_pages': n_pages,
                'pages': [chapter_page],
                'date_added': datetime.datetime.utcnow(),
                'last_modified': datetime.datetime.utcnow(),

            }
            coll.insert_one(chapter_item)
        return item
