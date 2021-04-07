import argparse
import logging
import datetime
import csv
import re
import time
import random
import pandas as pd
import page_objects as pages
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError
from bootstrap import Bootstrap, select_category_menu, confirm_init_scraper_menu
from datetime import datetime
from bcolors import bcolors
from utils import is_true

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
is_well_formed_link = re.compile(r'^https?://.+/.+$')
is_root_path = re.compile(r'^/.+$')
total_products_scraped = 0


def menu(options: list, label=None) -> int:
    """
    Create a menu in console
    :param label:
    :param options: String array
    :return: Index of the selected option
    """
   
    if label is not None:
        print(bcolors.OKBLUE, f"({len(options)}) {label}:", bcolors.ENDC)
        
    for index, option in enumerate(options):
        print(f"""  {index + 1}. {option}""")

    selected = None

    while selected is None:
        
        try:
            
            option = int(input("Ingrese opción: ")) - 1
            if -1 < option < len(options):
                selected = option
            else:
                print(bcolors.FAIL, "Error: Seleccione una opción valida.", bcolors.ENDC)
                
        except ValueError:
            print(bcolors.FAIL, "Error: Debe ingresar un numero.", bcolors.ENDC)

    return selected


def _build_link(host, link):
    if is_well_formed_link.match(link):
        return link
    else:
        return f"{host}/{link}"


def _fetchProduct(marketplace,  link):
    # logger.info(f'Start fetching product at {link}')

    product = None
    try:
        product_page = pages.ProductPage(marketplace, link)
        product = product_page.get_product()
    except (HTTPError, MaxRetryError) as e:
        logger.warning('Error while fetching article!', exc_info=False)
        pass

    return product


def _save_products(marketplace_uid, country_uid, products, overwrite=True, pid=None):
    # print("_save_products", products)
    out_file_name = f'./.output/{pid}-{marketplace_uid}_{country_uid}_products.csv'
    csv_headers = list(products[0].keys())

    if overwrite is True:
        with open(out_file_name, mode='w+') as f:
            writer = csv.writer(f)
            writer.writerow(csv_headers)

            for product in products:
                writer.writerow(list(product.values()))
    else:      
        from csv import writer
        with open(out_file_name, 'a+', newline='') as f:
            writer = writer(f)
            # writer.writerow(csv_headers)
                
            for product in products:
                writer.writerow(list(product.values()))

    pass


def scrapperProducts(products, marketplace_uid, country_uid, category_id=None, overwrite=True, pid=None):
    logger.info(f" \n\nPRODUCTOS({len(products)}):\n")
    global total_products_scraped
    for counter, product in enumerate(products, 1):
        # logger.info(f"""
        #             ======================================================================
        #             {counter}. {product['name']}
        #             ======================================================================
        #             Precio: {product['price_simbol'] if product['price_simbol'] else ''} {product['price']}
        #             Descuento: {product['price_discount']}
        #             Más Vendido: {product['best_seller']}
        #             Promocionado (Ads): {product['promotional']}
        #             link: {product['link']}
        #             """)
        print(f"{counter}. {product.get('name')}")
        # # TODO Scrapper product
        product['number_sales'] = None
        product['seller'] = None
        product['delivery'] = None
        product['rating'] = None
        if marketplace_uid == 'mercadolibre':
            try:
                # scraper_sleep = random.randint(1,9)
                scraper_sleep = 0.2
                # print(f"Siguiente producto en {scraper_sleep}(s)")
                time.sleep(scraper_sleep)
                product_page = _fetchProduct(marketplace_uid,  product['link'])
                if product_page is not None:
                    product['number_sales'] = product_page.get('number_sales')
                    product['seller'] = product_page.get('seller')
                    product['delivery'] = product_page.get('delivery')
                    product['rating'] = product_page.get('rating')
                    
            except Exception as e:
                print("Fallo product_page.get_product()")
                print(e)

        product['category_id'] = category_id
        counter += 1
    print(f"products scraped: {len(products)}")
    total_products_scraped += len(products)
    print(f"products total: {total_products_scraped}")
    _save_products(marketplace_uid, country_uid, products, overwrite=overwrite, pid=pid)
    return counter


