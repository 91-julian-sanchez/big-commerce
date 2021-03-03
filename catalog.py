#* Categorias: https://www.mercadolibre.com.co/categorias#nav-header
# https://deportes.mercadolibre.com.co/accesorios-bicicletas-seguridad-cascos/#applied_filter_id=category&applied_filte_name=Categor%C3%ADas&applied_filter_order=4&applied_value_id=MCO158235&applied_value_name=Cascos&applied_value_order=2&applied_value_results=20601
class Catalog:
    
    def __init__(self, name):
        self.name = name
        

class MarketplaceCatalog(Catalog):
    
    @property
    def host(self):
        return self._host
    
    @host.setter
    def host(self, host):
        self._host = host
        
    @property
    def category_index(self):
        return self._category_index
    
    @category_index.setter
    def category_index(self, category_index):
        self._category_index = category_index
        
    def __init__(self, name):
        super().__init__(name)
        self._host = None
        self._paginator = None
        self._category_index = []
     
        
class CategoryIndex:
    
    def __init__(self):
        self.categories = []
    
    def add_category(self, category):
        self.categories.append(category)


class Category:
    def __init__(self, name):
        self.name = name
        self.subcategories:Category = []
     
     
def print_category_index(category, prefix):
    print(f"{prefix} {category.name}")
    for subcategory in category.subcategories:
        print_category_index(subcategory, prefix+"-")
    
    
if __name__ == '__main__':
    marketplaceCatalog = MarketplaceCatalog("mercadolibre")
    print(marketplaceCatalog.name)
    marketplaceCatalog.host = 'https://www.mercadolibre.com.co/'
    print(marketplaceCatalog.host)
    categoryIndex = CategoryIndex()
    #! ==============================================
    category = Category("Deportes y Fitness")
    category.subcategories = (
        Category('Bádminton'),
        Category('Baloncesto'),
        Category('Balonmano'),
        Category('Boxeo y Artes Marciales'),
        Category('Buceo'),
        Category('Camping, Caza y Pesca'),
        Category('Canoas, Kayaks e Inflables'),
        Category('Ciclismo'),
        Category('Equitación y Polo'),
        Category('Esgrima'),
        Category('Esqui y Snowboard'),
        Category('Fitness y Musculación'),
        Category('Fútbol'),
        Category('Fútbol Americano'),
        Category('Golf'),
        Category('Hockey'),
        Category('Juegos de Salón'),
        Category('Kitesurf'),
        Category('Monopatines y Scooters'),
        Category('Montañismo y Trekking'),
        Category('Natación'),
        Category('Paintball'),
        Category('Parapente'),
        Category('Patín, Gimnasia y Danza'),
        Category('Pulsómetros y Cronómetros'),
        Category('Ropa Deportiva'),
        Category('Rugby'),
        Category('Skateboard y Sandboard'),
        Category('Slackline'),
        Category('Softball y Beisbol'),
        Category('Suplementos y Shakers'),
        Category('Surf y Bodyboard'),
        Category('Tenis'),
        Category('Tenis, Padel y Squash'),
        Category('Tiro Deportivo'),
        Category('Voleibol'),
        Category('Wakeboard y Esqui Acuático'),
        Category('Windsurf'),
        Category('Yoga y Pilates'),
        Category('Otros'),
    )
    category.subcategories[7].subcategories = (
        Category('Accesorios para Bicicletas'),
        Category('Indumentaria'),
        Category('Bicicletas'),
        Category('Repuestos'),
        Category('Bicicletas Fijas'),
        Category('Bicicletas Eléctricas'),
        Category('Otros')
    )
    category.subcategories[7].subcategories[0].subcategories = (
        Category('Seguridad'),
        Category('Portabicicletas'),
        Category('Velocímetros'),
        Category('Transporte y Carga'),
        Category('Herramientas'),
        Category('Bombas de Aire'),
        Category('Fundas Cubre Bicicleta'),
        Category('Guardafangos'),
        Category('Rodillos'),
    )
    category.subcategories[7].subcategories[0].subcategories[0].subcategories = (
        Category('Cascos'),
        Category('Luces'),
        Category('Guayas y Candados'),
        Category('Bocinas'),
        Category('Espejos Retrovisores'),
        Category('Cubre Cadenas'),
        Category('Otros'),
    )
    categoryIndex.add_category(category)
    #! ==============================================
    category = Category("Computación")
    category.subcategories = (
        Category('Accesorios de Antiestática'),
        Category('Accesorios para PC Gaming'),
        Category('Almacenamiento'),
        Category('Cables y Hubs USB'),
        Category('Componentes de PC'),
        Category('Conectividad y Redes'),
        Category('Estabilizadores y UPS'),
        Category('Impresión'),
        Category('Lectores y Scanners'),
        Category('Limpieza y Cuidado de PCs'),
        Category('Monitores y Accesorios'),
        Category('Palms, Agendas y Accesorios'),
        Category('PC de Escritorio'),
        Category('Periféricos de PC'),
        Category('Porta CDs, Cajas y Sobres'),
        Category('Portátiles y Accesorios'),
        Category('Software'),
        Category('Tablets y Accesorios'),
        Category('Video Beams y Pantallas'),
        Category('Otros'),
    )
    categoryIndex.add_category(category)
    
    #TODO
    marketplaceCatalog.category_index = categoryIndex.categories
    for category in marketplaceCatalog.category_index:
        print_category_index(category, "")