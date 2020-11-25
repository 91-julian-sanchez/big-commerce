import bs4
import requests
from common import config


class CategoryPage:

    def __init__(self, marketplace_id, url, subcategory=None):
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
    
    def _select(self, query_string):
        return self._html.select(query_string)

    def _visit(self, url):
        response = requests.get(url)
        response.encoding = 'utf-8'
        response.raise_for_status()

        # print("\n\n","=="*40,f"_visit(self, {url})", response.text)
        self._html = bs4.BeautifulSoup(response.text, 'html.parser')


