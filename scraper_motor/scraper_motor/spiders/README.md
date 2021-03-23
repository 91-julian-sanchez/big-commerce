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
`-a category_id={CATEGORY_ID} -a category_href={CATEGORY_HREF}` | Scraper category page
`--nolog` | Sets LOG_ENABLED to False

DOWNLOAD_DELAY: pause length to (N) seconds

