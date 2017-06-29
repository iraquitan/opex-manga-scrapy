# -*- coding: utf-8 -*-
import os

import requests
import scrapy
import scrapy_splash

from opex_manga_scrapy.items import OpexMangaScrapyItem


class OpexSpider(scrapy.Spider):
    name = 'opex'
    # allowed_domains = ['https://one-piece-x.com.br/mangas/leitor/870/']
    start_urls = ['https://one-piece-x.com.br/mangas/leitor/870/']
    base_img_url = 'https://one-piece-x.com.br'
    save_path = 'mangas'

    def parse(self, response):
        for href in response.xpath("//a[re:test(@id, '\d$')]"):
            req_url = self.start_urls[0] + href.xpath('@href').extract()[0]
            # splash_url = "http://localhost:8050/render.json"

            request = scrapy_splash.SplashRequest(
                req_url, self.parse_images,
                # splash_url=splash_url,
                args={'wait': 2},
                slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,
                                    )
            request.meta['name'] = req_url
            yield request

    def parse_images(self, response):
        name = response.meta['name']
        img = response.xpath('//*[@id="conteudo"]/p[2]/a/img').xpath("@src")
        # img = response.xpath('//img[re:test(@class, "paginamanga")]').xpath("@src")  # noqa
        imageURL = img.extract_first()

        spath = os.path.join(self.save_path, 'chapter-870')
        if not os.path.exists(spath):
            os.makedirs(spath)

        full_url = os.path.join(self.base_img_url, imageURL[1:])
        fpath = os.path.join(spath, os.path.basename(full_url))
        r = requests.get(full_url, stream=True)
        if r.status_code == 200:
            with open(fpath, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)

        yield OpexMangaScrapyItem(name=name, file_urls=[full_url])