def scrapper_marketplace(marketplace_uid, country_uid,  link=None, category_id=None, overwrite=True, recursive=False, products_counter=0, pid=None):
    """
    Scraper start function
    :param link:
    :param category_id:
    :param marketplace_uid: marketplace id for marketplace scraper
    :param country_uid: country id for marketplace scraper
    """

    # TODO INIT PRODUCTS SCRAPER
    print(bcolors.OKCYAN,f"""
            Inicia scrapper...
            """, bcolors.ENDC)
    productsPage = pages.ProductSectionPage(marketplace_uid, link, country_id=country_uid, category_id=category_id)    
    scrapperProducts(productsPage.produtcs, marketplace_uid, country_uid, category_id=category_id, overwrite=overwrite, pid=pid)
    # print(recursive, type(recursive))
    # raise Exception("kill")
    # TODO BROWSE PAGES
    if marketplace_uid == 'mercadolibre':
        paginationSectionPage = pages.PaginationSectionPage(marketplace_uid, link, country_id=country_uid)
        paginator = paginationSectionPage.getPaginator()
        products_counter += len(productsPage.produtcs)
        print(bcolors.OKCYAN,f"""
            productos: {len(productsPage.produtcs)}
            Pagina {paginator['current_page']} de {'primeras' if paginator['has_more_pages'] else ''} {paginator['count']}
            {"...."*30}
            Total productos: {products_counter}
        """, bcolors.ENDC)
            
        # * NEXT PAGE
        if paginator['current_page'] is not None and paginator['next_page_url'] is not None:
            print("* Siguiente pagina?")
            
            if recursive is True:
                scraper_sleep = random.randint(1,10)
                print(f"Si, siguiente pagina en {scraper_sleep}(s)")
                time.sleep(scraper_sleep)
                scrapper_marketplace(marketplace_uid, country_uid,  link=paginator['next_page_url'], category_id=category_id, overwrite=False, recursive=recursive, products_counter=products_counter, pid=pid) 
            elif menu(['Si','No']) == 0:
                scrapper_marketplace(marketplace_uid, country_uid,  link=paginator['next_page_url'], category_id=category_id, overwrite=False, products_counter=products_counter, pid=pid )
        elif paginator['next_page_url'] is None:
            print("Termina scrapper")
    else:
        print(bcolors.OKCYAN,f"""
            Total productos: {len(productsPage.produtcs)}
            Pagina 1 de (?)
        """, bcolors.ENDC)
        
            
def run(
    marketplace_uid: str, country_uid: str, origin: str,
    category_id=None, categories_path=None, pid=None, recursive=False):
    """[summary]

    Args:
        marketplace_uid (str): marketplace to scrape
        country_uid (str): country code
        origin (str): domain marketplace
        url_categories (str): [description]
        category_id ([type], optional): category to scrape
        recursive (bool, optional): scraper recursive MODE
        categories_path ([type], optional): path categories csv file
        pid ([type], optional): id process scraper
    """
    scraper_link = None
    categories_to_scraper = []
    # TODO Scrapper Subcategorias
    df = pd.read_csv(categories_path)
    if marketplace_uid == 'mercadolibre':
        df = df[['id', 'name', 'href', 'hierarchy','parent']]

        level3_df = df[df['parent']==category_id]
        level4_df = df[
            df['parent'].apply( lambda parente_id: parente_id in list(level3_df['id'].unique()) ) 
        ]
        result = pd.concat([level3_df, level4_df])
        for index, row in df.iterrows():
            if row['parent'] == category_id:
                categories_to_scraper.append((row['id'], row['href']))
        
    elif marketplace_uid == 'linio':
        df = df[['id', 'name', 'href', 'hierarchy','parent']]
        for index, row in df.iterrows():
            if row['id'] == category_id:
                categories_to_scraper.append((row['id'], row['href']))
        
    # TODO Iniciar scrapper
    for category_id, link in categories_to_scraper:
        try:
            scrapper_marketplace(marketplace_uid, country_uid, link=link, category_id=category_id, recursive=recursive, overwrite=False, pid=pid)
        except Exception as e:
            print("An exception occurred")
            print(e)
        

def main(marketplace: str, country: str, recursive: bool, category_id: str = None , categories_path: str = None, marketplace_config: dict = None, pid :str = None):
    """
    :param marketplace: name of marketplace
    :param country: code country in standard ISO_3166_COUNTRY_CODE
    :param categories_path: path categories generated with scrapy
    """
    run(
        marketplace, 
        country, 
        pid=pid,
        origin=marketplace_config['origin'],  # * Url marketplace Website
        category_id=category_id,
        categories_path=categories_path,
        recursive=recursive)


