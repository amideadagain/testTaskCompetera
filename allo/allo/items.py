# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst


def remove_currency(value):
    return float(value.strip().replace('\xa0', '').replace('₴', ''))


class AlloItem(scrapy.Item):
    # define the fields for your item here like:
    scanned_at = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    sku = scrapy.Field()
    category = scrapy.Field()
    availability = scrapy.Field()
    price = scrapy.Field(serializer=remove_currency)
    price_regular = scrapy.Field(serializer=remove_currency)
    seller = scrapy.Field()
    special_offers = scrapy.Field()


class CategoriesItem(scrapy.Item):
    category_url = scrapy.Field()
