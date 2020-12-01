import bs4
import requests
from common import config
import logging
# logging.basicConfig(level=logging.INFO)
# logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


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

    def _find(self, html, tag, class_=None):
        return html.find(tag, class_=class_)

    def _findText(self, html, tag, class_=None, trim=None):
        found = self._find(html, tag, class_=class_)
        if found is not None:
            if trim is None or trim is True:
                return found.text.strip()

            return found.text
        else:
            return None

    def _visit(self, url):
        response = requests.get(url)
        response.encoding = 'utf-8'
        response.raise_for_status()

        # print("\n\n","=="*40,f"_visit(self, {url})", response.text)
        self._html = bs4.BeautifulSoup(response.text, 'html.parser')


class CategoryPage(HomePage):

    _country_id = None
    _marketplace_id = None

    def __init__(self, marketplace_id, url, subcategory=None, country_id=None):
        super().__init__(marketplace_id, url, subcategory)
        self._marketplace_id = marketplace_id
        self._country_id = country_id

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

        for link in self._select(self._queries['categorypage_subcategories_links']):
            # print(link)
            if link and link.has_attr('href'):
                link_list.append(link)
        # print(link_list)

        if self._config['id'] == 'linio':
            return set(
                f"{link.span.text} -> {config()['marketplace'][self._marketplace_id]['country'][self._country_id]['origin']}{link['href']}" for link in link_list
            )
        elif self._config['id'] == 'mercadolibre':
            return set(f"{link.span.text} -> {link['href']}" for link in link_list)
        else:
            return []


class ProductPage(HomePage):

    def __init__(self, marketplace_id, url, subcategory=None):
        super().__init__(marketplace_id, url, subcategory)

    @property
    def produtcs(self):

        layout_products = self._select(self._queries['list_products'])
        products_list = []

        if len(layout_products) == 1:
            layout_products = layout_products[0]

            for layout_product in layout_products.find_all(self._queries['product_container_tag'],
                                                           self._queries['product_container']):

                # TODO Name
                name = self._findText(layout_product, self._queries['product_title_tag'],
                                      class_=self._queries['product_title'])
                # print(name)

                # TODO Precio
                price_symbol = self._findText(layout_product, "span", class_=self._queries['product_price_symbol'])
                price = self._findText(layout_product, "span", class_=self._queries['product_price'])
                # print(f"Precio: {price_symbol} {price}")

                # TODO Descuento
                price_discount = self._findText(layout_product, "span", class_=self._queries['product_price_discount'])
                # print(f"Descuento: {price_discount}")

                # TODO Best seller
                best_seller = self._findText(layout_product, "div", class_=self._queries['product_best_seller'])
                # logging.warning(best_seller)

                if best_seller is not None:
                    best_seller = True
                else:
                    best_seller = False
                # print(f"Más Vendido: {best_seller}")

                # TODO Promotional (Ads)
                promotional = layout_product.select(self._queries['product_promotional'])

                if len(promotional) == 1:
                    promotional = True
                else:
                    promotional = False

                # print(f"Promotional: {promotional}")

                # TODO append Dic products
                products_list.append({
                    'name': name,
                    'price_simbol': price_symbol,
                    'price': price,
                    'price_discount': price_discount,
                    'best_seller': best_seller,
                    'promotional': promotional
                })
        else:
            raise Exception("Multiple products layout")

        return products_list
