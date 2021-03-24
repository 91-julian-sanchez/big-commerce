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
Example: 
* scrapy crawl category_glossary
* scrapy crawl category_glossary  -a category_level=2 -a category_id=MCO1276 -a category_href=https://www.mercadolibre.com.co/c/deportes-y-fitness#c_id=/home/categories/category-l1/category-l1&c_category_id=MCO1276&c_uid=bb43bf2e-8b17-11eb-81c9-e9c5bb60a707
