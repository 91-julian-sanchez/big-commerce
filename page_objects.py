import bs4
import requests
from common import config
import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class HomePage:

    def __init__(self, marketplace_id, url, subcategory=None):
        self._config = config()['marketplace'][marketplace_id]
        self._queries = self._config['queries']
        self._html = None
        self.subcategory = subcategory

        if self.subcategory is not None:
            self._visit(f"{url}/{self.subcategory}/")
        else:
            self._visit(url)
 
    def _select(self, query_string):
        return self._html.select(query_string)

    def _visit(self, url):
        response = requests.get(url)
        response.encoding = 'utf-8'
        response.raise_for_status()

        # print("\n\n","=="*40,f"_visit(self, {url})", response.text)
        self._html = bs4.BeautifulSoup(response.text, 'html.parser')


class CategoryPage(HomePage):
    
    def __init__(self, marketplace_id, url, subcategory=None):
        print("CategoryPage.__init__(self)")
        self._config = config()['marketplace'][marketplace_id]
        self._queries = self._config['queries']
        self._html = None
        self.subcategory = subcategory

        if self.subcategory is not None:
            self._visit(f"{url}/{self.subcategory}/")
        else:
            self._visit(url)
    
    @property
    def subcategory(self):
        return self._subcategory

    @subcategory.setter
    def subcategory(self, subcategory):
        if subcategory is not None:
            self._subcategory = subcategory.strip()

    @property
    def subcategories_links(self):
        link_list = []
        categorypage_subcategories_links = self._select(self._queries['categorypage_subcategories_links'])

        for link in self._select(self._queries['categorypage_subcategories_links']):
            print(link)
            if link and link.has_attr('href'):
                link_list.append(link)

        if self._config['id'] == 'linio':
            return set(f"{link.span.text} -> {self._config['origin']}{link['href']}" for link in link_list)
        elif self._config['id'] == 'mercadolibre':
            return set(f"{link.span.text} -> {link['href']}" for link in link_list)
        else:
            return []


class ProductPage(HomePage):

    def __init__(self, marketplace_id, url, subcategory=None):
        super().__init__(marketplace_id, url, subcategory)

    @property
    def product_body(self):

        layout_products = self._select(self._queries['list_products'])

        if len(layout_products) == 1:
            layout_products = layout_products[0]

            for layout_product in layout_products.select(".ui-search-layout__item"):
                # print(layout_product.select('.ui-search-item__title')[0])
                name = layout_product.find("h2", class_="ui-search-item__title").text
                print(name)
                # Precio
                price_symbol = layout_product.find("span", class_="price-tag-symbol").text
                price = layout_product.find("span", class_="price-tag-fraction").text
                print(f"{price_symbol} {price}")

                price_discount = layout_product.find("span", class_="ui-search-price__discount")
                if price_discount is not None:
                    price_discount = price_discount.text
                    print(f"Discount: {price_discount}")
                else:
                    print(f"Discount: 0%")


                # Tags
                best_seller = layout_product.select(".ui-search-item__highlight-label--best_seller")
                if len(best_seller) == 1:
                    best_seller = True
                else:
                    best_seller = False

                print(f"Best seller: {best_seller}")

                promotional = layout_product.select(".ui-search-item__ad-label--blue")
                logging.warning(promotional)

                if len(promotional) == 1:
                    promotional = True
                else:
                    promotional = False

                print(f"Promotional: {promotional}")

                print("\n")
        else:
            raise Exception("Multiple products layout")

        # print(layout_products)
        # print(len(layout_products))
        raise Exception("kill")
        return self._select(self._queries['product'])
