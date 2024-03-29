import bs4
import requests
from common import config
import logging
# logging.basicConfig(level=logging.INFO)
# logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class HomePage:

    def __init__(self, marketplace_id, url, origin=None):
        self._config = config()['marketplace'][marketplace_id]
        self._queries = self._config['queries']
        self._html = None
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
        self._html.encode("utf-8")


class CategorySectionPage(HomePage):

    _country_id = None
    _marketplace_id = None
    _origin = None

    def __init__(self, marketplace_id, url, country_id=None):
        super().__init__(marketplace_id, url)
        self._marketplace_id = marketplace_id
        self._country_id = country_id
        self._origin = config()['marketplace'][self._marketplace_id]['country'][self._country_id]['origin']

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
                f"{link.span.text} -> {self._origin}{link['href']}" for link in link_list
            )
        elif self._config['id'] == 'mercadolibre':
            return set(f"{link.span.text} -> {link['href']}" for link in link_list)
        else:
            return []


class ProductSectionPage(HomePage):

    _country_id = None
    _marketplace_id = None
    _origin = None

    def __init__(self, marketplace_id, url, country_id=None, category_id=None):
        super().__init__(marketplace_id, url)
        self._marketplace_id = marketplace_id
        self._country_id = country_id
        self.category_id = category_id
        self._origin = config()['marketplace'][self._marketplace_id]['country'][self._country_id]['origin']

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

                # TODO url
                link = layout_product.select(self._queries['product_url'])

                if link is not None:
                    if self._marketplace_id == 'linio':
                        link = self._origin+link[0]['href']
                    else:
                        link = link[0]['href']
                else:
                    link = None
                # print(url)

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
                    'link': link,
                    'price_simbol': price_symbol,
                    'price': price,
                    'price_discount': price_discount,
                    'best_seller': best_seller,
                    'promotional': promotional,
                    'category_id': self.category_id,
                    #Only with scraper page product
                    'number_sales': None,
                    'seller': None,
                    'delivery': None,
                    'rating': None,
                })
        else:
            raise Exception("Multiple products layout")

        return products_list

class PaginationSectionPage(HomePage):
    
    def __init__(self, marketplace_id, url, country_id=None):
        # print("PaginationSectionPage(HomePage)::__init__", url)
        super().__init__(marketplace_id, url)
        
    def getPaginator(self):
        pagination_container = self._select(self._queries['section_pagination'])
        current_page = 0
        next_page = None
        has_more_pages = False
        zero_is_first_page = False
        
        for index, page in enumerate(pagination_container):
            
            if  'andes-pagination__button--current' in page['class']:
                current_page = index
                if index + 1 < len(pagination_container):
                    next_page = pagination_container[index + 1]
                
            if  'andes-pagination__button--next' in page['class']:
                has_more_pages = True
            
        if current_page == 0 :
            current_page = 0 if zero_is_first_page is True else 1
            
        paginator = {
            'count': len(pagination_container)-1,
            'current_page': current_page,
            'next_page_url': next_page.a['href'] if next_page is not None else None,
            'has_more_pages': has_more_pages
        }
        # print(paginator)
        return paginator
        
class CategoryPage(HomePage):

    _marketplace_id = None
    _origin = None

    def __init__(self, marketplace_id, url, origin=None):
        # print("CategoryPage(HomePage)::__init__", url)
        super().__init__(marketplace_id, url)
        self._marketplace_id = marketplace_id
        self._origin = origin
        pass

    def getCategories(self):
        categories_container = self._select(self._queries['page_categories'])
        # print(categories_container)
  
        categories = []
        for category_container in categories_container:
            # print("category_container:", category_container)
            # self._find('a')
            if category_container.a.has_attr('href'):

                link_split = (category_container.a['href'].split("/"))
                category = dict()
                
                if self._marketplace_id == 'mercadolibre' and len(link_split) >= 5:

                    link_split = link_split[4].split("#")

                    if len(link_split) >= 2:
                        category['id'] = link_split[0]
                        category['name'] = category_container.text
                        category['link'] = category_container.a['href']
                        
                elif self._marketplace_id == 'linio' and len(link_split) >= 3:
                    
                        category['id'] = link_split[2]
                        category['name'] = category_container.a.find("span", "label-text").text
                        category['link'] = f"{self._origin}{category_container.a['href']}"

            # print(category)
            categories.append(category)

        return categories

    def getSubcategories(self):
        # print("getSubcategories(self): ", self._html)
        subcategories_container = self._select(self._queries['page_subcategories'])
        subcategories = []
        for index, subcategory in enumerate(subcategories_container):

            try:
                subcategory_link = subcategory['href']
                subcategory = {
                    'name': subcategory.find("h3", "category-list__permanlink-custom").text,
                    'link': subcategory_link,
                    'id': (subcategory_link.split("/"))[3]
                }
                subcategories.append(subcategory)
            except Exception as e:
                print("No se pudo...")

        return subcategories

class ProductPage(HomePage):

    _country_id = None
    _marketplace_id = None
    _origin = None

    def __init__(self, marketplace_id, url, country_id=None):
        super().__init__(marketplace_id, url)
        self._marketplace_id = marketplace_id
        self._country_id = country_id
        
    def get_product(self):
       
        # print(  )
        seller = None
        delivery = None
        rating = None
        
        try:
            seller_container = self._select('div.ui-pdp-seller__header__info-container')[0]
            seller = seller_container.find('span','ui-pdp-color--BLUE').text
        except Exception as e:
            print(e)
        
        # try:
        #     summary = self._select('div.ui-pdp-container__row ui-pdp-container__row--pick-up-summary')[0]
        #     delivery = summary.find('h2','ui-pdp-color--GREEN ui-pdp-media__title').text  
        #     if delivery is None:
        #         summary = self._select('ui-pdp-container__row ui-pdp-container__row--shipping-summary')[0]
        #         delivery = summary.find('span','price-tag-fraction').text
        # except Exception as e:
        #     print(e)
            
        try:
            reviews__rating = self._select('div.ui-pdp-reviews__rating')[0]
            rating = reviews__rating.find('h2','ui-pdp-reviews__rating__summary__average').text  
        except Exception as e:
            print(e)
        
        # raise Exception('kill')  
        return  {
            'number_sales': self._findText(self._html, "span", "ui-pdp-subtitle"),
            'seller': seller,
            'delivery': delivery,
            'rating': rating,
        }