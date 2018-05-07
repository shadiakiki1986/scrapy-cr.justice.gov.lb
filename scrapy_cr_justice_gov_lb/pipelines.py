# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging
import pandas as pd
import datetime as dt
import os
from google.cloud import translate

class ScrapyCrJusticeGovLbPipeline(object):
    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.df = pd.DataFrame()

    def process_item(self, item, spider):
      #print("----"*10)
      #print("----"*10)
      print("appending item to pipeline df")
      item2 = dict(item)
      self.df = self.df.append(item2, ignore_index=True)
      return item
  
    def close_spider(self, spider):
      if self.df.shape[0]==0:
        logging.info("No results to show")
        return

      # drop duplicates
      self.df = self.df[~self.df.duplicated()]
  
      # transliterate
      if os.getenv('GOOGLE_APPLICATION_CREDENTIALS', None) is not None:
        translate_client = translate.Client()
        get_trans = lambda text: translate_client.translate(text, target_language='en')['translatedText']
        self.df['name_en'] = self.df['obligor_alien'].apply(get_trans)
        
      # print
      print(self.df)
  
      # save to file
      import tempfile
      default_tmp_dir = tempfile._get_default_tempdir()
      suffix_2 = next(tempfile._get_candidate_names())
      suffix_1 = dt.datetime.strftime(dt.datetime.now(), "%Y%m%d_%H%M%S")
      temp_name = "scrape_%s_%s.csv"%(suffix_1, suffix_2)
      fn = os.path.join(default_tmp_dir, temp_name)
      self.df.to_csv(fn)
      print("Save to %s"%fn)
