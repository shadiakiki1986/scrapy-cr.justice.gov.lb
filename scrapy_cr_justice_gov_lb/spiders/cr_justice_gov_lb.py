import scrapy

class ScrapyCrJusticeGovLbSpider(scrapy.Spider):
  """
  curl --data "FindBox=5000780" http://cr.justice.gov.lb/search/res_list.aspx
  """

  name = "quotes"
  start_urls = [
    'http://cr.justice.gov.lb/search/res_list.aspx',
  ]

  def __init__(self, df_in:pd.DataFrame, *args, **kwargs):
    super().__init__(*args, **kwargs)
    missing_cols = set(['register_number', 'register_place']) - set(df_in.columns)
    if len(missing_cols)>0:
      raise ValueError("Missing columns: %s"%", ".join(missing_cols))
    self.df_in = df_in

  def parse(self, response):
    qs_set = ObligorParty.objects.filter(obligor_type='CO', register_number__isnull=False).all()
    # FIXME
    qs_set = qs_set[:3]
    for qs_single in qs_set:
      self.logger.info("searching for %s"%qs_single.register_number)
      request = scrapy.FormRequest.from_response(
        response,
        formdata={'FindBox': qs_single.register_number},
        callback=self.after_search
      )
      request.meta['register_number'] = qs_single.register_number
      request.meta['register_place'] = qs_single.register_place
      yield request


  def after_search(self, response):
    n_res = response.xpath('//span[@id="DataList1_rec_countLabel_0"]/text()').extract_first()
    n_res = int(n_res)
    self.logger.info("for {number: %s, place: %s} got %s results"%(response.meta['register_number'], response.meta['register_place'], n_res))
    if n_res == 0:
      raise ValueError("Not found. Aborting")

    if n_res >  1:
      details_url = response.xpath('//div[@id="ListView1_itemPlaceholderContainer"]/div[@class="res_line2" and contains(string(), "%s")]/preceding-sibling::div[last()]/a/@href'%(response.meta['register_place']))
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
 