def get_marketplace(marketplace: str, available_marketplaces: list):
    if marketplace is None:
        marketplace = Bootstrap.select_marketplace(available_marketplaces=available_marketplaces)
    return marketplace


def get_country(country: str, marketplace: str):
    if country is None:
        country = Bootstrap.select_country(marketplace)
    return country


def parse_args(available_marketplaces: list):
    parser = argparse.ArgumentParser()
    # * Select marketplace
    parser.add_argument('--marketplace', help='The marketplace that you want to scraper', type=str,
                        choices=available_marketplaces)
    # * Select country args --country {ISO_3166_COUNTRY_CODE}
    parser.add_argument("--country", required=False, help=f"Country where the scrapper will run, avalible: co, mx, cl")
    # * Config DEBUG MODE
    parser.add_argument("--debug", required=False, help=f"DEBUG MODE", choices=['True', 'False'])
    # * Recursive scrapper pages
    parser.add_argument("--recursive", required=False, help=f"Recursive scrapper pages: True or False")
    # * Categories tree path
    parser.add_argument("--categories_path", required=False, help=f"Categories path")
    # * Scraper product
    parser.add_argument("--product_link", required=False, help=f"Product link to scraper")
    return parser.parse_args()


def scraper_categories(marketplace, country, pid, debug_mode):
    categories = bootstrap.category_glossary(marketplace, country, pid, debug_mode)
    category_selected = select_category_menu(choices=categories)
    return categories, category_selected


if __name__ == '__main__':
    
    # TODO scraper settings
    AVAILABLE_MARKETPLACES = Bootstrap.get_available_marketplaces()
    PID = datetime.today().strftime('%y%m%d%H%M%S')
    # * Options args
    args = parse_args(AVAILABLE_MARKETPLACES)
    DEBUG_MODE = is_true(args.debug)
    MARKETPLACE = get_marketplace(args.marketplace, AVAILABLE_MARKETPLACES)
    COUNTRY = get_country(args.country, MARKETPLACE)
    
    if args.product_link is None:
        RECURSIVE = is_true(args.recursive)
        categories_path = args.categories_path
        bootstrap = Bootstrap(MARKETPLACE, COUNTRY, recursive=RECURSIVE, debug=DEBUG_MODE)
        category_glossary_tree = []
        category_selected = None
        confirm_message = 'Extraer productos de categorias?'

        if categories_path is None:

            categories_path = f'./.output/{PID}-{MARKETPLACE}-{COUNTRY}-categories.csv'
            # * LEVEL 1
            categories, category_selected = scraper_categories(MARKETPLACE, COUNTRY, PID, DEBUG_MODE)
            category_glossary_tree.append(category_selected)

            if MARKETPLACE == 'mercadolibre':
                # TODO INIT CATEGORY GLOSSARY SCRAPER ===============================================
                parent_category_selected = category_selected
                # * LEVEL 2
                categories = bootstrap.category_glossary(
                    MARKETPLACE, COUNTRY, PID, DEBUG_MODE, category=category_selected, level=2
                )
                category_selected = select_category_menu(choices=categories)
                category_glossary_tree.append(category_selected)

                # * LEVEL 3 and 4
                categories = bootstrap.category_glossary(
                    MARKETPLACE, COUNTRY, PID, DEBUG_MODE, category=category_selected, level=3,
                    parent_category=parent_category_selected
                )
                category_glossary_tree = category_glossary_tree + categories

                # * CONFIRM CRAWL PRODUCTS OF CATEGORIES SELECTED
                bullets = ['', ' >', '  *', '   -']
                for category in category_glossary_tree:
                    print(bullets[category.get('hierarchy') - 1], f"{category.get('name')}")

                confirm_message = 'Extraer productos del arbol de categorias?'

            elif MARKETPLACE == 'linio':
                # TODO INIT CATEGORY GLOSSARY SCRAPER ===============================================
                print(f"Crawl {MARKETPLACE}> init...")

        confirm = confirm_init_scraper_menu(confirm_message)
        if confirm.get('continue') is True:
            main(MARKETPLACE, COUNTRY, RECURSIVE, categories_path=categories_path, pid=PID,
                 category_id=category_selected.get('id'), marketplace_config=bootstrap.country_config)
            
        pass
    
    else:
        
        print("Scraper product page")
        products = [
            {
               'link': args.product_link,
            } 
        ]
        scrapperProducts(products, MARKETPLACE, COUNTRY, pid=PID)
