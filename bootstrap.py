from common import config

class Bootstrap:
    
    countries_config = None
    country_config = None
    _countries_codes = None
    
    @property
    def recursive(self):
        return self._recursive
    
    @recursive.setter
    def recursive(self, recursive: str):
        if recursive is True or recursive == 'True' or recursive is False or recursive is 'False':
            self._recursive = bool(recursive)
        elif recursive is None:
            self.recursive = False      
        else:
            raise Exception("Recursion no valida.")
        
    @property 
    def country(self):
        return self._country
    
    @country.setter
    def country(self, country: str):
        if country in self._countries_codes:
            self._country = country
            self.country_config = self.countries_config.get(country)
        else:
            raise Exception("Codigo de pais invalido.", country)
      
    def __init__(self, marketplace):
        self.marketplace = marketplace
        self.countries_config: dict = config()['marketplace'][self.marketplace]['country']
        self._countries_codes = list(self.countries_config.keys())
        self._country = None
        self._recursive = None
        
if __name__ == '__main__':
    bootstrap = Bootstrap("mercadolibre")
    print(bootstrap.marketplace)
    bootstrap.country = 'co'
    print(bootstrap.country)
    print(bootstrap.country_config)
    bootstrap.recursive = True
    print(bootstrap.recursive)