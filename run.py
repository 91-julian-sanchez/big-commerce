import argparse
import os
from os import walk
import subprocess
import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraper_motor.scraper_motor.spiders.category_glossary import CategoryGlossarySpider
from common import config
from bootstrap import Bootstrap
from menu import CliMenu
from multiprocessing import Process, Queue
CRAWL_SETTINGS = {
   'LOG_ENABLED': False
}


def crawl():
  crawler = CrawlerProcess(CRAWL_SETTINGS)
  crawler.crawl(CategoryGlossarySpider, config_path='./')
  crawler.start()


def crawl2(category_level=None,category_href=None):
  crawler = CrawlerProcess(CRAWL_SETTINGS)
  crawler.crawl(CategoryGlossarySpider, config_path='./', category_level=category_level, category_href=category_href)
  crawler.start()


def crawl3(category_level=None,category_href=None,xxx=None):
  print("aca estoy reputo")
  crawler = CrawlerProcess(CRAWL_SETTINGS)
  crawler.crawl(CategoryGlossarySpider, config_path='./', category_level=category_level, category_href=category_href, xxx=xxx)
  crawler.start()


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


def select_category_menu(choices):
  # TODO Init scraper
  # * Select country
  climenu = CliMenu(
    name='category',
    message='Que categoria?',
    choices=choices
  )
  selected = climenu.start()
  # print(categories_dict.get(selected.get('category')))
  print("selected: ", selected)
  return selected.get('category')


def motor_scraper_subprocess_shell(category_level=None, category_href=None, debug=False):
  wd = os.getcwd()
  os.chdir("scraper_motor/scraper_motor/spiders/")
  # subprocess.Popen("ls")
  nolog = '--nolog'
  if debug is True:
    nolog = ''
  if category_level is not None and category_href is not None:
    command = f"scrapy crawl category_glossary -a category_level={category_level} -a category_href={category_href} {nolog}"
  else:
    command = f"scrapy crawl category_glossary {nolog}"
    
  # print(f"command>> {command}")
  subprocess.run(command)
  os.chdir(wd)


def motor_scraper_start(marketplace_selected, country_selected, category_level=None, category_href=None, debug=None):
  print("Extrayendo datos...")
  # process = CrawlerProcess(get_project_settings())
  if marketplace_selected == 'mercadolibre':
    motor_scraper_subprocess_shell(category_level=category_level, category_href=category_href, debug=debug)
  else:
    print("linio no esta en scrapy")


def open_last_scrapy_file():
  _, _, filenames = next(walk("./.output"))
  path = f"./.output/{filenames[len(filenames)-1]}"
  df = pd.read_csv(path)
  df = df[['id','name','href','hierarchy','parent']]
  # print(df.head())
  return df


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  # # TODO Select marketplace
  # parser.add_argument('marketplace', help='The marketplace that you want to scraper', type=str, choices=Bootstrap.get_marketplace_avalible())
  
  parser.add_argument("--debug", required=False, help=f"DEBUG MODE", choices=['True', 'False'])
  args = parser.parse_args()
  DEBUG_MODE = True if args.debug == 'True' else False
  
  marketplace_selected = select_marketplace_menu().get('marketplace')
  # * Select country args --country {ISO_3166_COUNTRY_CODE} 
  country_selected = select_country_menu(marketplace_selected).get('country')
  
  # TODO INIT SCRAPER ==================================================================================================================
  # tree = {
  #   'hierarchy':None,'href':None,'id':None,'index':None,'name':None,'parent':None,'subcategories':None,'uid':None
  # }
  # * LEVEL 1
  motor_scraper_start(marketplace_selected, country_selected, debug=DEBUG_MODE)
  category_glossary_df = open_last_scrapy_file()
  categories = dict(zip(category_glossary_df['name'], category_glossary_df['href']))
  category_selected = select_category_menu(categories.keys())
  href_category_selected = categories.get(category_selected)
  
  # * LEVEL 2
  motor_scraper_start(marketplace_selected, country_selected, category_level=2, category_href=href_category_selected, debug=DEBUG_MODE)
  category_glossary_df = open_last_scrapy_file()
  level_2_category_glossary_df = category_glossary_df[category_glossary_df['hierarchy']==2]
  choices = []
  parent_id = None
  for index, row in level_2_category_glossary_df.iterrows():
    print("level 2:", row['name'])
    name_parent = row['name']
    parent_id = row['id']
    choices.append(name_parent)
    
  # * LEVEL 3    
  category_selected = select_category_menu(choices)
  category_id_selected = category_glossary_df[category_glossary_df['name']==category_selected]['id'].iloc[0]
  print("category_selected: ", category_selected, category_id_selected)
  level_3_category_glossary_df = category_glossary_df[category_glossary_df['parent']==category_id_selected]
  for index, row in level_3_category_glossary_df.iterrows():
    print("   ", row['name'])
    try:
        # * LEVEL 4
        motor_scraper_start(marketplace_selected, country_selected, category_level=4, category_href=row['href'], debug=DEBUG_MODE)
        level_4_category_glossary_df = open_last_scrapy_file()
        for index, row in level_4_category_glossary_df.iterrows():
          print("    ", row['name'])
    except Exception as e:
      print(e)
