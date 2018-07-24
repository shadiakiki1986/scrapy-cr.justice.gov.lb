# scrapy-cr.justice.gov.lb

[![Build Status](https://travis-ci.org/shadiakiki1986/scrapy-cr.justice.gov.lb.svg?branch=master)](https://travis-ci.org/shadiakiki1986/scrapy-cr.justice.gov.lb)

scrapy spider that extracts shareholder names from http://cr.justice.gov.lb using the commercial register number

Check [cr.justice.gov.lb-proxy](https://github.com/shadiakiki1986/cr.justice.gov.lb-proxy) for a flask app wrapping this spider via [scrapyrt](http://scrapyrt.readthedocs.io/)


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

To update the `scrapyrt-sample.json` file,

1. run the [cr.justice.gov.lb-proxy](https://github.com/shadiakiki1986/cr.justice.gov.lb-proxy) docker stack
2. then click on the example link provided
3. choose `json`, click `submit`
4. and save the result to the sample file.


## Note on transliteration

The original result is in arabic characters.
Transliterating with [buckwalter](https://github.com/shadiakiki1986/ocr-arabic/blob/master/transliterate.py) was poor.
Testing translating with [translate.google.com](https://translate.google.com) was much better,
e.g. labib instead of lbyb
so I resort to the [Google Cloud Translation API](https://cloud.google.com/translate/docs/translating-text#translate-translate-text-python)


## Dev notes

To make a new release:
- add notes to Changelog in README.md
- bump version in setup.py
- git commit and push
- git tag "new version"
- git push origin "new version"


## Changelog

Version 0.1.5 (2018-07-??)
* add `business_name_ar` to the raw html entries


Version 0.1.4 (2018-07-06)
* add `business_name_en` and `business_name_ar` of the company to the `df_in`


Version 0.1.3 (2018-06-27)
* add constructor agrument "check_json_serializable" to spider constructor


Version 0.1.2 (2018-06-26)
* rename some fields as per Nada
* add "raw html pipeline" which saves a zip archive of html files per company
  * also "yield" the raw html for easy integration with scrapyrt


Version 0.1.1 (2018-05-28)
* bug fix for spider=None passed
* add `pipeline.merge_in_out` for convenience
* wrap yielded items from spider into `{'type': '...', 'entry': '...'}` to collect `df_in` and `df_out` in the pipeline
* add `n_shares` to `df_out`
* save `business_description` in `spider.df_in`


Version 0.1.0 (2018-05-28)
* added in-line comments in code and FIXME tags and betamax fixture cassettes that were not committed
* distinguish between `df_in` and `df_out` in spider and pipeline
* add `status` field to `df_in`


Version 0.0.5 (2018-05-22)
* added spider "Single" for usage with [scrapyrt](http://scrapyrt.readthedocs.io/)


Version 0.0.4 (2018-05-01)
* first working version
