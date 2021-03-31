import scrapy
import copy
import os
import ntpath
import logging
from ..common import config
from ..items import CategoryItem

logging.basicConfig(
    filename=f'{ntpath.basename(os.path.basename(__file__)).replace(".py", "")}.log',
    format='%(levelname)s: %(message)s',
    level=logging.INFO
)


class CategoryGlossarySpider(scrapy.Spider):
    name = 'category_glossary'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
    custom_settings = {
            'FEEDS':{
                '../../../.output/mercadolibre_category_glossary_%(time)s.csv': {
                    'format': 'csv',
                    'encoding': 'utf8',
                    'overwrite': False
                },
            }
        }
    
    def start_requests(self):
        if hasattr(self, 'config_path'):
            self.config = config(config_path=self.config_path)
        else:
            self.config = config()
        if hasattr(self, 'category_href') and hasattr(self, 'category_level'):
            
            parent = self._extract_category_ids_from_href(self.category_href).get('c_category_id')
            if hasattr(self, 'parent'):
                parent = self.parent
                
            level = int(self.category_level)
            urls = [self.category_href]
            
            for url in urls:
                if level == 2:
                    yield scrapy.Request(url=url, meta={'parent_id': parent, "level": level}, callback=self.parse_category_page)
                if level == 3:
                    yield scrapy.Request(url=url, meta={'parent_id': parent, "level": level}, callback=self.parse_category_page)
                elif level == 4:
                    yield scrapy.Request(url=url, meta={'parent_id': parent, "level": level}, callback=self.parse_products_category_page)
        else:
            # print(self.country)
            urls = [
                # f'https://www.mercadolibre.com.{self.country}/categorias',
                self.config['marketplace']['mercadolibre']['country'][self.country]['url_categories']
            ]
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse_categories_page)

    def _next_category_page(self, href, meta, callback):
        return scrapy.Request(
            href,
            meta=meta,
            callback=callback
        )

    def parse_categories_page(self, response):
        ## self._create_web_page_file("mercadolibre.html", response.body)
        self.logger.info("parse_categories_page>> Visited %s", response.url)
        # TODO recorrer categorias de primer nivel
        level = 1
        for index, categories_container in enumerate(response.css(self.config['queries'][f'categories_container_level_{level}'])):
            href = categories_container.css(self.config['queries'][f'category_href_level_{level}']).attrib['href']
            id = self._extract_category_ids_from_href(href).get('c_category_id')
            yield self._extract_category_data(id, category_container=categories_container, href=href, index=index, level=1)
            # !add flag to recursive
            # # ?link de subcategorias 
            # yield self._next_category_page(
            #     href,
            #     {'parent_id': id, "level": 2},
            #     self.parse_category_page
            # )
        pass

    def parse_category_page(self, response):
        self.logger.info("parse_category_page>> Visited %s", response.url)
        level= response.meta.get('level')
        # TODO recorrer categorias de segundo nivel
        for index, categories_container in enumerate(response.css(self.config['queries'][f'categories_container_level_{level}'])):
            href = categories_container.css(self.config['queries'][f'category_href_level_{level}']).attrib['href']
            id = self._extract_category_ids_from_href("".join((href).split("#")[1:2])).get('c_category_id')
            yield self._extract_category_data(id, category_container=categories_container, href=href, index=index, level=level, parent=response.meta.get('parent_id'), hierarchy=2)
            # # TODO recorrer categorias de tercer nivel
            next_level= 3
            next_parent_id = copy.copy(id)
            for count, category_container in enumerate(categories_container.css(self.config['queries'][f'categories_container_level_{next_level}'])):
                href = category_container.css(self.config['queries'][f'category_href_level_{next_level}']).attrib['href']
                id = self._extract_category_ids_from_href("".join((href).split("#")[1:2])).get('c_category_id')
                yield self._extract_category_data(id, category_container=category_container, href=href, index=count, level=next_level, parent=next_parent_id, hierarchy=3)
                # !add flag to recursive
                # ?link de subcategorias
                # yield self._next_category_page(
                #     href,
                #     {'parent_id': id, "level": 4},
                #     self.parse_products_category_page
                # )
                #
    
    def parse_products_category_page(self, response):
        self.logger.info("parse_products_category_page>> Visited %s", response.url)
        level = 4
        for index, category_container in enumerate(response.css(self.config['queries'][f'categories_container_level_{level}'])):
            href = category_container.css(self.config['queries'][f'category_href_level_{level}']).attrib['href']
            id = "LAST_ID"
            yield self._extract_category_data(id, category_container=category_container, href=href, index=index, level=level, hierarchy=4, parent=response.meta.get('parent_id'))
        
    def _extract_category_data(self, id, category_container=None,  href:str =None, index:int =0, level:int=None, parent=None, hierarchy:int =1):
        
        if self.config['queries'][f'category_subcategories_level_{level}']:
            subcategories = len(category_container.css(self.config['queries'][f'category_subcategories_level_{level}']))
        else:
            subcategories = 0
          
        name = category_container.css(self.config['queries'][f'category_name_level_{level}']).get()
    
        return self._render_category_of_catalog(
            id=id,
            # uid=self._extract_category_ids_from_href(href).get('c_uid'),
            index=index,
            name=name,
            parent=parent,
            href=href,
            hierarchy=hierarchy,
            subcategories=subcategories
        )

    def _render_category_of_catalog(self, id=None, uid=None, name=None, parent=None, href=None, hierarchy=None,
                                    subcategories=0, index=0):
        # * prints
        # self._print_category_name(name, hierarchy)
        # * return itrm
        categoryItem = CategoryItem()
        categoryItem['id'] = id
        categoryItem['uid'] = uid
        categoryItem['parent'] = parent
        categoryItem['name'] = name
        categoryItem['href'] = href
        categoryItem['index'] = index
        categoryItem['hierarchy'] = hierarchy
        categoryItem['subcategories'] = subcategories
        return categoryItem

    def _extract_category_ids_from_href(self, href, split_separator='&', start=None, stop=None):
        """Return dict with category ids

        Args:
            href (str): link category

        Returns:
            [type]: {'c_category_id': str, 'c_uid': str}
        """
        # !CAMBIAR POR REGEX
        try:
            if start is None and stop is None:
                return {_.split("=")[0].replace("CATEGORY_ID", "c_category_id"): _.split("=")[1] for _ in
                        href.split(split_separator)}
            return {_.split("=")[0].replace("CATEGORY_ID", "c_category_id"): _.split("=")[1] for _ in
                    href.split(split_separator)[start:stop]} 
        except Exception as e:
            return "UNKNOWN"
        
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