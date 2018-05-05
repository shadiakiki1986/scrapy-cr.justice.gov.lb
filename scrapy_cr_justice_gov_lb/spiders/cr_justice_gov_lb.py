import scrapy
import pandas as pd

class ScrapyCrJusticeGovLbSpiderBase(scrapy.Spider):
  """
  curl --data "FindBox=5000780" http://cr.justice.gov.lb/search/res_list.aspx
  """

  name = "cr_justice_gov_lb_base"
  #start_urls = []
  url = 'http://cr.justice.gov.lb/search/res_list.aspx'

  def __init__(self, df_in:pd.DataFrame, *args, **kwargs):
    missing_cols = set(['register_number', 'register_place']) - set(df_in.columns)
    if len(missing_cols)>0:
      raise ValueError("Missing columns: %s"%", ".join(missing_cols))
    self.df_in = df_in
    return super().__init__(*args, **kwargs)

  def parse(self, response):
    for index, row in self.df_in.iterrows():
      self.logger.info("searching for %s - %s"%(row['register_number'], row['register_place']))
      request = scrapy.FormRequest.from_response(
        response,
        formdata={'FindBox': str(row['register_number'])},
        callback=self.after_search
      )
      self.logger.info('parse .. request =')
      request.meta['register_number'] = row['register_number']
      request.meta['register_place'] = row['register_place']
      self.logger.info('yield parse')
      yield request


  def after_search(self, response):
    self.logger.info('start after search')
    #with open('after_search.html', 'w') as fn:
    #  fn.write(response.body.decode("utf-8"))

    n_res = response.xpath('//span[@id="DataList1_rec_countLabel_0"]/text()').extract_first()
    n_res = int(n_res)
    self.logger.info("for {number: %s, place: %s} got %s results"%(response.meta['register_number'], response.meta['register_place'], n_res))
    if n_res == 0:
      raise ValueError("Not found. Aborting")

    if n_res >  1:
      details_url = response.xpath('//div[@id="ListView1_itemPlaceholderContainer"]/div[@class="res_line2" and contains(string(), "%s")]/preceding-sibling::div[@class="res_line1"]/a/@href'%(response.meta['register_place']))
      if len(details_url) > 1:
        raise ValueError("Need to filter further. Aborting")
      if len(details_url) == 0:
        raise ValueError("Filter failed. Aborting")
      self.logger.info("filtered down to 1")
      details_url = details_url.extract_first()

    if n_res == 1:
      details_url = response.xpath('//div[@id="ListView1_itemPlaceholderContainer"]/div[@class="res_line1"]/a/@href').extract_first()

    details_url =  'http://cr.justice.gov.lb/search/' + details_url
    self.logger.info("details at %s"%(details_url))
    request = scrapy.Request(
      url = details_url,
      callback=self.after_result
    )
    request.meta['register_number'] = response.meta['register_number']
    yield request

  def after_result(self, response):
    qs_set = response.xpath('//table[@id="Relations_ListView_itemPlaceholderContainer"]/tr')
    self.logger.info("for %s got %s aliens"%(response.meta['register_number'], len(qs_set)))
    for quote in qs_set:
      q2 = quote.xpath('td[1]/span/text()').extract()
      if len(q2)==0: continue
      q2=q2[0]
      yield {
        'register_number': response.meta['register_number'],
        'obligor_alien': q2,
      }
 

class ScrapyCrJusticeGovLbSpiderCsv(ScrapyCrJusticeGovLbSpiderBase):
  """
  Instead of a pd.DataFrame in the constructor, read a csv file with
  fields "register_number, register_place" which can be read with
  pd.read_csv
  """
  name = "cr_justice_gov_lb_csv"
  def __init__(self, csv_in:pd.DataFrame, *args, **kwargs):
    df_in = pd.read_csv(csv_in)
    super().__init__(df_in=df_in, *args, **kwargs)
