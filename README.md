# scrapy-cr.justice.gov.lb

[![Build Status](https://travis-ci.org/shadiakiki1986/scrapy-cr.justice.gov.lb.svg?branch=master)](https://travis-ci.org/shadiakiki1986/scrapy-cr.justice.gov.lb)

scrapy spider that extracts shareholder names from http://cr.justice.gov.lb using the commercial register number


## Installation

1. To run the srapy spider locally:

```
pew new -r requirements.txt SCRAPY_CRJUST
```

Copy `scrapy.cfg.dist` to `scrapy.cfg` and modify as needed

Then use scrapy-fu from [tutorial](https://doc.scrapy.org/en/latest/intro/tutorial.html)

2. To install this as a dependency in another project

```
pip install git+https://github.com/shadiakiki1986/scrapy-cr.justice.gov.lb.git
```

or append the URL to your `requirements.txt` or `setup.py` file.


## Usage

Fetching shareholders of register numbers/places in a csv file
```
scrapy crawl cr_justice_gov_lb_csv -a csv_in=scrapy_cr_justice_gov_lb/tests/fixtures/df_in_sample.csv
```

To benefit from translation with Google Cloud Platform, set the corresponding environment variable

```
GOOGLE_APPLICATION_CREDENTIALS=abc123 scrapy crawl ...
```
or
```
export GOOGLE_APPLICATION_CREDENTIALS=abc123
scrapy crawl ...
```

Note that this is a paid service by Google Cloud Platform


For testing xpath against html, useful website: http://www.xpathtester.com/xpath


Run test
```
python -m unittest scrapy_cr_justice_gov_lb.tests.test_spider_cr_justice_gov_lb -v
```

The tests use [betamax](http://betamax.readthedocs.io/).
This only makes a real internet request as long as there is no corresponding file in `test/fixtures/cassettes`.
Each test has one file in `test/fixtures/cassettes`.
To update the recorded responses, `rm test/fixtures/cassettes/*json` and run all tests.
This will recreate the deleted json files, with fresh content

Using [scrapyrt](http://scrapyrt.readthedocs.io/en/latest/api.html#)

```
pip install scrapyrt
scrapyrt -i 0.0.0.0 -p 3000

curl http://localhost:3000/crawl.json \
  -d '{"request":{"url": "http://example.com", "meta": {"df_in": [{"register_number": "66942", "register_place": "Mount Lebanon"}]}}, "spider_name": "cr_justice_gov_lb_single"}'
```

Sample result available in `scrapyrt-sample.json` (also available at [this link](https://s3-us-west-2.amazonaws.com/keras-models-factory/scrapy-crjusticegovlb-scrapyrt-sample.json))


## Note on transliteration

The original result is in arabic characters.
Transliterating with [buckwalter](https://github.com/shadiakiki1986/ocr-arabic/blob/master/transliterate.py) was poor.
Testing translating with [translate.google.com](https://translate.google.com) was much better,
e.g. labib instead of lbyb
so I resort to the [Google Cloud Translation API](https://cloud.google.com/translate/docs/translating-text#translate-translate-text-python)


## Changelog

Version 0.0.5
* added spider "Single" for usage with [scrapyrt](http://scrapyrt.readthedocs.io/)


Version 0.0.4 (2018-05-01)
* first working version
