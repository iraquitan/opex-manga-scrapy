# -*- coding: utf-8 -*-
import os

import requests
import scrapy
import scrapy_splash

from opex_manga_scrapy.items import OpexMangaScrapyItem, MangaPageItem


class OpexSpider(scrapy.Spider):
    name = 'opex'

    def __init__(self, title='one-piece', chapter="870", *args, **kwargs):
        super(OpexSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'https://one-piece-x.com.br/mangas/leitor/{}/'.format(chapter)]
        self.chapter = chapter
        self.title = title

    # allowed_domains = ['https://one-piece-x.com.br/mangas/leitor/870/']
    base_img_url = 'https://one-piece-x.com.br'
    save_path = 'mangas'

    def parse(self, response):
        pages = response.xpath("//a[re:test(@id, '\d$')]")
        for page_aid in pages:
            page_id = page_aid.xpath("text()").extract_first()
            req_url = self.start_urls[0] + page_aid.xpath('@href').extract()[0]
            request = scrapy_splash.SplashRequest(
                req_url, self.parse_images,
                args={'wait': 5},
                slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,
            )
            request.meta['page'] = int(page_id)
            request.meta['n_pages'] = len(pages)
            yield request

    def parse_images(self, response):
        page = response.meta['page']
        n_pages = response.meta['n_pages']
        ch_title = response.xpath(
            '//*[@id="tituloleitor"]/text()').extract_first()
        img = response.xpath('//*[@id="conteudo"]/p[2]/a/img').xpath("@src")
        imageURL = img.extract_first()
        if imageURL:
            full_url = os.path.join(self.base_img_url, imageURL[1:])
        else:
            full_url = self.base_img_url

        chapter_page = MangaPageItem(title=self.title, ch_title=ch_title,
                                     ch_number=self.chapter, n_pages=n_pages,
                                     page=page, req_url=self.start_urls[0],
                                     image_urls=[full_url])

        yield chapter_page
        # yield OpexMangaScrapyItem(page=page, chapter=self.chapter,
        #                           n_pages=n_pages, title=title,
        #                           req_url=self.start_urls[0],
        #                           image_urls=[full_url])
