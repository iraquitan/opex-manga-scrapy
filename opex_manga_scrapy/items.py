# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class OpexMangaScrapyItem(scrapy.Item):
    name = scrapy.Field()
    chapter = scrapy.Field()
    title = scrapy.Field()
    req_url = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
