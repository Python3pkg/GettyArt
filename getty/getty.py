# pylint:disable=C0111
from __future__ import absolute_import

import itertools
import os
import re
import urllib

from getty import util


CATEGORIES = [
    'Architectural drawings',
    'Architecture',
    'Book',
    'Coins',
    'Decorative Arts',
    'Drawings',
    'Figures (illustrations)',
    'Illuminations',
    'Implements',
    'Jewelry',
    'Manuscripts',
    'Mixed Material',
    'Paintings',
    'Photographs',
    'Plates (illustrations)',
    'Playing cards',
    'Prints',
    'Sculpture',
    'Vessels',
    'Visual Material',
    'Watercolors (paintings)',
]


class Scraper(object):
    def __init__(self, category, batchsize=100, page=1):
        self._category = category
        self._batchsize = batchsize
        self._page = page

    @classmethod
    def format_filename(cls, url, basedir=None):
        basename = os.path.basename(url)
        return (util.tmpfile(basename) if basedir is None
                else os.path.join(basedir, basename))

    @classmethod
    def extract_images(cls, resultspage):
        image_re = re.compile(r'"(?P<url>http://www.getty.edu/art/collections'
                              r'/images/enlarge/[^"]+)"')
        return set(match.group('url') for line in resultspage
                   for match in image_re.finditer(line))

    def resultspage(self, page):
        url_template = (r'http://search.getty.edu/gateway/search'
                        r'?q&cat=type&dir=s&img=1'
                        r'&types="{category}"&rows={batchsize}&pg={page}')
        url = url_template.format(
            category=self._category,
            batchsize=self._batchsize,
            page=page)
        return urllib.urlopen(url)

    def scrape(self, num=None, basedir=None):
        filenames = []
        for image_url in itertools.islice(self, num):
            filename = self.format_filename(image_url, basedir)
            urllib.urlretrieve(image_url, filename)
            filenames.append(filename)
        return filenames

    def __iter__(self):
        while True:
            resultspage = self.resultspage(self._page)
            image_urls = self.extract_images(resultspage)
            if image_urls:
                for image_url in image_urls:
                    yield image_url
                self._page += 1
            else:
                break


def _main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('category', metavar='category', choices=CATEGORIES,
                        help=('type of images to scrape; '
                              'allowed values are: ' + ', '.join(CATEGORIES)))
    parser.add_argument('-l', '--limit', metavar='L', default=None, type=int,
                        help='maximum number of images to scrape')
    parser.add_argument('-o', '--output', metavar='O', default=None,
                        help='directory in which to store images')
    parser.add_argument('-p', '--page', metavar='P', default=1,
                        help='results page at which to start scraping')
    parser.add_argument('--batchsize', metavar='B', default=100,
                        help='number of results to fetch per query')
    args = parser.parse_args()

    Scraper(
        category=args.category,
        batchsize=args.batchsize,
        page=args.page,
    ).scrape(
        num=args.limit,
        basedir=args.output,
    )


if __name__ == '__main__':
    _main()
