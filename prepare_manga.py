# -*- coding: utf-8 -*-
import getopt
import os
import os.path as op
import shutil
import sys

from opex_manga_scrapy.pipelines import MongoPipelineNew
from opex_manga_scrapy.settings import IMAGES_STORE, MONGO_URI, \
    MONGO_DATABASE, MONGO_USER, MONGO_PW

mongo_setup = {
    'mongo_uri': MONGO_URI,
    'mongo_db': MONGO_DATABASE,
    'mongo_user': MONGO_USER,
    'mongo_pw': MONGO_PW
}


def copy_chapter(chapter):
    if chapter is None:
        raise ValueError('chapter is None')
    curr_dir = op.dirname(__file__)
    dest_dir = op.join(curr_dir, 'mangas', 'chapter-{}'.format(chapter['num']))
    if not op.exists(dest_dir):
        os.makedirs(dest_dir)
    for page in chapter['pages']:
        page_num = page['num']
        tt = os.path.basename(page['images'][0]['path'])
        page_file = os.path.join(IMAGES_STORE, page['images'][0]['path'])
        shutil.copy2(page_file, dest_dir)
        shutil.move(op.join(dest_dir, tt), op.join(dest_dir,
                                                   str(page_num) + '.png'))
    print('Chapter copied to {}'.format(dest_dir))


def main(argv):
    manga = ''
    chapter = ''
    try:
        opts, args = getopt.getopt(argv, "hm:c:", ["manga=", "chapter="])
    except getopt.GetoptError:
        print('prepare_manga.py -m <mangatitle> -c <chapternumber>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('prepare_manga.py -m <mangatitle> -c <chapternumber>')
            sys.exit()
        elif opt in ("-m", "--manga"):
            manga = arg
        elif opt in ("-c", "--chapter"):
            chapter = arg
    print('Manga title is {}'.format(manga))
    print('Chapter number is {}'.format(chapter))

    if argv is None:
        argv = sys.argv

    mdb = MongoPipelineNew(**mongo_setup)
    mdb.open_spider(None)

    manga_obj = mdb.query_manga(manga)
    chapter_obj = mdb.query_manga_chapter(manga, int(chapter))
    copy_chapter(chapter_obj)


if __name__ == "__main__":
    main(sys.argv[1:])
