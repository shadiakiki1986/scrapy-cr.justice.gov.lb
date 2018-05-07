# scrapy-cr.justice.gov.lb
scrapy spider that extracts shareholder names from http://cr.justice.gov.lb using the commercial register number

## Installation

```
pew new -r requirements.txt SCRAPY_CRJUST
```

Copy `scrapy.cfg.dist` to `scrapy.cfg` and modify as needed

Scrapy-fu from [tutorial](https://doc.scrapy.org/en/latest/intro/tutorial.html)

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

Run test
```
python -m unittest scrapy_cr_justice_gov_lb.tests.test_spider_cr_justice_gov_lb -v
```

The tests use [betamax](http://betamax.readthedocs.io/).
This only makes a real internet request as long as there is no corresponding file in `test/fixtures/cassettes`.
Each test has one file in `test/fixtures/cassettes`.
To update the recorded responses, `rm test/fixtures/cassettes/*json` and run all tests.
This will recreate the deleted json files, with fresh content

Using [scrapyrt](http://scrapyrt.readthedocs.io/en/latest/api.html#) (experimental)

```
pip install scrapyrt
scrapyrt -i 0.0.0.0 -p 3005
curl -X POST -H "Content-Type: application/json" -d '{"spider_name":"cr_justice_gov_lb_base", "request": {"meta": {"df_in": [{"register_number": "66942", "register_place": "jabal"}]}, "callback": "parse", "url": "http://duckduckgo.com"}}' http://bsec-apps.net:3005/crawl.json
```