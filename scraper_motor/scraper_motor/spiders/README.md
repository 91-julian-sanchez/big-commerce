### Create a new spider 
```bash
$ scrapy genspider {NAME_SPIDER} {URL_TO_CRAWLING}
```
### Run spider 
```bash
$ scrapy crawl {NAME_SPIDER}
```


**Options**
Optional argument | Description
--- | --- 
`-a category_href="{}" -a category_level={}` | Scraper category page
`--nolog` | Sets LOG_ENABLED to False

DOWNLOAD_DELAY: pause length to (N) seconds
Example: Deportes y Fitness > Ciclismo: 
* All categories
```bash
 $ scrapy crawl category_glossary
```

* Deportes y Fitness categories
```bash
scrapy crawl category_glossary -a category_href="https://www.mercadolibre.com.co/c/deportes-y-fitness#c_id=/home/categories/category-l1/category-l1&c_category_id=MCO1276&c_uid=5ae2440d-8ea8-11eb-bca2-5da2288c72af" -a category_level=2
```

* Accesorios para Bicicletas category
```bash
scrapy crawl category_glossary -a category_href="https://deportes.mercadolibre.com.co/ciclismo-accesorios-bicicletas/#CATEGORY_ID=MCO12214&S=hc_deportes-y-fitness" -a category_level=4
```
