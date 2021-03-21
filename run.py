import scrapy
from scrapy.crawler import CrawlerProcess
from scraper_motor.scraper_motor.spiders.category_glossary import CategoryGlossarySpider

if __name__ == "__main__":
  process = CrawlerProcess()
  process.crawl(CategoryGlossarySpider)
  process.start()