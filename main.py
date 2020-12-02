import argparse
import logging
import datetime
import csv
import re
import page_objects as pages
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError
from common import config

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


def marketplaceScrapper(marketplace_uid, country_uid):
    """
    Scraper start function
    :param marketplace_uid: marketplace id for marketplace scraper
    :param country_uid: country id for marketplace scraper
    """
    host = config()['marketplace'][marketplace_uid]['country'][country_uid]['url']
    logger.info(f"Beginning scraper for {marketplace_uid} in {country_uid}: {host}.")

    subcategory = input("Escriba subcategoría que quiere buscar en deportes: ")

    try:
        categoryPage = pages.CategorySectionPage(marketplace_uid, host, subcategory=subcategory, country_id=country_uid)

        counter = 1
        subcategories_links = categoryPage.subcategories_links
        logger.info(f"\n\nSUBCATEGORIAS({len(subcategories_links)}):\n")

        for link in subcategories_links:
            logger.info(f"{counter}. {link}")
            counter += 1

        productsPage = pages.ProductSectionPage(marketplace_uid, host, subcategory=subcategory, country_id=country_uid)
        products = productsPage.produtcs

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

            product_page = _fetchProduct(marketplace_uid, host, product['link'])

            if product_page:
                logger.info("product detail scraper!")
                logger.info(product_page.title)
            #
            #     break;
            counter += 1

        _save_products(marketplace_uid, country_uid, products)

    except HTTPError as e:
        print(f"La subcategoría '{subcategory}' no existe.")
        pass
    except Exception as e:
        print(str(e))
        pass


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    # TODO Select marketplace
    marketplace_choices = list(config()['marketplace'].keys())
    parser.add_argument('marketplace', help='The marketplace that you want to scrape', type=str, choices=marketplace_choices)
    args = parser.parse_args()
    # print("args: ", args)

    # TODO Select country
    country_choices = list(config()['marketplace'][args.marketplace]['country'].items())
    print("Seleccione país:")

    for index, (key, value) in enumerate(country_choices):
        print(f"{index+1}. {value['name']}")
        pass

    country_selected = None

    while country_selected is None:
        country = int(input("Ingrese opción: ")) - 1

        if -1 < country < len(config()['marketplace'][args.marketplace]['country'].keys()):
            country_selected = list(config()['marketplace'][args.marketplace]['country'].keys())[country]

            # TODO Iniciar scrapper
            marketplaceScrapper(args.marketplace, country_selected)
        else:
            print("Error: Seleccione una opción valida.")

    pass
