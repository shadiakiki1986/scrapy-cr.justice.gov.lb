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

from .update_fixtures import CASSETTE_LIBRARY_DIR
with Betamax.configure() as config:
  config.cassette_library_dir = CASSETTE_LIBRARY_DIR

import pandas as pd

class TestSpiderCrJusticeGovLb(BetamaxTestCase):
  def setUp(self):
    df_in = os.path.join(BASE_DIR, 'tests/fixtures/df_in_sample.csv')
    self.spider = ScrapyCrJusticeGovLbSpiderCsv(df_in)
    super().setUp()

  def test_parse(self):
    response = self.session.get(self.spider.url)
    request = list(self.spider.parse(response))
    self.assertEqual(1, len(request))
    request = request[0]
    self.assertEqual('POST', request.method)
    self.assertTrue('FindBox=66942' in str(request._body))


if __name__ == '__main__':
  unittest.main()
