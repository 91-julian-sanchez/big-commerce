import argparse
import logging
import page_objects as pages
from common import config
logging.basicConfig(level=logging.INFO)
# logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
host = None


def marketplaceScrapper(marketplace_uid):
    """
    Scrappy start function
    :param marketplace_uid: marketplace id for scrappy
    """
    global host
    host = config()['marketplace'][marketplace_uid]['url']
    logger.info(f"Beginning scraper for {marketplace_uid}: {host}.")

    subcategory = input("Escriba subcategoria que quiere buscar en deportes: ")

    print("\n\nSUBCATEGORIAS:\n")
    categoryPage = pages.CategoryPage(marketplace_uid, host, subcategory=subcategory)

    counter = 1
    subcategories_links = categoryPage.subcategories_links

    for link in subcategories_links:
        logger.info(f"{counter}. {link}")
        counter += 1

    print(" \n\nPRODUCTOS:\n")
    productsPage = pages.ProductPage(marketplace_uid, host, subcategory=subcategory)
    products = productsPage.produtcs
    counter = 1
    for product in products:
        logger.info(f"""
        ======================================================================
        {counter}. {product['name']} 
        ======================================================================
        Precio: {product['price_simbol'] if product['price_simbol'] else ''} {product['price']} 
        Descuento: {product['price_discount']}
        Más Vendido: {product['best_seller']}
        Promocionado (Ads): {product['promotional']}
        """)
        counter += 1


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    marketplace_choices = list(config()['marketplace'].keys())
    # print("marketplace_choices: ", marketplace_choices)
    parser.add_argument('marketplace', help='The marketplace that you want to scrape', type=str, choices=marketplace_choices)

    args = parser.parse_args()
    # print("args: ", args)
    marketplaceScrapper(args.marketplace)
    pass
