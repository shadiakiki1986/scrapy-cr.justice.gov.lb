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

# show output
# https://stackoverflow.com/a/7483862/4126114
# import logging
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)
# import sys
# stream_handler = logging.StreamHandler(sys.stdout)
# logger.addHandler(stream_handler)

from scrapy.http import HtmlResponse


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
    # print(request.meta)
    # print(request.__dict__)
    # print(request.url)
    # print(request)

    # make a plain python.requests post and wrap it in scrapy response
    data = str(request.body).split('&')[-1].split('=')[-1].replace("'","")
    response_1 = self.session.post(request.url, data={'FindBox': data})
    # print(response_1.content.decode('utf-8'))
    
    response_1b = HtmlResponse(
        url=response_1.url,
        status=response_1.status_code,
        headers=response_1.headers,
        body=response_1.content,
        request = request
    )
    
    # pass scrapy response to spider function to test    
    response_2 = list(self.spider.after_search(response_1b)) # hxs
    self.assertEqual(1, len(response_2))
    response_2 = response_2[0]
    self.assertEqual('GET', response_2.method)
    # print(response_2.__dict__)
    self.assertTrue('id=2000004239' in str(response_2.url))

    # repeat request, but this time test that register_place filtering that is insufficient still raises an error
    request.meta['register_place'] = 'ج'
    response_1b = HtmlResponse(
        url=response_1.url,
        status=response_1.status_code,
        headers=response_1.headers,
        body=response_1.content,
        request = request
    )
    with self.assertRaises(ValueError):
        response_2 = list(self.spider.after_search(response_1b)) # hxs
