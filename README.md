# scrapy-cr.justice.gov.lb
scrapy spider that extracts shareholder names from http://cr.justice.gov.lb using the commercial register number

## Installation

```
pew new -r requirements.txt SCRAPY_CRJUST
```

Copy `scrapy.cfg.dist` to `scrapy.cfg` and modify as needed

Scrapy-fu from [tutorial](https://doc.scrapy.org/en/latest/intro/tutorial.html)

## Usage

```
scrapy crawl cr_justice_gov_lb_csv -a csv_in=df_in_sample.csv
```
