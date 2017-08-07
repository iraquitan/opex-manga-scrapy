# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

import datetime
from urllib import parse

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

    collection_name = 'mangas'

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

    def query_manga(self, title):
        coll = self.db[self.collection_name]
        cur = coll.find_one({'title': title})
        return cur

    def query_manga_chapter(self, title, chapter):
        coll = self.db[self.collection_name]
        cur = coll.find_one({'title': title,
                             'chapters': {'$elemMatch': {'num': chapter}}})
        return cur

    def query_manga_chapter_page(self, title, chapter, page):
        coll = self.db[self.collection_name]
        cur = coll.find_one({'title': title,
                             'chapters': {"$elemMatch": {'num': chapter}},
                             'chapters.pages': {'$elemMatch': {'num': page}}})
        return cur

    def add_manga(self, title, domain):
        coll = self.db[self.collection_name]
        manga = {'title': title,
                 'domain': domain,
                 'chapters': [],
                 'date_added': datetime.datetime.utcnow(),
                 'last_modified': datetime.datetime.utcnow()}
        coll.insert_one(manga)

    def add_manga_chapter(self, title, chapter_name, chapter_num, n_pages,
                          req_url):
        coll = self.db[self.collection_name]
        chapter_dict = {
            'name': chapter_name,
            'num': chapter_num,
            'n_pages': n_pages,
            'pages': [],
            'req_url': req_url
        }
        cur = self.query_manga_chapter(title, chapter_num)
        res = None
        if not cur:
            res = coll.find_one_and_update(
                {'title': title},
                {
                    "$push": {"chapters": chapter_dict},
                    "$set": {"last_modified": datetime.datetime.utcnow()}
                })
            print(res)
        return res

    def add_chapter_page(self, title, chapter_num, page, page_url, images):
        coll = self.db[self.collection_name]
        page_dict = {
            'num': page,
            'image_urls': page_url,
            'images': images
        }
        cur = self.query_manga_chapter_page(title, chapter_num, page)
        res = None
        if not cur:
            res = coll.find_one_and_update(
                {'title': title,
                 'chapters': {'$elemMatch': {'num': chapter_num}}},
                {
                    "$push": {"chapters.$.pages": page_dict},
                    "$set": {"last_modified": datetime.datetime.utcnow()}
                })
            print(res)
        return res

    def process_item(self, item, spider):
        coll = self.db[self.collection_name]
        d_item = dict(item)
        title = d_item['title']
        ch_title = d_item['ch_title']
        ch_number = d_item.get('ch_number', None)
        if ch_number:
            ch_number = int(ch_number)
        page = d_item.get('page', None)
        if page:
            page = int(page)
        n_pages = d_item.get('n_pages', None)
        if n_pages:
            n_pages = int(n_pages)
        req_url = d_item['req_url']
        image_urls = d_item['image_urls']
        images = d_item.get('images', None)
        if images is None:
            raise DropItem("Page image not loaded.")

        manga_cur = self.query_manga(title)
        if not manga_cur:
            parsed_uri = parse.urlparse(req_url)
            domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
            self.add_manga(title=title, domain=domain)
            self.add_manga_chapter(title=title, chapter_name=ch_title,
                                   chapter_num=ch_number, n_pages=n_pages,
                                   req_url=req_url)
            self.add_chapter_page(title=title, chapter_num=ch_number,
                                  page=page, page_url=image_urls,
                                  images=images)
        else:
            chapter_cur = self.query_manga_chapter(title=title,
                                                   chapter=ch_number)
            if not chapter_cur:
                self.add_manga_chapter(title=title, chapter_name=ch_title,
                                       chapter_num=ch_number, n_pages=n_pages,
                                       req_url=req_url)
                self.add_chapter_page(title=title, chapter_num=ch_number,
                                      page=page, page_url=image_urls,
                                      images=images)
            else:
                page_cur = self.query_manga_chapter_page(title=title,
                                                         chapter=ch_number,
                                                         page=page)
                if not page_cur:
                    self.add_chapter_page(title=title, chapter_num=ch_number,
                                          page=page, page_url=image_urls,
                                          images=images)
        return item


