import scrapy
import pandas as pd
import time

def validate_df_in(df_in):
    missing_cols = set(['register_number', 'register_place']) - set(df_in.columns)
    if len(missing_cols)>0:
      raise ValueError("Missing columns: %s"%", ".join(missing_cols))
    
    if df_in['register_number'].dtype!='object':
        raise ValueError("register_number should be a str. Received %s"%df_in['register_number'].dtype)
    
map_place = {
    'Mount Lebanon': 'جبل لبنان',
    'South Lebanon': 'الجنوب',
    'Saida': 'الجنوب',
}
def preprocess_df_in(df_in):
    df_in['register_place'] = df_in['register_place'].apply(lambda x: map_place[x] if x in map_place else x)
    return df_in
    
MAX_PAGES = 10 # 10 pages = 100 results at 10 results per page

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
#    df_in = df_in[df_in['register_number']=='5792'] # FIXME
#    df_in = df_in[df_in['register_number']=='66942'] # FIXME
#    df_in = df_in[~df_in['register_number'].isin(['5792','66942'])] # FIXME
#    df_in = df_in[df_in['register_number']=='2471'] # FIXME
    print("input df")
    print(df_in)

    # prepare fields to be appended
    df_in['details_url'] = None
    df_in['obligor_alien'] = None
    df_in['relationship'] = None

    # save and return
    self.df_in = df_in
    return super().__init__(*args, **kwargs)

  def parse(self, response):
    for index, row in self.df_in.iterrows():
      yield self.request_search(response, index, row['register_number'], row['register_place'])

  def request_search(self, response, index, register_number, register_place):
      self.logger.info("searching for %s - %s"%(register_number, register_place))
      request = scrapy.FormRequest.from_response(
        response,
        formdata={'FindBox': register_number},
        callback=self.after_search
      )
      #self.logger.info('parse .. request =')
      request.meta['register_number'] = register_number
      request.meta['register_place'] = register_place
      request.meta['df_idx'] = index
      self.logger.info('yield parse')
      return request


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

    # show total number of results
    n_res = response.selector.xpath('//span[@id="DataList1_rec_countLabel_0"]/text()').extract_first()
    n_res = int(n_res)
    self.logger.info(
        "for {number: %s, place: %s} total of %s results"%(
            response.meta['register_number'], 
            response.meta['register_place'], n_res
        )
    )
    
    """
    # try to extract a single result

    if n_res == 0:
      raise ValueError("Not found. Aborting")

    if n_res == 1:
      details_url = response.selector.xpath('//div[@id="ListView1_itemPlaceholderContainer"]/div[@class="res_line1"]/a/@href').extract_first()
      return self.process_details_url(details_url, response)

    # filter for exact match .. note that cr.justice.gov.lb search for "123" would include results with "5123, 6123, 123, ..."
    self.logger.info('filter for exact match')
    details_url = response.selector.xpath('//div[@id="ListView1_itemPlaceholderContainer"]/div[@class="res_line1" and starts-with(string(), "%s ")]/a/@href'%(response.meta['register_number']))
    self.logger.info("Filtered down to %s results"%len(details_url))
    if len(details_url) == 1:
        if not is_multi:
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
            raise ValueError("Filter by exact failed. Aborting")
        else:
          return self.move_to_next_page(response, has_next)

    # print(details_url)

    # filter by register_place
    self.logger.info('filter for register place')
    """
    details_url = response.selector.xpath('//div[@id="ListView1_itemPlaceholderContainer"]/div[@class="res_line1" and starts-with(string(), "%s ")]/following-sibling::div[@class="res_line2"][1][contains(string(), "%s")]/preceding-sibling::div[@class="res_line1"][1]/a/@href'%(response.meta['register_number'], response.meta['register_place']))
    if len(details_url)>=1:
        print(response.body.decode('utf-8'))
        
    if len(details_url) > 1:
        # print(details_url)
        raise ValueError("Need to filter further. Aborting")
        
    if len(details_url) == 0:
        if not is_multi:
            raise ValueError(
                "Filtered down to %s results. %s. Aborting"%(
                    len(details_url), 
                    "Need to filter further" if len(details_url) > 1 else "Entity not found"
                )
            )
        else:
            return self.move_to_next_page(response, has_next)


    details_url = details_url.extract_first()
    if not is_multi:
        self.logger.info("filtered down to 1")
        return self.process_details_url(details_url, response)
    else:
        if response.meta['page_items'] is None:
            response.meta['page_items'] = []
            response.meta['page_items'].append(details_url)
        else:
            # check that this item was not already in a previous page
            if details_url in response.meta['page_items']:
                print("&"*100)
                print("&"*100)
                print("&"*100)
                self.logger.info("Already saw this result. Not appending")
            else:
                self.logger.info("Appending new result")
                response.meta['page_items'].append(details_url)
                print(response.meta['page_items'])
                raise ValueError("Got more than 1 result. Aborting")

        return self.move_to_next_page(response, has_next)

  def move_to_next_page(self, response, has_next):
    # if multi-page scenario, gather all results first
    self.logger.info(
        'Moving to next page. Current page: %s. Num results: %s'%(
            response.meta['page_num'],
            0 if response.meta['page_items'] is None else len(response.meta['page_items'])
        )
    )
    if response.meta['page_items'] is not None:
        #if len(response.meta['page_items'])>0:
        #    print(response.meta['page_items'])
        if len(response.meta['page_items'])>1:
            raise ValueError("Found at least %s results. Need to filter further. Aborting"%(len(response.meta['page_items'])))
        
    if not has_next or response.meta['page_num'] >= MAX_PAGES:
        self.logger.info("max pages reached" if response.meta['page_num'] >= MAX_PAGES else "no more pages with multi-page")
            
        if response.meta['page_items'] is None:
            raise ValueError("after multi-page, didnt find any results")
            
        if len(response.meta['page_items'])==1:
            details_url = response.meta['page_items'][0]
            self.logger.info("concluding multi-page")
            request = [self.process_details_url(details_url, response)]
            request = request[0]
            return request
            #return
        
        raise ValueError("after multi-page, found %s results. Need to filter further"%len(response.meta['page_items']))

    # if there are multiple pages, get the next page and re-parse with after_search
    time.sleep(.5)   # delays for x seconds
    request = scrapy.FormRequest.from_response(
      response,
      formdata={'DataPager1$ctl00$ctl02': 'true'},
      callback=self.after_search
    )
    request.meta.update(response.meta)
    return request

  def process_details_url(self, details_url, response):
    self.logger.info("details at %s"%(details_url))
    response.meta['details_url'] = details_url
    details_url =  'http://cr.justice.gov.lb/search/' + details_url
    self.logger.info("details at %s"%(details_url))
    request = scrapy.Request(
      url = details_url,
      callback=self.after_result
    )
    request.meta.update(response.meta)
    return request

  def after_result(self, response):
    qs_set = response.xpath('//table[@id="Relations_ListView_itemPlaceholderContainer"]/tr')
    self.logger.info("for %s got %s aliens"%(response.meta['register_number'], len(qs_set)))
    for quote in qs_set:
      q2 = quote.xpath('td[1]/span/text()').extract()
      if len(q2)==0: continue
      q2=q2[0]
      q3 = quote.xpath('td[3]/span/text()').extract_first()

      # check nothing went wrong 
      idx = response.meta['df_idx']
      if self.df_in.loc[idx, 'register_number'] != response.meta['register_number']:
        raise ValueError("df_in[idx,register_number'] mismatch with response")

      if self.df_in.loc[idx, 'register_place'] != response.meta['register_place']:
        raise ValueError("df_in[idx,register_place'] mismatch with response")

      # save in df_in
      self.df_in.loc[idx, 'details_url'] = response.meta['details_url']
      self.df_in.loc[idx, 'obligor_alien'] = q2
      self.df_in.loc[idx, 'relationship'] = q3

      # TODO simplify by
      # - yield idx
      # - use spider.df_in in the pipeline.close_spider
      # - delete the function pipeline.process_item
      yield dict(self.df_in.loc[idx])
 

class ScrapyCrJusticeGovLbSpiderCsv(ScrapyCrJusticeGovLbSpiderBase):
  """
  Instead of a pd.DataFrame in the constructor, read a csv file with
  fields "register_number, register_place" which can be read with
  pd.read_csv
  """
  name = "cr_justice_gov_lb_csv"
  def __init__(self, csv_in:pd.DataFrame, *args, **kwargs):
    df_in = pd.read_csv(
        csv_in,
        # keep as string
        # Why "object": https://stackoverflow.com/a/16988624/4126114
        dtype={'register_number': object} 
    )
    super().__init__(df_in=df_in, *args, **kwargs)


class ScrapyCrJusticeGovLbSpiderSingle(ScrapyCrJusticeGovLbSpiderBase):
  name = "cr_justice_gov_lb_single"
  def __init__(self, register_number, register_place, *args, **kwargs):
    df_in = pd.DataFrame({'register_number': [register_number], 'register_place': [register_place]})
    super().__init__(df_in=df_in, *args, **kwargs)

