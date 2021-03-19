import scrapy
import copy
import yaml

__config = None


def config():
    global __config
    if not __config:
        with open('config.yaml', mode='r') as f:
            __config = yaml.load(f, Loader=yaml.FullLoader)

    return __config


class CategoryGlossarySpider(scrapy.Spider):
    name = 'category_glossary'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
    # allowed_domains = ['https://www.mercadolibre.com.co']
    # start_urls = ['https://www.mercadolibre.com.co/categorias']
    custom_settings = {'FEED_URI': "category_glossary.csv",
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
        # TODO recorrer categorias de primer nivel
        for index, categories_container in enumerate(response.css(config()['queries']['categories_container'])):
            href = categories_container.css(config()['queries']['category_href']).attrib['href']
            id = self._extract_category_ids_from_href(href).get('c_category_id')
            yield self._extract_category_data(categories_container, id, href, index)
            # ?link de subcategorias
            yield self._next_category_page(
                href,
                {'parent_id': id},
                self.parse_category_page
            )
        pass

    def parse_category_page(self, response):
        # self.logger.info("Visited %s", response.url)
        for index, categories_container in enumerate(response.css(config()['queries']['categories_container_category_page'])):
            href = categories_container.css('a').attrib['href']
            id = self._extract_category_ids_from_href("".join((href).split("#")[1:2])).get('c_category_id')
            yield self._render_category_of_catalog(
                id=id,
                uid=None,
                index=index,
                name=categories_container.css(config()['queries']['category_name_category_page']).get(),
                parent=response.meta.get('parent_id'),
                href=href,
                hierarchy=2,
                subcategories=len(categories_container.css(config()['queries']['category_subcategories_category_page']))
            )
            # for category_container in categories__container.css("ul.desktop__view-ul > li"):
            #     parent = copy.copy(id)
            #     href = category_container.css('a').attrib['href']
            #     # category_id = self._extract_category_ids_from_href("".join((href).split("#")[1:2])).get('c_category_id')
            #     uid = None
            #     name = category_container.css('h4::text').get()
            #     hierarchy = 3
            #     subcategories = 0
            #     yield self._render_category_of_catalog(
            #         category_id=self._extract_category_ids_from_href("".join((href).split("#")[1:2])).get('c_category_id'),
            #         uid=uid,
            #         name=name,
            #         parent=parent,
            #         href=href,
            #         hierarchy=hierarchy,
            #         subcategories=subcategories
            #     )

    def _extract_category_data(self, category_container, id, href, index):
        return self._render_category_of_catalog(
            id=id,
            uid=self._extract_category_ids_from_href(href).get('c_uid'),
            index=index,
            name=category_container.css(config()['queries']['category_name']).get(),
            parent=None,
            href=href,
            hierarchy=1,
            subcategories=len(category_container.css(config()['queries']['category_subcategories']))
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