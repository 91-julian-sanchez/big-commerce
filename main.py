import argparse
import logging
import page_objects as pages
from common import config
logging.basicConfig(level=logging.INFO)
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

    # subcategory = input("Escriba subcategoria que quiere buscar en deportes: ")
    # categoryPage = pages.CategoryPage(marketplace_uid, host, subcategory=subcategory)
    #
    # counter = 1
    # for link in categoryPage.subcategories_links:
    #     logger.info(f"{counter}. {link}")
    #     counter += 1

    productsPage = pages.ProductPage(marketplace_uid, host, None)
    productsPage.product_body
    # print(productsPage.product_body)

    # for product_body in productsPage.product_body:
    #     print("=="*40,"\n\n",product_body)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    marketplace_choices = list(config()['marketplace'].keys())
    # print("marketplace_choices: ", marketplace_choices)
    parser.add_argument('marketplace', help='The marketplace that you want to scrape', type=str, choices=marketplace_choices)

    args = parser.parse_args()
    # print("args: ", args)
    marketplaceScrapper(args.marketplace)
    pass
