import scrapy
import logging
import os
import ntpath
from ..items import CategoryItem
from ..common import config

logging.basicConfig(
    filename=f'{ntpath.basename(os.path.basename(__file__)).replace(".py", "")}.log',
    format='%(levelname)s: %(message)s',
    level=logging.INFO
)

class LinioGlossarySpider(scrapy.Spider):
    name = 'linio'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
    custom_settings = {
            'FEEDS':{
                '../../../.output/linio_category_glossary_%(time)s.csv': {
                    'format': 'csv',
                    'encoding': 'utf8',
                    'overwrite': False
                },
            }
        }
    
    def start_requests(self):
        self.config = config()
        if hasattr(self, 'country'):
            self.country = self.country
            
        urls = [
            self.config['marketplace']['linio']['country'][self.country]['url_categories']
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        # self._create_web_page_file('linio.html', response.body)
        nav_container = response.xpath('//li[@class="nav-item"]')
        for category_container in nav_container: 
            yield self._render_category_of_catalog(
                id=category_container.xpath('a').attrib['href'], 
                uid=None, 
                name=category_container.xpath('a').attrib['title'], 
                parent=None, 
                href=f"{self.config['marketplace']['linio']['country'][self.country]['origin']}{category_container.xpath('a').attrib['href']}", 
                hierarchy=1,
                subcategories=0, 
                index=0
            )
        pass
    
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

    def _create_web_page_file(self, filename, body):
        with open(filename, 'wb') as f:
            f.write(body)
        self.log(f'Saved file {filename}')
        pass