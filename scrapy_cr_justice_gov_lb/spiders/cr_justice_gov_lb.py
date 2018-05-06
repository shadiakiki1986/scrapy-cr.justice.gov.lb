import scrapy
import pandas as pd

def validate_df_in(df_in):
    missing_cols = set(['register_number', 'register_place']) - set(df_in.columns)
    if len(missing_cols)>0:
      raise ValueError("Missing columns: %s"%", ".join(missing_cols))
    
map_place = {
    'Mount Lebanon': 'جبل لبنان',
    'South Lebanon': 'الجنوب',
}
def preprocess_df_in(df_in):
    df_in['register_place'] = df_in['register_place'].apply(lambda x: map_place[x] if x in map_place else x)
    return df_in
    
MAX_PAGES = 3

class ScrapyCrJusticeGovLbSpiderBase(scrapy.Spider):
  """
  curl --data "FindBox=5000780" http://cr.justice.gov.lb/search/res_list.aspx
  """

  name = "cr_justice_gov_lb_base"
  url = 'http://cr.justice.gov.lb/search/res_list.aspx'
  # necessary for `scrapy crawl` call from command-line
  #start_urls = []
  start_urls = ['http://cr.justice.gov.lb/search/res_list.aspx']

  def __init__(self, df_in:pd.DataFrame, *args, **kwargs):
    validate_df_in(df_in)
    df_in = preprocess_df_in(df_in)
    print("input df")
    print(df_in)
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
    
    # multi-page management
    if 'page_num' not in response.meta:
        response.meta['page_num'] = 0
        response.meta['page_items'] = None

    response.meta['page_num'] = response.meta['page_num'] + 1
        
    # if there are multiple pages, get the next page and re-parse with after_search
    has_next = response.selector.xpath('//span[@id="DataPager1"]/input[@name="DataPager1$ctl00$ctl02" and not(@disabled)]')
    has_next = len(has_next) > 0
    is_multi = (response.meta['page_num'] > 1) or (has_next)

    # try to extract a single result
    n_res = response.selector.xpath('//span[@id="DataList1_rec_countLabel_0"]/text()').extract_first()
    n_res = int(n_res)
    self.logger.info("for {number: %s, place: %s} got %s results"%(response.meta['register_number'], response.meta['register_place'], n_res))
    if n_res == 0:
      print("Not found. Aborting")
      return

    if n_res == 1:
      details_url = response.selector.xpath('//div[@id="ListView1_itemPlaceholderContainer"]/div[@class="res_line1"]/a/@href').extract_first()
      return self.process_details_url(details_url, response)

    # filter for exact match .. note that cr.justice.gov.lb search for "123" would include results with "5123, 6123, 123, ..."
    print('filter for exact match')
    details_url = response.selector.xpath('//div[@id="ListView1_itemPlaceholderContainer"]/div[@class="res_line1" and starts-with(string(), "%s ")]/a/@href'%(response.meta['register_number']))
    if len(details_url) == 1:
        if not is_multi:
            self.logger.info("filtered down to 1")
            details_url = details_url.extract_first()
            return self.process_details_url(details_url, response)
        else:
            if response.meta['page_items'] is None:
                response.meta['page_items'] = details_url
            else:
                response.meta['page_items'].append(details_url)
                
            return self.move_to_next_page(response, has_next)

    if len(details_url) == 0:
        if not is_multi:
            print("Filter by exact failed. Aborting")
            return
        else:
          return self.move_to_next_page(response, has_next)

    print("Filtered down to %s results"%len(details_url))
    print(details_url)

    # filter by register_place
    print('filter for register place')
    details_url = response.selector.xpath('//div[@id="ListView1_itemPlaceholderContainer"]/div[@class="res_line2" and contains(string(), "%s")]/preceding-sibling::div[@class="res_line1"][1]/a/@href'%(response.meta['register_place']))
    if len(details_url) == 1:
        if not is_multi:
            self.logger.info("filtered down to 1")
            details_url = details_url.extract_first()
            return self.process_details_url(details_url, response)
        else:
            if response.meta['page_items'] is None:
                response.meta['page_items'] = details_url
            else:
                response.meta['page_items'].append(details_url)

            return self.move_to_next_page(response, has_next)

    if len(details_url) > 1:
        # print(details_url)
        print("Need to filter further. Aborting")
        return
        
    print("Filtered down to %s results"%len(details_url))
    print("Filter failed. Aborting")
    return

  def move_to_next_page(self, response, has_next):
    # if multi-page scenario, gather all results first
    self.logger.info('page num %s'%response.meta['page_num'])
    if not has_next or response.meta['page_num'] > MAX_PAGES:
        print("max pages exceeded" if response.meta['page_num'] > MAX_PAGES else "done with multi-page")
            
        if len(response.meta['page_items'])==1:
            details_url = response.meta['page_items']
            details_url = details_url.extract_first()
            return self.process_details_url(details_url, response)
        
        print("after multi-page, found %s results"%len(response.meta['page_items']))
        return

    # if there are multiple pages, get the next page and re-parse with after_search
    request = scrapy.FormRequest.from_response(
      response,
      formdata={'DataPager1$ctl00$ctl02': 'true'},
      callback=self.after_search
    )
    request.meta.update(response.meta)
    yield request

  def process_details_url(self, details_url, response):
    details_url =  'http://cr.justice.gov.lb/search/' + details_url
    self.logger.info("details at %s"%(details_url))
    request = scrapy.Request(
      url = details_url,
      callback=self.after_result
    )
    request.meta['register_number'] = response.meta['register_number']
    #yield request
    yield None

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
