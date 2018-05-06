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

  def get_request_0(self):
    response = self.session.get(self.spider.url)
    request = list(self.spider.parse(response))
    return request
    
  def test_1_parse(self):
    request_0 = self.get_request_0()
    self.assertEqual(1, len(request_0))
    request_0 = request_0[0]
    self.assertEqual('POST', request_0.method)
    self.assertTrue('FindBox=66942' in str(request_0.body))

  def get_response_1(self):
    request_0 = self.get_request_0()[0]

    # make a plain python.requests post and wrap it in scrapy response
    data = str(request_0.body).split('&')[-1].split('=')[-1].replace("'","")
    response_1 = self.session.post(request_0.url, data={'FindBox': data})
    # print(response_1.content.decode('utf-8'))
    return response_1, request_0

  def get_request_2(self):
    response_1, request_0 = self.get_response_1()
    response_1b = HtmlResponse(
        url=response_1.url,
        status=response_1.status_code,
        headers=response_1.headers,
        body=response_1.content,
        request = request_0
    )
    
    # pass scrapy response to spider function to test    
    request_2 = list(self.spider.after_search(response_1b))
    return request_2, response_1, request_0

  def test_2_after_search(self):
    request_2, response_1, request_0 = self.get_request_2()
    
    self.assertEqual(1, len(request_2))
    request_2 = request_2[0]
    self.assertEqual('GET', request_2.method)
    # print(response_2.__dict__)
    self.assertTrue('id=2000004239' in str(request_2.url))

    # repeat request, but this time test that register_place filtering that is insufficient still raises an error
    request_0.meta['register_place'] = 'ج'
    response_1b = HtmlResponse(
        url=response_1.url,
        status=response_1.status_code,
        headers=response_1.headers,
        body=response_1.content,
        request = request_0
    )
    with self.assertRaises(ValueError):
        request_2 = list(self.spider.after_search(response_1b)) # hxs
