# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScraperMotorItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class Categorytem(scrapy.Item):
    id = scrapy.Field()
    uid = scrapy.Field()
    parent = scrapy.Field()
    name = scrapy.Field()
    href = scrapy.Field()
    index = scrapy.Field()
    hierarchy = scrapy.Field()
    subcategories = scrapy.Field()
    pass