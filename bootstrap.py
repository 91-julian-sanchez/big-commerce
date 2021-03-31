from common import config
from menu import CliMenu
import pandas as pd
import csv
import os
from os import walk
import subprocess


def render_cli_menu(name=None, message=None, choices=None):
    return CliMenu(
        name=name,
        message=message,
        choices=choices
    )


def select_marketplace_menu(choices: list = None):
    selected = render_cli_menu(
        name='marketplace',
        message='Que marketplace quieres scrapear?',
        choices=choices
    ).start()
    # print("selected: ", selected)
    return selected


def select_country_menu(choices: list = None):
    selected = render_cli_menu(
        name='country',
        message='En que país?',
        choices=choices
    ).start()
    # print("selected: ", selected)
    return selected


def select_category_menu(choices):
    selected = render_cli_menu(
        name='category',
        message='Que categoria?',
        choices=choices
    ).start()
    # print("selected: ", selected)
    category_selected = list(filter(lambda choice: choice.get('name') == selected.get('category'), choices))
    if len(category_selected) > 0:
        return category_selected[0]
    else:
        return None


def confirm_init_scraper_menu(message):
    selected = CliMenu(questions={
        'type': 'confirm',
        'message': message,
        'name': 'continue',
        'default': True,
    }).start()
    # print(selected)
    return selected


def remove_duplicates_header_rows(path):
    with open(path) as f:
        data = list(csv.reader(f))
        new_data = [a for i, a in enumerate(data) if a not in data[:i]]
        with open(path, 'w') as t:
            write = csv.writer(t)
            write.writerows(new_data)


def open_last_scrapy_file(pid=None):
    if not os.path.exists('./.output'):
        os.makedirs('./.output')
    import time
    # print("Printed immediately.")
    time.sleep(5)
    _, _, filenames = next(walk("./.output"))
    path = f"./.output/{filenames[len(filenames) - 1]}"
    remove_duplicates_header_rows(path)
    df = pd.read_csv(path)
    # raise Exception('kill')
    return df


def motor_scraper_subprocess_shell(marketplace=None, country=None, category_level=None, category_href=None, parent=None,
                                   debug=False, pid=None):
    wd = os.getcwd()
    os.chdir("scraper_motor/scraper_motor/spiders/")
    # subprocess.Popen("ls")
    nolog = '--nolog'
    if debug is True:
        nolog = ''

    argument_country = ''
    if country is not None:
        argument_country = f'-a country={country}'

    argument_parent = ''
    if parent is not None:
        argument_parent = f'-a parent={parent}'

    output = ''
    if pid is not None:
        output = f'-o "../../../.output/{pid}-{marketplace}-{country}-categories.csv"'

    if category_level is not None and category_href is not None:
        command = f'scrapy crawl category_glossary {argument_country} -a category_level={category_level} -a category_href="{category_href}" {argument_parent} {output} {nolog}'
    else:
        command = f"scrapy crawl category_glossary {argument_country} {output} {nolog}"

    # print(f"command>> {command}")
    # subprocess.run(command)
    subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    os.chdir(wd)


def motor_scraper_start(marketplace, country, category_level=None, category_href=None, parent=None, debug=None,
                        pid=None):
    if marketplace == 'mercadolibre':
        motor_scraper_subprocess_shell(marketplace=marketplace, country=country, category_level=category_level,
                                       parent=parent, category_href=category_href, debug=debug, pid=pid)
    else:
        print("linio no esta en scrapy")


