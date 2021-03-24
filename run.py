import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraper_motor.scraper_motor.spiders.category_glossary import CategoryGlossarySpider

if __name__ == "__main__":
  # process = CrawlerProcess(get_project_settings())
  process = CrawlerProcess({
    'LOG_ENABLED': False
  })
  process.crawl(CategoryGlossarySpider, config_path='./')
  process.start()