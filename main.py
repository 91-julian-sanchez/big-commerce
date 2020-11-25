import argparse
import logging
import category_page_objects as pages
from common import config
import requests
import bs4
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
host = None


def requestMercadolibre(path):
    """
    function that makes request to Mercado libre
    :param path:
    :return: request response
    """
    response = requests.get(path)
    response.encoding = 'utf-8'
    # print(response.text)
    return response


def requestCategory(category, marketplace_uid):
    """
    function to handle marketplace requests
    :param category:
    :param marketplace_uid:
    :return:
    """
    if marketplace_uid == 'mercadolibre':
        return requestMercadolibre(f"{host}/{category}/")


def marketplaceScrapper(marketplace_uid):
    """
    Scrappy start function
    :param marketplace_uid: marketplace id for scrappy
    """
    global host
    host = config()['marketplace'][marketplace_uid]['url']
    logger.info(f"Beginning scraper for {marketplace_uid}: {host}.")

    subcategory = input("Escriba subcategoria que quiere buscar en deportes: ")
    categoryPage = pages.CategoryPage(marketplace_uid, host, subcategory=subcategory)

    counter = 1
    for link in categoryPage.subcategories_links:
        logger.info(f"{counter}. {link}")
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
