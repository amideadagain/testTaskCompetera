import scrapy
from scrapy import Spider, Request
from ..items import CategoriesItem


# initially I  had everything in one spider and it worked, but I divided it into two, will have a second branch with one
class CategoriesSpider(scrapy.Spider):
    name = 'categories_spider'
    start_urls = ['https://allo.ua/']

    def parse(self, response):
        for categories in response.css("div.home-categories.snap-slider a::attr(href)"):
            yield Request(categories.get(), callback=self.parse_catalog)

    def parse_catalog(self, response):
        catalog_all = response.xpath(
            "//h2[@class='portal-category__title' and contains(text(), 'Каталог')]/../..//div[@class='accordion__content']//ul//a/@href")
        if response.xpath("//h2[@class='portal-category__title' and contains(text(), 'Каталог')]").get() is not None:
            for catalog in catalog_all:
                yield Request(catalog.get(), callback=self.parse_catalog)
        else:
            page_url = response.xpath("//head//link[@hreflang='uk']/@href").get()
            item = CategoriesItem()

            item['category_url'] = page_url

            yield item
