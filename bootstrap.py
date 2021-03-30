from common import config
from menu import CliMenu


def render_cli_menu(name=None, message=None, choices=None):
    return CliMenu(
        name=name,
        message=message,
        choices=choices
    )


def select_marketplace_menu():
    selected = render_cli_menu(
        name='marketplace',
        message='Que marketplace quieres scrapear?',
        choices=Bootstrap.get_marketplace_avalible()
    ).start()
    # print(selected)
    return selected


class Bootstrap:
    MARKETPLACE_AVALIBLE = list(config()['marketplace'].keys())

    @classmethod
    def get_marketplace_avalible(cls):
        return cls.MARKETPLACE_AVALIBLE

    @classmethod
    def select_marketplace(cls):
        return select_marketplace_menu().get('marketplace')

    countries_config = None
    _countries_codes = None
    _marketplace = None
    country_config = None

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
        if country in self._countries_codes:
            self._country = country
            self.country_config = self.countries_config.get(country)
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

    def __init__(self, marketplace):
        self.marketplace = marketplace
        self.countries_config: dict = config()['marketplace'][self.marketplace]['country']
        self._countries_codes = list(self.countries_config.keys())
        self._country = None
        self._recursive = None

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
