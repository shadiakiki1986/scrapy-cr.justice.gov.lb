# Based on
# https://stackoverflow.com/a/38214137/4126114
# http://betamax.readthedocs.io/en/latest/integrations.html#unittest-integration
# https://docs.python.org/3/library/unittest.html

from betamax.fixtures.unittest import BetamaxTestCase
from betamax import Betamax
import unittest
# from unittest import TestCase
from ..spiders.cr_justice_gov_lb import ScrapyCrJusticeGovLbSpiderCsv

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CASSETTE_LIBRARY_DIR = os.path.join(BASE_DIR, 'tests/fixtures/cassettes/')
with Betamax.configure() as config:
  config.cassette_library_dir = CASSETTE_LIBRARY_DIR

import pandas as pd

class TestSpiderCrJusticeGovLb(BetamaxTestCase):
  def setUp(self):
    df_in = os.path.join(BASE_DIR, 'tests/fixtures/df_in_sample.csv')
    self.spider = ScrapyCrJusticeGovLbSpiderCsv(df_in)
    super().setUp()

  def test_1_parse(self):
    response = self.session.get(self.spider.url)
    response = list(self.spider.parse(response))
    self.assertEqual(1, len(response))
    response = response[0]
    self.assertEqual('POST', response.method)
    self.assertTrue('FindBox=66942' in str(response.body))

  def test_2_after_search(self):
    response = self.session.get(self.spider.url)
    request = list(self.spider.parse(response))
    request = request[0]
    # print(request.__dict__)

    # method 1: plain requests post
    response = self.session.post(request.url, data=str(request.body))

    # method 2
    # copied from scrapy.shell#L114
    # Blocks and never returns .. FIXME
#    from scrapy.utils.test import get_crawler
#    from scrapy.shell import Shell
#    crawler = get_crawler()
#    shell = Shell(crawler)
#    response = shell.fetch(request, spider=self.spider, redirect=False)

    response = list(self.spider.after_search(response))
    self.assertEqual(1, len(response))
    response = response[0]
    self.assertEqual('GET', response.method)
    self.assertTrue('FindBox=66942' in str(response._body))


if __name__ == '__main__':
  unittest.main()
