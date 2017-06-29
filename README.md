# opex-manga-scrapy

## Requirements
* Scrapy
* Splash
* scrapy_splash

## Quick start
The easiest way to set up Splash is through Docker:
```bash
$ docker pull scrapinghub/splash
$ docker run -p 5023:5023 -p 8050:8050 -p 8051:8051 scrapinghub/splash
```

To run just do:
```bash
$ scrapy runspider opex_manga_scrapy/spiders/opex.py -o output.json
```
