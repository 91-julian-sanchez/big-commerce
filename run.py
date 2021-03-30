import argparse
import os
from os import walk
import subprocess
import csv
import pandas as pd
import scrapy
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraper_motor.scraper_motor.spiders.category_glossary import CategoryGlossarySpider
from common import config
from bootstrap import Bootstrap
from menu import CliMenu
from multiprocessing import Process, Queue

def select_marketplace_menu():
  climenu = CliMenu(
    name='marketplace',
    message='Que marketplace quieres scrapear?',
    choices=Bootstrap.get_marketplace_avalible()
  )
  selected = climenu.start()
  # print(selected)
  return selected


def confirm_init_scraper_menu():
  questions = {
    'type': 'confirm',
    'message': 'Extraer productos del arbol de categorias?',
    'name': 'continue',
    'default': True,
  }
  climenu = CliMenu(questions=questions)
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
  # print("selected: ", selected)
  category_selected =  list(filter(lambda choice: choice.get('name') == selected.get('category'), choices))
  if len(category_selected) > 0:
    return category_selected[0]
  else:
    return None


def motor_scraper_subprocess_shell(marketplace=None, country=None, category_level=None, category_href=None, parent=None, debug=False, pid=None):
  wd = os.getcwd()
  os.chdir("scraper_motor/scraper_motor/spiders/")
  # subprocess.Popen("ls")
  nolog = '--nolog'
  if debug is True:
    nolog = ''
  
  argument_country = ''
  if country is not None:
    argument_country = f'-a country={country}'
    
  argument_parent = ''
  if parent is not None:
    argument_parent = f'-a parent={parent}'
    
  output = ''
  if pid is not None:
    output = f'-o ../../../.output/{pid}-{marketplace}-{country}-categories.csv'
    
  if category_level is not None and category_href is not None:
    command = f"scrapy crawl category_glossary {argument_country} -a category_level={category_level} -a category_href={category_href} {argument_parent} {output} {nolog}"
  else:
    command = f"scrapy crawl category_glossary {argument_country} {output} {nolog}"
    
  # print(f"command>> {command}")
  subprocess.run(command)
  os.chdir(wd)


def motor_scraper_start(marketplace, country, category_level=None, category_href=None, parent=None, debug=None, pid=None):
  # print("Extrayendo datos...")
  # process = CrawlerProcess(get_project_settings())
  if marketplace == 'mercadolibre':
    motor_scraper_subprocess_shell(marketplace=marketplace, country=country, category_level=category_level, parent=parent, category_href=category_href, debug=debug, pid=pid)
  else:
    print("linio no esta en scrapy")


def remove_duplicates_header_rows(path):
  with open(path) as f:
    data = list(csv.reader(f))
    new_data = [a for i, a in enumerate(data) if a not in data[:i]]
    with open(path, 'w') as t:
      write = csv.writer(t)
      write.writerows(new_data)

      
def open_last_scrapy_file(pid=None):
  _, _, filenames = next(walk("./.output"))
  path = f"./.output/{filenames[len(filenames)-1]}"
  remove_duplicates_header_rows(path)
  df = pd.read_csv(path)
  return df


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  ## TODO Select marketplace
  # * Config marketplace
  parser.add_argument('--marketplace', required=False, help='The marketplace that you want to scraper', type=str, choices=Bootstrap.get_marketplace_avalible())
  # * Config country args --country {ISO_3166_COUNTRY_CODE} 
  parser.add_argument("--country", required=False, help=f"Country where the scrapper will run, avalible: co, mx")
  # * Config DEBUG MODE
  parser.add_argument("--debug", required=False, help=f"DEBUG MODE", choices=['True', 'False'])
  args = parser.parse_args()
  
  DEBUG_MODE = True if args.debug == 'True' else False
  MARKETPLACE_SELECTED = args.marketplace if args.marketplace else select_marketplace_menu().get('marketplace')
  COUNTRY_SELECTED = args.country if args.country else select_country_menu(MARKETPLACE_SELECTED).get('country')
  PID = datetime.today().strftime('%y%m%d%H%M%S')
  
  if MARKETPLACE_SELECTED == 'mercadolibre':

    # TODO INIT SCRAPER ==================================================================================================================
    category_glossary_tree = []
    
    # * LEVEL 1
    print(f"Crawl {MARKETPLACE_SELECTED}: Extrayendo categorias...")
    motor_scraper_start(MARKETPLACE_SELECTED, COUNTRY_SELECTED, pid=PID, debug=DEBUG_MODE)
    category_glossary_df = open_last_scrapy_file(pid=PID)
    categories = [{'name': row['name'], 'href': row['href'], 'id': row['id'], 'parent': row['parent'], 'hierarchy': row['hierarchy']} for index, row in category_glossary_df.iterrows()]
    category_selected = select_category_menu(choices=categories)
    # print("category_selected: ", category_selected)
    category_glossary_tree.append(category_selected)
    
    # * LEVEL 2
    print(f"Crawl {MARKETPLACE_SELECTED}> Extrayendo categorias de '{category_selected.get('name')}'...")
    parent_category = category_selected.copy()
    motor_scraper_start(MARKETPLACE_SELECTED, COUNTRY_SELECTED, pid=PID, category_level=2, category_href=category_selected.get('href'), debug=DEBUG_MODE)
    category_glossary_df = open_last_scrapy_file()
    level_2_category_glossary_df = category_glossary_df[category_glossary_df['hierarchy']==2] 
    categories = [{'name': row['name'], 'href': row['href'], 'id': row['id'], 'parent': row['parent'], 'hierarchy': row['hierarchy']} for index, row in level_2_category_glossary_df.iterrows()]
    category_selected = select_category_menu(choices=categories)
    # print("category_selected: ", category_selected)
    category_glossary_tree.append(category_selected)
    
    # * LEVEL 3    
    print(f"Crawl {MARKETPLACE_SELECTED}: Extrayendo categorias de '{parent_category.get('name')} > {category_selected.get('name')}'...") 
    level_3_category_glossary_df = category_glossary_df[category_glossary_df['parent']==category_selected.get('id')]
    # level_3_category_glossary_df = level_3_category_glossary_df[level_3_category_glossary_df['hierarchy']==3]
    for index, row in level_3_category_glossary_df.iterrows():
      category_glossary_tree.append({'name': row['name'], 'href': row['href'], 'id': row['id'], 'parent': row['parent'], 'hierarchy': row['hierarchy']})
      try:
          # * LEVEL 4
          motor_scraper_start(MARKETPLACE_SELECTED, COUNTRY_SELECTED, pid=PID, category_level=4, category_href=row['href'], debug=DEBUG_MODE, parent=row['id'])
          level_4_category_glossary_df = open_last_scrapy_file()
          level_4_category_glossary_df = level_4_category_glossary_df[level_4_category_glossary_df['parent']==row['id']]
          for index, row in level_4_category_glossary_df.iterrows():
            category_glossary_tree.append({'name': row['name'], 'href': row['href'], 'id': row['id'], 'parent': row['parent'], 'hierarchy': row['hierarchy']})
      except Exception as e:
        print(e)

    # * CONFIRM CRAWL PRODUCTS OF CATEGORIES SELECTED
    bullets = ['',' >','  *', '   -']
    for category in category_glossary_tree:
      print(bullets[category.get('hierarchy')-1], f"{category.get('name')}")
      
  elif MARKETPLACE_SELECTED == 'linio':
    print("iniciar linio main.py")
    
  confirm = confirm_init_scraper_menu()
    
  if confirm.get('continue') is True:
    print("iniciar mercadolibre main.py")