# Based on
# https://stackoverflow.com/a/38214137/4126114
# http://betamax.readthedocs.io/en/latest/integrations.html#unittest-integration
# https://docs.python.org/3/library/unittest.html

from betamax.fixtures.unittest import BetamaxTestCase
from betamax import Betamax
import unittest
# from unittest import TestCase
from ..spiders.cr_justice_gov_lb import *

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

def convert_response_from_requests_scrapy(response_1, request_1):
    return HtmlResponse(
        url=response_1.url,
        status=response_1.status_code,
        headers=response_1.headers,
        body=response_1.content,
        request = request_1
    )

class TestSpiderCrJusticeGovLbCsv(BetamaxTestCase):
  def setUp(self):
    df_in = os.path.join(BASE_DIR, 'tests/fixtures/df_in_sample.csv')
    self.spider = ScrapyCrJusticeGovLbSpiderCsv(df_in)
    self.df_in_original = self.spider.df_in.copy()
    super().setUp()

  def get_request_1(self):
    response = self.session.get(self.spider.url)
    request = list(self.spider.parse(response))
    return request

  def filter_df_in(self, comment):
    self.spider.df_in = self.df_in_original[self.df_in_original['comment']==comment].copy()
    self.assertEqual(1, self.spider.df_in.shape[0])
    
  def test_1_parse(self):
    self.filter_df_in('single page/multiple results')
    request_1 = self.get_request_1()
    self.assertEqual(1, len(request_1))
    request_1 = request_1[0]
    self.assertEqual('POST', request_1.method)
    self.assertTrue('FindBox=66942' in str(request_1.body))

  def get_response_1(self):
    request_1 = self.get_request_1()[0]

    # make a plain python.requests post and wrap it in scrapy response
    data = str(request_1.body).split('&')[-1].split('=')[-1].replace("'","")
    response_1 = self.session.post(request_1.url, data={'FindBox': data})
    # print(response_1.content.decode('utf-8'))
    return response_1, request_1

  def get_request_2(self):
    response_1, request_1 = self.get_response_1()
    response_1b = convert_response_from_requests_scrapy(response_1, request_1)
    
    # pass scrapy response to spider function to test    
    request_2 = self.spider.after_search(response_1b)
    return request_2, response_1, request_1

  def test_2a_after_search_pass(self):
    self.filter_df_in('single page/multiple results')
    request_2, response_1, request_1 = self.get_request_2()
    
    self.assertEqual('GET', request_2.method)
    # print(response_2.__dict__)
    self.assertTrue('id=2000004239' in str(request_2.url))

  def test_2b_after_search_fail(self):
    self.filter_df_in('single page/multiple results')
    request_2, response_1, request_1 = self.get_request_2()

    # repeat request, but this time test that register_place filtering that is insufficient still raises an error
    request_1.meta['register_place'] = 'ج'
    response_1b = convert_response_from_requests_scrapy(response_1, request_1)
    request_2 = self.spider.after_search(response_1b)
    self.assertEqual('df_in', request_2['type'])
    self.assertTrue('further' in request_2['entry']['status'])

  def test_2c_after_search_singlepage_singleresult(self):
    self.filter_df_in('single page/single result')
    request_2, response_1, request_1 = self.get_request_2()
    
    self.assertEqual('GET', request_2.method)
    #print(request_2.url)
    self.assertTrue('id=5000022640' in str(request_2.url))

  def test_2d_after_search_multipage_singleresult(self):
    self.filter_df_in('multiple pages/multiple aliens')
    request_2, response_1, request_1 = self.get_request_2()
    
    self.assertEqual('POST', request_2.method)
    self.assertTrue('FindBox=5792' in str(request_2.body))
    # print(request_2.__dict__)

  def test_3_after_result(self):
    self.filter_df_in('single page/multiple results')
    request_2, response_1, request_1 = self.get_request_2()
    response_2 = self.session.get(request_2.url)
    response_2b = convert_response_from_requests_scrapy(response_2, request_2)
    
    actual_out = list(self.spider.after_result(response_2b))
    actual_out = [x['entry'] for x in actual_out if x['type']=='df_out']
    self.assertEqual(20, len(actual_out))
    actual_out = pd.DataFrame(actual_out)

    df_out = os.path.join(BASE_DIR, 'tests/fixtures/df_out_singlepage_multiresult.pkl')
    # uncomment the below to update the fixture
    # actual_out.to_pickle(df_out)
   
    expected_out = pd.read_pickle(df_out)
    #print('columns expected_out vs actual_out', expected_out.columns, actual_out.columns)
    #print('expected_out', expected_out)
    #print('actual_out', actual_out)
    pd.testing.assert_frame_equal(actual_out, expected_out)

    # same for df_in
    actual_in = self.spider.df_in
    self.assertNotEqual('', actual_in.loc[0,'business_description'])

    df_in = os.path.join(BASE_DIR, 'tests/fixtures/df_in_singlepage_multiresult.pkl')
    # actual_in.to_pickle(df_in)
    expected_in = pd.read_pickle(df_in)
    pd.testing.assert_frame_equal(actual_in, expected_in)


class TestSpiderCrJusticeGovLbSingle(BetamaxTestCase):
  def test_init(self):
    spider = ScrapyCrJusticeGovLbSpiderSingle()

    # copy from get_request_1 above
    response = self.session.get(spider.url)

    # FIXME
    #response.meta['df_in'] = [
    #  {'register_number': 66942, 'register_place': 'Mount+Lebanon'},
    #]
    #request = list(spider.parse(response))

    self.assertTrue(True)
