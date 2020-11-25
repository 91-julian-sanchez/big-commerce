import argparse
import logging
from common import config
import requests
import bs4
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
host = None


def requestLinio(path):
    response = requests.get(path)
    response.encoding = 'utf-8'
    # print(response.text)
    return response


def requestMercadolibre(path):
    response = requests.get(path)
    response.encoding = 'utf-8'
    # print(response.text)
    return response


def requestCategory(category, marketplace_uid):

    if marketplace_uid == 'mercadolibre':
        return requestMercadolibre(f"{host}/{category}/")
    elif marketplace_uid == 'linio':
        return requestLinio(f"{host}/{category}/")


def marketplaceScrapper(marketplace_uid):

    global host
    host = config()['marketplace'][marketplace_uid]['url']
    logger.info(f"Beginning scraper for {marketplace_uid}: {host}.")

    category = input("Escriba subcategoria que quiere buscar en deportes: ")
    response = requestCategory(category, marketplace_uid)
    soup = bs4.BeautifulSoup(response.text, 'html.parser', )

    if marketplace_uid == 'mercadolibre':

        categories_link = soup.select('.ui-search-filter-container > a')

        counter = 1
        for category_link in categories_link:
            # print("\n\n", "==" * 40, category_link)
            class_ui_search_filter_name = category_link.select('.ui-search-filter-name')

            if len(class_ui_search_filter_name) > 0:
                logger.info(f"{counter}. {class_ui_search_filter_name[0].text} -> {category_link['href']}")
                counter += 1

    elif marketplace_uid == 'linio':

        categories_link = soup.select('.catalogue-list > ul > li > a')

        counter = 1
        for category_link in categories_link:
            # print("\n\n","=="*40,category_link)

            logger.info(f"{counter}. {category_link.span.text} -> https://www.linio.com.co{category_link['href']}")
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
