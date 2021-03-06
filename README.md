# Big Commerce
Big commerce is a scraping tool for ecommerce in latam

### Prerequisites

Have python >= 3.7.4  installed

**Install Python packages with pip and requirements.txt:**

```sh
$ pip install -r requirements.txt
```
### Run Scraper

**Scrappy subcategories of a category in mercadolibre:**

```sh
$ python main.py mercadolibre
```
![alt text](https://github.com/91-julian-sanchez/big-commerce/blob/master/_assetes/mercadolibre.gif "Mercadolibre scraper")

**Scrappy subcategories of a category in linio:**

```sh
$ python main.py linio
```

**Options**
Optional argument | Description
--- | --- 
`--country` | Country code where you want to scrape marketplace, available: co, mx 
`--recursive` | Browse product pages recursively, available: True or False

**Marketplace and available commands:**

```sh
$ python main.py --help
```