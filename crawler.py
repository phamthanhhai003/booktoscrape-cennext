import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
from scrapy import signals
import html
import re
import logging
from urllib.parse import urljoin
from pydantic import BaseModel
from typing import Optional
import os

def save_html(self, response, book_title):
    book_title = book_title.replace("/", "-")
    filename = f"html_backup/{book_title}.html"
    
    with open(filename, 'wb') as f:
        f.write(response.body)
        print(f"html raw {response.url}:  {filename}")
            
            
class BookDetail(BaseModel):
    title: Optional[str] = None
    price: Optional[str] = None
    availability: Optional[str] = None
    page_link: Optional[str] = None
    rating: Optional[int] = None
    

class IndexSpider(scrapy.Spider):
    name = 'bookstoscrape'
    start_urls = [f"https://books.toscrape.com/catalogue/category/books/sequential-art_5/index.html"]
    crawled_company_id = set()
    custom_settings = {
        'RETRY_HTTP_CODES': [403, 429, 500, 502, 503, 504],
        'RETRY_TIMES': 5,
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 32,
        'COOKIES_ENABLED': False,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    }
    
    def parse(self, response):
        next_page =  response.xpath('//li[@class="next"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        books = response.xpath('//article[@class="product_pod"]/h3/a/@href').getall()
        for book in books:
            yield scrapy.Request(url = urljoin(response.url, book), callback=self.parse_book_detail)
    
    def parse_book_detail(self, response):
        title = response.xpath('//h1/text()').get()
        price = response.xpath('//p[@class="price_color"]/text()').get()
        availability_field = response.xpath('//th[contains(text(), "Availability")]/following-sibling::td/text()').get()
        availability = re.search(r'(\d+)', availability_field).group(1) if availability_field else None
        page_link = response.url
        
        rating_star = None

        if response.xpath('//div[@class="col-sm-6 product_main"]/p[@class="star-rating One"]').get():
            rating_star = 1
        elif response.xpath('//div[@class="col-sm-6 product_main"]/p[@class="star-rating Two"]').get():
            rating_star = 2
        elif response.xpath('//div[@class="col-sm-6 product_main"]/p[@class="star-rating Three"]').get():
            rating_star = 3
        elif response.xpath('//div[@class="col-sm-6 product_main"]/p[@class="star-rating Four"]').get():
            rating_star = 4
        elif response.xpath('//div[@class="col-sm-6 product_main"]/p[@class="star-rating Five"]').get():
            rating_star = 5

        if rating_star is not None:
            print(f"Rating:{page_link} {rating_star} stars")
        else:
            print(f"Rating not found for: {page_link}")
        
        save_html(self, response, title)
        book = BookDetail(
            title=title,
            price=price,
            availability=availability,
            page_link=page_link,
            rating=rating_star if rating_star else None,
        )
        yield book        

def run_index_crawler():
    logging.info("Starting Scrapy Spider")
    process = CrawlerProcess(settings={
        "LOG_LEVEL": "INFO",
        "FEEDS": {
            "books.csv": {
                "format": "csv",
                "overwrite": True,
            },
        },
    })
    def stop_scrapy():
        logging.info("Stopping Scrapy Spider")
        process.stop()

    dispatcher.connect(stop_scrapy, signal=signals.spider_closed)

    process.crawl(IndexSpider)
    process.start()
    logging.info("Scrapy Spider finished")

def main_crawler():
    run_index_crawler()