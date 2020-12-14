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


def scrapperProducts(products, marketplace_uid, host, country_uid):
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
        # product_page = _fetchProduct(marketplace_uid, host, product['link'])
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


def marketplaceScrapper(marketplace_uid, country_uid, category_id=None, link=None):
    """
    Scraper start function
    :param link:
    :param category_id:
    :param marketplace_uid: marketplace id for marketplace scraper
    :param country_uid: country id for marketplace scraper
    """
    host = None
    if marketplace_uid == 'mercadolibre':
        if category_id is not None:
            host = (config()['marketplace'][marketplace_uid]['country'][country_uid]['url']).replace("{CATEGORY_ID}", category_id)
    else:
        host = (config()['marketplace'][marketplace_uid]['country'][country_uid]['url'])

    if marketplace_uid == 'linio':

        logger.info(f"Beginning scraper for {marketplace_uid} in {country_uid}: {host}.")
        subcategory = input(f"Escriba subcategoría que quiere buscar en '{category_id}': ")

        try:
            categoryPage = pages.CategorySectionPage(marketplace_uid, host, subcategory=subcategory, country_id=country_uid)

            counter = 1
            subcategories_links = categoryPage.subcategories_links
            logger.info(f"\n\nSUBCATEGORIAS({len(subcategories_links)}):\n")

            for link in subcategories_links:
                logger.info(f"{counter}. {link}")
                counter += 1

            productsPage = pages.ProductSectionPage(marketplace_uid, host, subcategory=subcategory, country_id=country_uid)
            scrapperProducts(productsPage.produtcs, marketplace_uid, host, country_uid)

        except HTTPError as e:
            print(f"La subcategoría '{subcategory}' no existe.")
            pass
        except Exception as e:
            print(str(e))
            pass

    elif "mercadolibre":
        productsPage = pages.ProductSectionPage(marketplace_uid, link, country_id=country_uid)
        print(bcolors.OKCYAN,f"""
              Inicia scrapper...
              """, bcolors.ENDC)
        scrapperProducts(productsPage.produtcs, marketplace_uid, host, country_uid )
        print(bcolors.OKCYAN,f"""
              total productos: {len(productsPage.produtcs)} 
              Pagina 1 de X""", bcolors.ENDC)


def run(marketplace_uid, country_uid):
    # print(f"run {marketplace_uid} {country_uid}")
    if marketplace_uid == 'mercadolibre':

        # TODO Scrapper Categorias
        url_categories = config()['marketplace'][marketplace_uid]['country'][country_uid]['url_categories']
        categoryPage = pages.CategoryPage(marketplace_uid, url_categories)
        categories = categoryPage.getCategories()
        print("* Seleccione Categoria:")
        category_selected = categories[menu([category['name'] for category in categories], "Categorias")]
        print(bcolors.OKCYAN,f"""
              Selecciono: {category_selected['name']}
              link: {category_selected['link']}
              """, bcolors.ENDC)
        # print(f"selecciono: ", category_selected)

        # TODO Scrapper Subcategorias
        subcategoryPage = pages.CategoryPage(marketplace_uid, category_selected['link'])
        subcategories = subcategoryPage.getSubcategories()
        print("* Seleccione Subcategoria:")
        subcategory_selected = subcategories[menu([subcategory['name'] for subcategory in subcategories], "Subcategorias")]
        print(bcolors.OKCYAN,f"""
              Selecciono: {subcategory_selected['name']}
              link: {subcategory_selected['link']}
              """, bcolors.ENDC)
        # print(f"selecciono: ", subcategory_selected)

        # TODO Iniciar scrapper
        marketplaceScrapper(args.marketplace, country_selected, link=subcategory_selected['link'])

    else:
        # TODO Iniciar scrapper
        marketplaceScrapper(args.marketplace, country_selected)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    # TODO Select marketplace
    marketplace_choices = list(config()['marketplace'].keys())
    parser.add_argument('marketplace', help='The marketplace that you want to scraper', type=str, choices=marketplace_choices)
    args = parser.parse_args()
    # print("args: ", args)

    # TODO Select country
    country_config = config()['marketplace'][args.marketplace]['country']
    country_choices = list(country_config.items())
    print("* Seleccione País:")
    country_selected = list(country_config.keys())[menu([value['name'] for key, value in country_choices])]
    print(bcolors.OKCYAN,f"Selecciono: {country_selected}", bcolors.ENDC)
    run(args.marketplace, country_selected)

    pass
