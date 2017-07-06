# -*- coding: utf-8 -*-
import re
import scrapy
import scrapy_splash

from opex_manga_scrapy.items import MangaItem


class BokunoheroSpider(scrapy.Spider):
    name = 'bokunohero'

    def __init__(self, title='boku-no-hero-academia', chapter="44", *args, **kwargs):
        super(BokunoheroSpider, self).__init__(*args, **kwargs)
        self.title = title
        self.chapter = int(chapter)
        self.start_urls = ['http://readmha.com/chapter/boku-no-hero-'
                           'academia-chapter-{:03d}'.format(int(chapter))]

    # allowed_domains = ['http://readmha.com/chapter/boku-no-hero-academia-chapter-045/']

    def parse(self, response):
        request = scrapy_splash.SplashRequest(
            self.start_urls[0], self.parse_chapter,
            args={'wait': 5},
            slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,
        )
        yield request

    def parse_chapter(self, response):
        pages = response.xpath("//img[re:test(@class, 'pages__img')]")
        image_urls = []
        for i, page in enumerate(pages):
            img_alt = "Page {}".format(i+1)
            img_src = page.xpath("@src | @lazysrc").extract_first()
            print("alt = {}".format(img_alt))
            print("src = {}".format(img_src))
            page_num = i + 1
            image_urls.append(img_src)
        chapter = MangaItem(title=self.title,
                            ch_title="Chapter {}".format(self.chapter),
                            ch_number=self.chapter, n_pages=len(pages),
                            page=page_num, req_url=self.start_urls[0],
                            image_urls=image_urls)
        yield chapter
