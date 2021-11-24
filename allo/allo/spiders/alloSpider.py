import scrapy
from scrapy import Request
from ..items import AlloItem
from datetime import datetime
import requests
import json
from ..read_files import read_csv


class AlloSpider(scrapy.Spider):
    name = 'allo_spider'
    payload = {}
    headers = {
        'authority': 'allo.ua',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'x-use-nuxt': '1',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
        'content-type': 'text/plain',
        'accept': 'application/json, text/plain, */*',
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6',
    }

    def start_requests(self):
        for category_page in read_csv():
            print(category_page)
            yield Request(category_page, callback=self.parse_pages)

    def parse_pages(self, response):
        for product_url in response.css("div.product-card__img a::attr(href)"):
            product_id = response.css(
                "div.products-layout__container div.products-layout__item::attr(data-product-id)").get()
            product_url_to_pass = product_url.get()
            yield Request(product_url_to_pass,
                          callback=self.parse_product,
                          cb_kwargs={'url': product_url_to_pass, 'product_id': product_id})

        next_page_url = response.css("div.pagination__next a::attr(href)").extract_first()
        if next_page_url is not None:
            yield Request(response.urljoin(next_page_url))

    def parse_product(self, response, url, product_id, payload=payload, headers=headers):
        for product in response.css("div.page__content"):
            scanned_at = datetime.now().isoformat()
            title = product.css("div.p-view__header h1::text").get()
            sku = product.css("span.p-view__header-sku__code::text").get().strip()
            category = product.css("ul.breadcrumbs li a.breadcrumbs__link::text").extract()
            # I initially had this line for deleting ""Інтернет магазин"" from categories, but I commented it before
            # the last scraping cause thought for a second that I need it, and now I'm very disappointed in this
            del category[0]
            category = json.dumps(category, ensure_ascii=False)

            if product.css("span.p-trade__stock-label-icon::text").get() is not None:
                availability = True
            else:
                availability = False

            price = product.css("div.p-trade-price__current span.sum::text").get(default=None)
            price_regular = product.css("div.p-trade-price__old span.sum::text").get(default=None)
            if price_regular is None:
                price_regular = price

            seller = product.css("div.shipping-seller-logo span.shipping-brand__name::text").get(default='Allo')

            discounts_url = f"https://allo.ua/ua/discounts/product/items/?sku={sku}&isAjax=1&currentLocale=uk_UA"
            services_url = f"https://allo.ua/ua/catalog/product/getServices/?id={product_id}&isAjax=1&currentLocale=uk_UA"
            offers_url = f"https://allo.ua/ua/ajax/block/get/?collection=[%7B%22conteinerId%22:%22forceGet%22,%22type%22:%22ajax%22,%22request%22:%22oggetto_cshipping%2Fshipping%2Fdata%22,%22data%22:%7B%22productId%22:{product_id},%22cityId%22:10%7D%7D]&isAjax=1&currentLocale=uk_UA"

            special_offers_list = []

            discounts_response = requests.request("GET", discounts_url, headers=headers, data=payload)
            services_response = requests.request("GET", services_url, headers=headers, data=payload)
            offers_response = requests.request("GET", offers_url, headers=headers, data=payload)

            # if there is no offers we get [] string
            if len(discounts_response.text) > 2:
                discounts = json.loads(discounts_response.text)
                for discount in discounts:
                    special_offers_list.append(discount['title'] + ' ' + discount['text'])

            services = json.loads(services_response.text)
            if services["success"] and len(services["data"]) > 2:
                for service in services["data"]:
                    special_offers_list.append(service['type_title'])

            offers = json.loads(offers_response.text)
            try:
                for shipping_offer in offers["result"]["forceGet"]["shipping_methods"]["data"]:
                    special_offers_list.append(shipping_offer["method_name"])
            except:
                print("no shipping offers")

            try:
                for payment_offer in offers["result"]["forceGet"]["payment_methods"]["data"].split(', '):
                    special_offers_list.append(payment_offer)
            except:
                print("no payment offers")

            special_offers = json.dumps(special_offers_list, ensure_ascii=False)

            item = AlloItem()

            item["scanned_at"] = scanned_at
            item["title"] = title
            item["url"] = url
            item["sku"] = sku
            item["category"] = category
            item["availability"] = availability
            if price is not None:
                item["price"] = price
            if price_regular is not None:
                item["price_regular"] = price_regular
            item["seller"] = seller
            item["special_offers"] = special_offers

            yield item
