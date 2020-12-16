import argparse
import logging
import datetime
import csv
import re
import page_objects as pages
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError
from common import config
from bcolors import bcolors

logging.basicConfig(level=logging.INFO)
# logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
is_well_formed_link = re.compile(r'^https?://.+/.+$')
is_root_path = re.compile(r'^/.+$')


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

def _save_products(marketplace_uid, country_uid, products):
    # print("_save_products", products)
    now = datetime.datetime.now().strftime('%Y_%m_%d')
    out_file_name = f'./output/{marketplace_uid}_{country_uid}_{now}_products.csv'
    csv_headers = list(products[0].keys())

    with open(out_file_name, mode='w+') as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)

        for product in products:
            writer.writerow(list(product.values()))
    pass

def scrapperProducts(products, marketplace_uid, country_uid):
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

    _save_products(marketplace_uid, country_uid, products)


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


def marketplaceScrapper(marketplace_uid, country_uid,  link=None):
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
    
    scrapperProducts(productsPage.produtcs, marketplace_uid, country_uid )
    print(bcolors.OKCYAN,f"""
        total productos: {len(productsPage.produtcs)}
    """, bcolors.ENDC)
    
    # TODO BROWSE PAGES
    if marketplace_uid == 'mercadolibre':
        paginationSectionPage = pages.PaginationSectionPage(marketplace_uid, link, country_id=country_uid)
        paginator = paginationSectionPage.getPaginator()
        print(bcolors.OKCYAN,f"""
            Pagina {paginator['current_page']} de {'primeras' if paginator['has_more_pages'] else ''} {paginator['count']}
        """, bcolors.ENDC)
            
        # * NEXT PAGE
        if paginator['current_page'] is not None:
            print("* Siguiente pagina?")
            if menu(['Si','No']) == 0:
                marketplaceScrapper(marketplace_uid, country_uid,  link=paginator['next_page_url'])
    else:
        print(bcolors.OKCYAN,f"""
            Pagina 1 de (?)
        """, bcolors.ENDC)
        
    
def scraperSubcategories(marketplace_uid, url_categories, origin=None):
    return pages.CategoryPage(marketplace_uid, url_categories, origin=origin).getSubcategories()


def scrapperCategories(marketplace_uid, url_categories, origin=None):
    return pages.CategoryPage(marketplace_uid, url_categories, origin=origin).getCategories()


def run(marketplace_uid, country_uid):
    # print(f"run {marketplace_uid} {country_uid}")
    scraper_link = None
    url_categories = config()['marketplace'][marketplace_uid]['country'][country_uid]['url_categories']
    
    # TODO Scrapper Categorias
    categories = scrapperCategories(marketplace_uid, url_categories, origin=config()['marketplace'][marketplace_uid]['country'][country_uid]['origin'])
    # * Menu categories
    print("* Seleccione Categoria:")
    category_selected = categories[menu([category['name'] for category in categories], "Categorias")]
    print(bcolors.OKCYAN,f"""
        Selecciono: {category_selected['name']}
        link: {category_selected['link']}
    """, bcolors.ENDC)
    # print(f"selecciono: ", category_selected)
    
    if marketplace_uid == 'mercadolibre':

        # TODO Scrapper Subcategorias
        subcategories = scraperSubcategories(marketplace_uid, category_selected['link'])
        # * Menu Subcategories
        print("* Seleccione Subcategoria:")
        subcategory_selected = subcategories[menu([subcategory['name'] for subcategory in subcategories], "Subcategorias")]
        print(bcolors.OKCYAN,f"""
            Selecciono: {subcategory_selected['name']}
            link: {subcategory_selected['link']}
        """, bcolors.ENDC)
        # print(f"selecciono: ", subcategory_selected)
        scraper_link = subcategory_selected['link']

    elif marketplace_uid == 'linio':
        
        scraper_link = category_selected['link']
        
    # TODO Iniciar scrapper    
    marketplaceScrapper(args.marketplace, country_selected, link=scraper_link)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    # TODO Select marketplace
    marketplace_choices = list(config()['marketplace'].keys())
    parser.add_argument('marketplace', help='The marketplace that you want to scraper', type=str, choices=marketplace_choices)
    parser.add_argument("--country", required=False, help=f"Country where the scrapper will run")
    args = parser.parse_args()
    # print("args: ", args)

    # TODO Select country
    country_selected = None
    country_config = config()['marketplace'][args.marketplace]['country']
    
    if args.country is None: 
        # * Select country by menu in console
        country_choices = list(country_config.items())
        print("* Seleccione País:")
        country_selected = list(country_config.keys())[menu([value['name'] for key, value in country_choices])]  
    else:
        # * Select country args --country {ISO_3166_COUNTRY_CODE}
        country_selected = args.country
        
    print(bcolors.OKCYAN,f"Selecciono: {country_config[country_selected]['name']}", bcolors.ENDC)
    run(args.marketplace, country_selected)
        

    pass