class MongoPipelineNew(object):

    collection_mangas = 'mangas'
    collection_chapters = 'chapters'

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

    def query_manga(self, title):
        coll = self.db[self.collection_mangas]
        manga = None
        res = coll.find_one({'title': title})
        if res is not None:
            manga = res
        return manga

    def query_manga_chapter(self, title, chapter_num):
        coll_mg = self.db[self.collection_mangas]
        coll_ch = self.db[self.collection_chapters]
        manga = coll_mg.find_one({"title": title,
                                  "chapters": {
                                      '$elemMatch': {"num": chapter_num}
                                  }})
        chapter = None
        if manga is not None:
            chapter_id = [c['id'] for c in manga['chapters']
                          if c['num'] == chapter_num]
            chapter = coll_ch.find_one({'_id': chapter_id[0]})

        return chapter

    def query_manga_chapter_page(self, title, chapter_num, page):
        coll_ch = self.db[self.collection_chapters]
        chapter = self.query_manga_chapter(title, chapter_num)

        chapter_page = None
        if chapter is not None:
            chapter_page = coll_ch.find_one({'_id': chapter['_id'],
                                             'pages': {
                                                 '$elemMatch': {'num': page}
                                             }})
        return chapter_page

    def add_manga(self, title, domain):
        coll = self.db[self.collection_mangas]
        manga = {'title': title,
                 'domain': domain,
                 'chapters': [],
                 'date_added': datetime.datetime.utcnow(),
                 'last_modified': datetime.datetime.utcnow()}
        coll.insert_one(manga)

    def add_manga_chapter(self, title, chapter_name, chapter_num, n_pages,
                          req_url):
        coll_ch = self.db[self.collection_chapters]
        coll_mangas = self.db[self.collection_mangas]

        if self.query_manga_chapter(title, chapter_num):
            # Chapter already exists
            return False

        chapter_dict = {
            'name': chapter_name,
            'num': chapter_num,
            'n_pages': n_pages,
            'pages': [],
            'req_url': req_url,
            'date_added': datetime.datetime.utcnow(),
            'last_modified': datetime.datetime.utcnow()
        }

        # Transaction
        res = False

        res_ch = coll_ch.insert_one(chapter_dict)
        if res_ch.inserted_id:

            res_mg = coll_mangas.find_one_and_update(
                {'title': title},
                {
                    "$push": {"chapters": {"id": res_ch.inserted_id,
                                           "num": chapter_num}},
                    "$set": {"last_modified": datetime.datetime.utcnow()}
                })
            if res_mg is None:  # Remove previously added chapter
                coll_ch.find_one_and_delete({"_id": res_ch.inserted_id})
            else:
                res = True
        return res

    def add_chapter_page(self, title, chapter_num, page, page_url, images):
        coll_ch = self.db[self.collection_chapters]
        page_dict = {
            'num': page,
            'image_urls': page_url,
            'images': images
        }
        chapter = self.query_manga_chapter(title, chapter_num)
        chapter_page = self.query_manga_chapter_page(title, chapter_num, page)
        res = None
        if chapter_page is None:
            res = coll_ch.find_one_and_update(
                {'_id': chapter['_id']},
                {"$push": {"pages": page_dict},
                 "$set": {"last_modified": datetime.datetime.utcnow()}})
        return res

    def process_item(self, item, spider):
        d_item = dict(item)
        title = d_item['title']
        ch_title = d_item['ch_title']
        ch_number = d_item.get('ch_number', None)
        if ch_number:
            ch_number = int(ch_number)
        page = d_item.get('page', None)
        if page:
            page = int(page)
        n_pages = d_item.get('n_pages', None)
        if n_pages:
            n_pages = int(n_pages)
        req_url = d_item['req_url']
        image_urls = d_item['image_urls']
        images = d_item.get('images', None)
        if images is None:
            raise DropItem("Page image not loaded.")

        manga_cur = self.query_manga(title)
        if manga_cur is None:
            parsed_uri = parse.urlparse(req_url)
            domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
            self.add_manga(title=title, domain=domain)
            self.add_manga_chapter(title=title, chapter_name=ch_title,
                                   chapter_num=ch_number, n_pages=n_pages,
                                   req_url=req_url)
            self.add_chapter_page(title=title, chapter_num=ch_number,
                                  page=page, page_url=image_urls,
                                  images=images)
        else:
            chapter_cur = self.query_manga_chapter(title, ch_number)
            if chapter_cur is None:
                self.add_manga_chapter(title=title, chapter_name=ch_title,
                                       chapter_num=ch_number, n_pages=n_pages,
                                       req_url=req_url)
                self.add_chapter_page(title=title, chapter_num=ch_number,
                                      page=page, page_url=image_urls,
                                      images=images)
            else:
                page_cur = self.query_manga_chapter_page(title, ch_number,
                                                         page)
                if page_cur is None:
                    self.add_chapter_page(title=title, chapter_num=ch_number,
                                          page=page, page_url=image_urls,
                                          images=images)
        return item


class MangaDB(object):
    collection = 'mangas'

    def __init__(self, mongo_uri, mongo_db, mongo_user, mongo_pw):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_user = mongo_user
        self.mongo_pw = mongo_pw

    def __enter__(self):
        self.client = pymongo.MongoClient(self.mongo_uri
                                          .replace('user', self.mongo_user)
                                          .replace('password', self.mongo_pw))
        self.db = self.client[self.mongo_db]

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def query_manga(self, title):
        coll = self.db[self.collection]
        cur = coll.find_one({'title': title})
        return cur

    def query_manga_chapter(self, title, chapter):
        coll = self.db[self.collection]
        cur = coll.find_one({'title': title, 'chapters': {'number': chapter}})
        return cur

    def query_manga_chapter_page(self, title, chapter, page):
        coll = self.db[self.collection]
        cur = coll.find_one({'title': title, 'chapters': {'number': chapter},
                             'chapters.pages': {'number': page}})
        return cur

    def add_manga(self, title, domain):
        coll = self.db[self.collection]
        manga = {'title': title,
                 'domain': domain,
                 'chapters': [],
                 'date_added': datetime.datetime.utcnow(),
                 'last_modified': datetime.datetime.utcnow()}
        coll.insert_one(manga)

    def add_manga_chapter(self, title, chapter_name, chapter_num, n_pages,
                          req_url):
        coll = self.db[self.collection]
        chapter_dict = {
            'name': chapter_name,
            'num': chapter_num,
            'n_pages': n_pages,
            'pages': [],
            'req_url': req_url
        }
        cur = self.query_manga_chapter(title, chapter_num)
        res = None
        if not cur:
            res = coll.find_one_and_update(
                {'title': title, 'chapters': {'number': chapter_num}},
                {
                    "$push": {"chapters": chapter_dict},
                    "$set": {"last_modified": datetime.datetime.utcnow()}
                })
        return res

    def add_chapter_page(self, title, chapter_num, page, page_url, images):
        coll = self.db[self.collection]
        page_dict = {
            'num': page,
            'image_urls': page_url,
            'images': images
        }
        cur = self.query_manga_chapter_page(title, chapter_num, page)
        res = None
        if not cur:
            res = coll.find_one_and_update(
                {'title': title, 'chapters': {'number': chapter_num}},
                {
                    "$push": {"chapters.pages": page_dict},
                    "$set": {"last_modified": datetime.datetime.utcnow()}
                })
        return res
