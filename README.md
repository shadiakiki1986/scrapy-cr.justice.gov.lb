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
scrapy crawl cr_justice_gov_lb_csv -a csv_in=scrapy_cr_justice_gov_lb/fixtures/df_in_sample.csv
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