class Bootstrap:
    CONFIG = config()
    countries_config = None
    country_config = None
    _marketplace = None
    _recursive = None
    _debug = None

    @classmethod
    def get_marketplace_avalible(cls):
        return list(cls.CONFIG['marketplace'].keys())

    @classmethod
    def select_marketplace(cls):
        return select_marketplace_menu(
            choices=list(cls.CONFIG['marketplace'].keys())
        ).get('marketplace')

    @classmethod
    def select_country(cls, marketplace=None):
        return select_country_menu(
            choices=list(cls.CONFIG['marketplace'][marketplace]['country'].keys())
        ).get('country')

    @property
    def marketplace(self):
        return self._marketplace

    @marketplace.setter
    def marketplace(self, marketplace):
        if marketplace in Bootstrap.get_marketplace_avalible():
            self._marketplace = marketplace
        else:
            raise Exception(f"Marketplace invalido: {marketplace}")

    @property
    def country(self):
        return self._country

    @country.setter
    def country(self, country: str):
        if country in list(self.countries_config.keys()):
            self._country = country
        else:
            raise Exception(f"Codigo de pais invalido: {country}")

    @property
    def recursive(self):
        return self._recursive

    @recursive.setter
    def recursive(self, recursive: str):
        if recursive is True or recursive == 'True' or recursive is False or recursive == 'False':
            self._recursive = bool(recursive)
        elif recursive is None:
            self.recursive = False
        else:
            raise Exception("Recursion no valida.")

    def __init__(self, marketplace, country, recursive=False, debug=False):
        self.debug = debug
        self.marketplace = marketplace
        self.countries_config: dict = self.CONFIG['marketplace'][marketplace]['country']
        self.country = country
        self.country_config = self.countries_config.get(country)
        self.recursive = recursive

    def category_glossary(
            self, marketplace, country, pid, debug_mode, level=1, category: dict = None, parent_category: dict = None
    ):
        # TODO INIT SCRAPER =====================================================================
        category_glossary_tree = []
        # * LEVEL 1
        if level == 1:
            print(f"Crawl {marketplace}: Extrayendo categorias...")
            motor_scraper_start(marketplace, country, pid=pid, debug=debug_mode)
            category_glossary_df = open_last_scrapy_file(pid=pid)
            categories = [{'name': row['name'], 'href': row['href'], 'id': row['id'], 'parent': row['parent'],
                           'hierarchy': row['hierarchy']} for index, row in category_glossary_df.iterrows()]
        # * LEVEL 2
        if level == 2:
            print(f"Crawl {marketplace}> Extrayendo categorias de '{category.get('name')}'...")
            motor_scraper_start(marketplace, country, pid=pid, category_level=level,
                                category_href=category.get('href'), debug=debug_mode)
            category_glossary_df = open_last_scrapy_file()
            level_2_category_glossary_df = category_glossary_df[category_glossary_df['hierarchy'] == 2]
            categories = [{'name': row['name'], 'href': row['href'], 'id': row['id'], 'parent': row['parent'],
                           'hierarchy': row['hierarchy']} for index, row in level_2_category_glossary_df.iterrows()]

        # * LEVEL 3
        if level == 3:
            print(
                f"Crawl {marketplace}: Extrayendo categorias de '{parent_category.get('name')} > {category.get('name')}'...")
            category_glossary_df = open_last_scrapy_file()
            level_3_category_glossary_df = category_glossary_df[category_glossary_df['parent'] == category.get('id')]
            for index, row in level_3_category_glossary_df.iterrows():
                category_glossary_tree.append(
                    {'name': row['name'], 'href': row['href'], 'id': row['id'], 'parent': row['parent'],
                     'hierarchy': row['hierarchy']})
                try:
                    # * LEVEL 4
                    motor_scraper_start(marketplace, country, pid=pid, category_level=4,
                                        category_href=row['href'], debug=debug_mode, parent=row['id'])
                    level_4_category_glossary_df = open_last_scrapy_file()
                    level_4_category_glossary_df = level_4_category_glossary_df[
                        level_4_category_glossary_df['parent'] == row['id']
                        ]
                    for index, row in level_4_category_glossary_df.iterrows():
                        category_glossary_tree.append(
                            {'name': row['name'], 'href': row['href'], 'id': row['id'], 'parent': row['parent'],
                             'hierarchy': row['hierarchy']})
                except Exception as e:
                    print(e)

            return category_glossary_tree
        # print("categories: ", categories)
        return categories

    def __str__(self):
        return f"marketplace is {marketplace}"

    def __repr__(self):
        return f"marketplace={marketplace}"


if __name__ == '__main__':
    print(Bootstrap.get_marketplace_avalible())
    bootstrap = Bootstrap("mercadolibre")
    print(bootstrap.marketplace)
    bootstrap.country = 'co'
    print(bootstrap.country)
    print(bootstrap.country_config)
    bootstrap.recursive = True
    print(bootstrap.recursive)
