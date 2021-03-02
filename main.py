import argparse
import logging
import datetime
import csv
import re
import time
import random
import page_objects as pages
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError
from bootstrap import Bootstrap
from common import config
from bcolors import bcolors

logging.basicConfig(level=logging.INFO)
# logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
is_well_formed_link = re.compile(r'^https?://.+/.+$')
is_root_path = re.compile(r'^/.+$')

def _build_link(host, link):
    if is_well_formed_link.match(link):
        return link
    else:
        return f"{host}/{link}"


def _fetchProduct(marketplace, host, link):
    # logger.info(f'Start fetching product at {link}')

    product = None
    try:
        product = pages.HomePage(marketplace, _build_link(host, link))
        # print(product._html)
    except (HTTPError, MaxRetryError) as e:
        logger.warning('Error while fetching article!', exc_info=False)
        pass

    if product and not product._html.body:
        logger.warning('Invalid product. There is not body')
        return None

    return product._html


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


def _save_products(marketplace_uid, country_uid, products, overwrite=True):
    # print("_save_products", products)
    now = datetime.datetime.now().strftime('%Y_%m_%d')
    out_file_name = f'./output/{marketplace_uid}_{country_uid}_{now}_products.csv'
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
            csv_writer = writer(f)
            for product in products:
                csv_writer.writerow(list(product.values()))
        
    pass


def scrapperProducts(products, marketplace_uid, country_uid, overwrite=True):
    logger.info(f" \n\nPRODUCTOS({len(products)}):\n")

    for counter, product in enumerate(products, 1):
        logger.info(f"""
                    ======================================================================
                    {counter}. {product['name']}
                    ======================================================================
                    Precio: {product['price_simbol'] if product['price_simbol'] else ''} {product['price']}
                    Descuento: {product['price_discount']}
                    Más Vendido: {product['best_seller']}
                    Promocionado (Ads): {product['promotional']}
                    link: {product['link']}
                    """)

        # TODO Scrapper product
        # product_page = _fetchProduct(marketplace_uid,  product['link'])
        #
        # if product_page:
        #     logger.info("product detail scraper!")
        #     logger.info(product_page.title)
        #
        #     break;
        counter += 1

    _save_products(marketplace_uid, country_uid, products, overwrite=overwrite)
    return counter

    
def scraper_subcategories(marketplace_uid, url_categories, origin=None) -> object:
    return pages.CategoryPage(marketplace_uid, url_categories, origin=origin).getSubcategories()


def scrapper_categories(marketplace_uid, url_categories, origin=None) -> object:
    return pages.CategoryPage(marketplace_uid, url_categories, origin=origin).getCategories()


def select_country_menu(country_config) -> str:
    print("* Seleccione País:")
    return list(country_config.keys())[menu([value['name'] for key, value in list(country_config.items())])]


def select_category_menu(categories) -> object:
    print("* Seleccione Categoria:")
    return categories[menu([category['name'] for category in categories], "Categorias")]

    
def select_subcategory_menu(subcategories) -> object:
    print("* Seleccione Subcategoria:")
    return subcategories[menu([subcategory['name'] for subcategory in subcategories], "Subcategorias")]
    
    
def print_category_selected(category_selected):
    print(bcolors.OKCYAN,f"""
        Selecciono: {category_selected['name']}
        link: {category_selected['link']}
    """, bcolors.ENDC)
    # print(f"selecciono: ", category_selected)


def print_subcategory_selected(subcategory_selected):
    print(bcolors.OKCYAN,f"""
            Selecciono: {subcategory_selected['name']}
            link: {subcategory_selected['link']}
    """, bcolors.ENDC)
    # print(f"selecciono: ", subcategory_selected)



def scrapper_marketplace(marketplace_uid, country_uid,  link=None, overwrite=True, recursive=False, products_counter=0):
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
    productsPage = pages.ProductSectionPage(marketplace_uid, link, country_id=country_uid)    
    scrapperProducts(productsPage.produtcs, marketplace_uid, country_uid, overwrite=overwrite)
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
                scrapper_marketplace(marketplace_uid, country_uid,  link=paginator['next_page_url'], overwrite=False, recursive=recursive, products_counter=products_counter)
            elif menu(['Si','No']) == 0:
                scrapper_marketplace(marketplace_uid, country_uid,  link=paginator['next_page_url'], overwrite=False, products_counter=products_counter)
        elif paginator['next_page_url'] is None:
            print("Termina scrapper")
    else:
        print(bcolors.OKCYAN,f"""
            Total productos: {len(productsPage.produtcs)}
            Pagina 1 de (?)
        """, bcolors.ENDC)
        
            
def run(marketplace_uid: str, country_uid: str, origin: str, url_categories: str, recursive=False):
    print(f"run scraper {marketplace_uid} {country_uid}")
    scraper_link = None
    
    # TODO Scrapper Categorias
    macrocategories = scrapper_categories(marketplace_uid, url_categories, origin=origin)
    macrocategory_selected = select_category_menu(macrocategories)
    
    # TODO Scrapper Subcategorias
    if marketplace_uid == 'mercadolibre':
        categories = scraper_subcategories(marketplace_uid, macrocategory_selected['link'])
        category_selected = select_subcategory_menu(categories)
        scraper_link = category_selected['link']
    elif marketplace_uid == 'linio':    
        scraper_link = macrocategory_selected['link']
        
    # TODO Iniciar scrapper
    scrapper_marketplace(marketplace_uid, country_uid, link=scraper_link, recursive=recursive)


def main(marketplace: str, country: str, recursive: bool):
    """
    :param marketplace: name of marketplace
    :param country: code country in standard ISO_3166_COUNTRY_CODE
    """
    # TODO Init scraper
    # * Select country
    bootstrap = Bootstrap(marketplace)
    if country is None: 
        # * Select country by menu console
        bootstrap.country = select_country_menu(bootstrap.countries_config)
    print(bcolors.OKCYAN,f"Selecciono: {bootstrap.country_config['name']}", bcolors.ENDC)
    # * Recursive scraper mode
    bootstrap.recursive = recursive
    # * Run scraper
    run(
        marketplace, 
        bootstrap.country, 
        origin = bootstrap.country_config['origin'], # * Url marketplace Website
        url_categories = bootstrap.country_config['url_categories'], # * Url categories page
        recursive=recursive)


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    # TODO Select marketplace
    parser.add_argument('marketplace', help='The marketplace that you want to scraper', type=str, choices=Bootstrap.get_marketplace_avalible())
    # * Select country args --country {ISO_3166_COUNTRY_CODE} 
    parser.add_argument("--country", required=False, help=f"Country where the scrapper will run, avalible: co, mx")
    # * Recursive scrapper pages
    parser.add_argument("--recursive", required=False, help=f"Recursive scrapper pages: True or False")
    args = parser.parse_args()
    # print("args: ", args)
    main(args.marketplace, args.country, bool(args.recursive))
    pass
