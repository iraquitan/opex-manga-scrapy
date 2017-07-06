# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class OpexMangaScrapyItem(scrapy.Item):
    title = scrapy.Field()
    n_pages = scrapy.Field()
    page = scrapy.Field()
    chapter = scrapy.Field()
    req_url = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()


class MangaPageItem(scrapy.Item):
    title = scrapy.Field()
    ch_title = scrapy.Field()
    ch_number = scrapy.Field()
    n_pages = scrapy.Field()
    page = scrapy.Field()
    req_url = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
