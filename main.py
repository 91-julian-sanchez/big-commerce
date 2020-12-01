import argparse
import logging
import page_objects as pages
from common import config
logging.basicConfig(level=logging.INFO)
# logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def marketplaceScrapper(marketplace_uid,country_uid):
    """
    Scrappy start function
    :param marketplace_uid: marketplace id for scrappy
    """
    host = config()['marketplace'][marketplace_uid]['country'][country_uid]['url']
    logger.info(f"Beginning scraper for {marketplace_uid}: {host}.")

    subcategory = input("Escriba subcategoria que quiere buscar en deportes: ")

    categoryPage = pages.CategoryPage(marketplace_uid, host, subcategory=subcategory, country_id=country_uid)

    counter = 1
    subcategories_links = categoryPage.subcategories_links
    print(f"\n\nSUBCATEGORIAS({len(subcategories_links)}):\n")

    for link in subcategories_links:
        logger.info(f"{counter}. {link}")
        counter += 1

    productsPage = pages.ProductPage(marketplace_uid, host, subcategory=subcategory, country_id=country_uid)
    products = productsPage.produtcs

    print(f" \n\nPRODUCTOS({len(products)}):\n")
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
        link: {product['link']}
        """)
        counter += 1


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    marketplace_choices = list(config()['marketplace'].keys())
    parser.add_argument('marketplace', help='The marketplace that you want to scrape', type=str, choices=marketplace_choices)

    args = parser.parse_args()
    # print("args: ", args)
    
    country_choices = list(config()['marketplace'][args.marketplace]['country'].items())
    
    print("Seleccione pais:")
    index = 1
    for key, value in country_choices:
        print(f"{index}. {value['name']}")
        index+= 1
        pass
    
    country = int(input("Ingrese opcion: ")) - 1
    
    if -1 < country < len(config()['marketplace'][args.marketplace]['country'].keys()):
        country_selected = list(config()['marketplace'][args.marketplace]['country'].keys())[country]
        marketplaceScrapper(args.marketplace, country_selected)
    else:
        print("Seleccione una opcion valida")
        
    pass
