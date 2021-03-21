# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class ScraperMotorItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.scrapy.Field()
    pass

class CategoryItem(scrapy.Item):
    id:str = scrapy.Field()
    uid:str = scrapy.Field()
    parent:int = scrapy.Field()
    name:str = scrapy.Field()
    href:str = scrapy.Field()
    index:int = scrapy.Field()
    hierarchy:int = scrapy.Field()
    subcategories:int = scrapy.Field()
    pass