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
  df = df[['id','name','href']]
  # print(df.head())
  return df


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  # # TODO Select marketplace
  # parser.add_argument('marketplace', help='The marketplace that you want to scraper', type=str, choices=Bootstrap.get_marketplace_avalible())
  
  # * Select country args --country {ISO_3166_COUNTRY_CODE} 
  parser.add_argument("--debug", required=False, help=f"DEBUG MODE", choices=['True', 'False'])
  args = parser.parse_args()
  marketplace_selected = select_marketplace_menu().get('marketplace')
  country_selected = select_country_menu(marketplace_selected).get('country')
  DEBUG_MODE = True if args.debug == 'True' else False
  
  # TODO INIT SCRAPER ==================================================================================================================
  
  # * LEVEL 1
  motor_scraper_start(marketplace_selected, country_selected, debug=DEBUG_MODE)
  category_glossary_df = open_last_scrapy_file()
  href_category_selected = select_category_menu(dict(zip(category_glossary_df['name'], category_glossary_df['href']))).get('category')
  
  # * LEVEL 2
  motor_scraper_start(marketplace_selected, country_selected, category_level=2, category_href=href_category_selected, debug=DEBUG_MODE)
  category_glossary_df = open_last_scrapy_file()
  href_category_selected = select_category_menu(dict(zip(category_glossary_df['name'], category_glossary_df['href']))).get('category')
  
  # * LEVEL 4
  # motor_scraper_start(marketplace_selected, country_selected, category_level=4, category_href=href_category_selected)
  # category_glossary_df = open_last_scrapy_file()
  # href_category_selected = select_category_menu(dict(zip(category_glossary_df['name'], category_glossary_df['href']))).get('category')