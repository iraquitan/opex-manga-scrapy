# -*- coding: utf-8 -*-
import os

import requests
import scrapy
import scrapy_splash

from opex_manga_scrapy.items import OpexMangaScrapyItem


class OpexSpider(scrapy.Spider):
    name = 'opex'

    def __init__(self, chapter="870", *args, **kwargs):
        super(OpexSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'https://one-piece-x.com.br/mangas/leitor/{}/'.format(chapter)]
        self.chapter = chapter

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
                args={'wait': 2},
                slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,
            )
            request.meta['page'] = int(page_id)
            request.meta['n_pages'] = len(pages)
            yield request

    def parse_images(self, response):
        page = response.meta['page']
        n_pages = response.meta['n_pages']
        title = response.xpath(
            '//*[@id="tituloleitor"]/text()').extract_first()
        img = response.xpath('//*[@id="conteudo"]/p[2]/a/img').xpath("@src")
        imageURL = img.extract_first()
        if imageURL:
            full_url = os.path.join(self.base_img_url, imageURL[1:])
        else:
            full_url = self.base_img_url

        yield OpexMangaScrapyItem(page=page, chapter=self.chapter,
                                  n_pages=n_pages, title=title,
                                  req_url=self.start_urls[0],
                                  image_urls=[full_url])

        # spath = os.path.join(self.save_path, 'chapter-870')
        # if not os.path.exists(spath):
        #     os.makedirs(spath)
        #
        # full_url = os.path.join(self.base_img_url, imageURL[1:])
        # fpath = os.path.join(spath, os.path.basename(full_url))
        # r = requests.get(full_url, stream=True)
        # if r.status_code == 200:
        #     with open(fpath, 'wb') as f:
        #         for chunk in r.iter_content(1024):
        #             f.write(chunk)

        # yield OpexMangaScrapyItem(name=name, image_urls=[full_url])
