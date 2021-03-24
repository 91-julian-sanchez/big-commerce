import argparse
from os import walk
import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraper_motor.scraper_motor.spiders.category_glossary import CategoryGlossarySpider
from common import config
from bootstrap import Bootstrap
from menu import CliMenu
from multiprocessing import Process, Queue

def crawl():
  crawler = CrawlerProcess({
        'LOG_ENABLED': False
  })
  crawler.crawl(CategoryGlossarySpider, config_path='./')
  crawler.start()

def crawl2():
  process = CrawlerProcess({
    'LOG_ENABLED': False
  })
  process.crawl(CategoryGlossarySpider, config_path='./', category_level=2, category_href="https://www.mercadolibre.com.co/c/deportes-y-fitness#c_id=/home/categories/category-l1/category-l1&c_category_id=MCO1276&c_uid=57b3e67f-8c42-11eb-8ac8-7d7e2c82dfcf")
  process.start()

def select_marketplace_menu():
  climenu = CliMenu(
    name='marketplace',
    message='Que marketplace quieres scrapear?',
    choices=Bootstrap.get_marketplace_avalible()
  )
  selected = climenu.start()
  # print(selected)
  return selected

def select_country_menu(marketplace):
  # TODO Init scraper
  # * Select country
  bootstrap = Bootstrap(marketplace)
  climenu = CliMenu(
    name='country',
    message='Que país?',
    choices=list(bootstrap.countries_config.keys())
  )
  selected = climenu.start()
  # print(selected)
  return selected

def select_category_menu(categories_dict):
  # TODO Init scraper
  # * Select country
  climenu = CliMenu(
    name='category',
    message='Que categoria?',
    choices=categories_dict.keys()
  )
  selected = climenu.start()
  # print(categories_dict.get(selected.get('category')))
  selected['category'] = categories_dict.get(selected.get('category'))
  return selected

def motor_scraper_start(marketplace_selected, country_selected, category_level=None, category_href=None):
  # process = CrawlerProcess(get_project_settings())
  if marketplace_selected == 'mercadolibre':
    
    if category_level is not None and category_href is not None:
      process = Process(target=crawl2)
      process.start()
      process.join()
    else:
      process = Process(target=crawl)
      process.start()
      process.join()
  else:
    print("linio no esta en scrapy")
    
def open_last_scrapy_file():
  _, _, filenames = next(walk("./.output"))
  path = f"./.output/{filenames[len(filenames)-1]}"
  df = pd.read_csv(path)
  df = df[['id','name','href']]
  # print(df.head())
  return df

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  # # TODO Select marketplace
  # parser.add_argument('marketplace', help='The marketplace that you want to scraper', type=str, choices=Bootstrap.get_marketplace_avalible())
  # * Init scraper
  args = parser.parse_args()
  marketplace_selected = select_marketplace_menu().get('marketplace')
  country_selected = select_country_menu(marketplace_selected).get('country')
  motor_scraper_start(marketplace_selected, country_selected)
  # process.stop()
  print("ya acabe....")
  category_glossary_df = open_last_scrapy_file()
  href_category_selected = select_category_menu(dict(zip(category_glossary_df['name'], category_glossary_df['href']))).get('category')
  # print(marketplace_selected, country_selected, href_category_selected)
  # * LEVEL 2
  motor_scraper_start(marketplace_selected, country_selected, category_level=2, category_href=href_category_selected)
  category_glossary_df = open_last_scrapy_file()
  href_category_selected = select_category_menu(dict(zip(category_glossary_df['name'], category_glossary_df['href']))).get('category')
  # print(marketplace_selected, country_selected, href_category_selected)
  
  