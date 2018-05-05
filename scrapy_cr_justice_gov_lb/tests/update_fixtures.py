# Based on http://betamax.readthedocs.io/en/latest/introduction.html#recording-your-first-cassette

import betamax
import requests

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASSETTE_LIBRARY_DIR = os.path.join(BASE_DIR, 'tests/fixtures/cassettes/')

from ..spiders.cr_justice_gov_lb import ScrapyCrJusticeGovLbSpiderBase

def main():
  session = requests.Session()
  recorder = betamax.Betamax(
    session, cassette_library_dir=CASSETTE_LIBRARY_DIR
  )

  record_mode = 'once'; # all new_episodes once
  with recorder.use_cassette('after_search', record=record_mode):
    main_url = ScrapyCrJusticeGovLbSpiderBase.url
    session.get(main_url)
    example_register_number = '66942'
    session.post(
      main_url,
      data={'FindBox': example_register_number}
    )
    example_details = 'http://cr.justice.gov.lb/search/result.aspx?id=2000004239'
    session.get(example_details)


if __name__ == '__main__':
  main()
