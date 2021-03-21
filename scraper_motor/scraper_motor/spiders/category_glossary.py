import scrapy
import copy
import os
import ntpath
import logging
from ..common import config

logging.basicConfig(
    filename=f'.log/{ntpath.basename(os.path.basename(__file__)).replace(".py", "")}.log',
    format='%(levelname)s: %(message)s',
    level=logging.INFO
)

class CategoryGlossarySpider(scrapy.Spider):
    name = 'category_glossary'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
    # allowed_domains = ['https://www.mercadolibre.com.co']
    # start_urls = ['https://www.mercadolibre.com.co/categorias']
    custom_settings = {'FEED_URI': "./.output/category_glossary_%(time)s.csv",
                       'FEED_FORMAT': 'csv'}

    def start_requests(self):
        urls = [
            'https://www.mercadolibre.com.co/categorias',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def _next_category_page(self, href, meta, callback):
        return scrapy.Request(
            href,
            meta=meta,
            callback=callback
        )

    def parse(self, response):
        ## self._create_web_page_file("mercadolibre.html", response.body)
        self.logger.info("Visited %s", response.url)
        # TODO recorrer categorias de primer nivel
        level = 1
        for index, categories_container in enumerate(response.css(config()['queries'][f'categories_container_level_{level}'])):
            href = categories_container.css(config()['queries'][f'category_href_level_{level}']).attrib['href']
            id = self._extract_category_ids_from_href(href).get('c_category_id')
            yield self._extract_category_data(id, category_container=categories_container, href=href, index=index, level=1)
            # ?link de subcategorias
            yield self._next_category_page(
                href,
                {'parent_id': id, "level": 2},
                self.parse_category_page
            )
        pass

    def parse_category_page(self, response):
        self.logger.info("Visited %s", response.url)
        level= response.meta.get('level')
        # TODO recorrer categorias de segundo nivel
        for index, categories_container in enumerate(response.css(config()['queries'][f'categories_container_level_{level}'])):
            href = categories_container.css(config()['queries'][f'category_href_level_{level}']).attrib['href']
            id = self._extract_category_ids_from_href("".join((href).split("#")[1:2])).get('c_category_id')
            yield self._extract_category_data(id, category_container=categories_container, href=href, index=index, level=level, parent=response.meta.get('parent_id'), hierarchy=2)
            # TODO recorrer categorias de tercer nivel
            next_level= 3
            next_parent_id = copy.copy(id)
            for count, category_container in enumerate(categories_container.css(config()['queries'][f'categories_container_level_{next_level}'])):
                href = category_container.css(config()['queries'][f'category_href_level_{next_level}']).attrib['href']
                id = self._extract_category_ids_from_href("".join((href).split("#")[1:2])).get('c_category_id')
                yield self._extract_category_data(id, category_container=category_container, href=href, index=count, level=next_level, parent=next_parent_id, hierarchy=3)
                yield self._next_category_page(
                    href,
                    {'parent_id': id, "level": 4},
                    self.parse_products_category_page
                )
                
    def parse_products_category_page(self, response):
        self.logger.info("Visited %s", response.url)
        level = 4
        print("-->",len(response.css(config()['queries'][f'categories_container_level_{level}'])))
        
        for index, category_container in enumerate(response.css(config()['queries'][f'categories_container_level_{level}'])):
            href = category_container.css(config()['queries'][f'category_href_level_{level}']).attrib['href']
            id = "LAST_ID"
            yield self._extract_category_data(id, category_container=category_container, href=href, index=index, level=level, hierarchy=4, parent=response.meta.get('parent_id'))
        
    def _extract_category_data(self, id, category_container=None,  href:str =None, index:int =0, level:int=None, parent=None, hierarchy:int =1):
        
        if config()['queries'][f'category_subcategories_level_{level}']:
            subcategories = len(category_container.css(config()['queries'][f'category_subcategories_level_{level}']))
        else:
            subcategories = 0
            
        return self._render_category_of_catalog(
            id=id,
            # uid=self._extract_category_ids_from_href(href).get('c_uid'),
            index=index,
            name=category_container.css(config()['queries'][f'category_name_level_{level}']).get(),
            parent=parent,
            href=href,
            hierarchy=hierarchy,
            subcategories=subcategories
        )

    def _render_category_of_catalog(self, id=None, uid=None, name=None, parent=None, href=None, hierarchy=None,
                                    subcategories=0, index=0):
        # print(f"id={category_id}")
        # ? some validation
        # ? ...
        # * prints
        self._print_category_name(name, hierarchy)
        return {
            'id': id,
            'uid': uid,
            'parent': parent,
            'name': name,
            'href': href,
            'index': index,
            'hierarchy': hierarchy,
            'subcategories': subcategories
        }

    def _extract_category_ids_from_href(self, href, split_separator='&', start=None, stop=None):
        """Return dict with category ids

        Args:
            href (str): link category

        Returns:
            [type]: {'c_category_id': str, 'c_uid': str}
        """
        # !CAMBIAR POR REGEX
        if start is None and stop is None:
            return {_.split("=")[0].replace("CATEGORY_ID", "c_category_id"): _.split("=")[1] for _ in
                    href.split(split_separator)}
        return {_.split("=")[0].replace("CATEGORY_ID", "c_category_id"): _.split("=")[1] for _ in
                href.split(split_separator)[start:stop]}

    def _print_category_name(self, name, hierarchy=None):
        print("-" * hierarchy, f" {name}")

    def _create_web_page_file(self, filename, body):
        with open(filename, 'wb') as f:
            f.write(body)
        self.log(f'Saved file {filename}')
        pass

# ? Aca debe navergar categoria por categoria
# NEXT_PAGE_SELECTOR = '.ui-pagination-active + a::attr(href)'
# next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
# if next_page:
#     yield scrapy.Request(
#         response.urljoin(next_page),
#         callback=self.parse
#     )