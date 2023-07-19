import scrapy
import random
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlparse, urljoin
from pymongo import MongoClient

class MySpider(scrapy.Spider):
    name = 'my_spider'
    proxy_list = []

    def load_proxies():
        proxies = []
        with open("proxies.txt", "r") as file:
            for line in file:
                proxy = line.strip()
                proxies.append(proxy)
            return proxies

    proxy_list = load_proxies()

    def __init__(self, start_url, database_url, database_name, collection_name, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.allowed_domains = [urlparse(start_url).netloc]
        self.database_url = database_url
        self.database_name = database_name
        self.collection_name = collection_name
        self.visited_urls = set()

    def parse(self, response):
        current_url = response.url
        self.visited_urls.add(current_url)

        custom_settings = {
            'ROBOTSTXT_OBEY': False
        }

        # Extract and process the desired data using Scrapy selectors
        page_data = response.xpath('/html').extract()
        data = {
            'url': current_url,
            'title': response.xpath('//title/text()').get().strip(),
            'page': page_data
        }
        self.save_to_mongodb(data)
        page_index = 0
        with open(urlparse(start_url).netloc + '_' + str(page_index) + '.txt', 'w') as file:
            file.write(' '.join(page_data))
            page_index += 1


        # Find internal links and follow them
        for link in response.css('a::attr(href)').getall():
            absolute_url = urljoin(response.url, link)
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept': '*/*',
                'X-Requested-With': 'XMLHttpRequest',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.8,fr;q=0.6,ta;q=0.4,bn;q=0.2'
            }
            if absolute_url not in self.visited_urls:
                yield scrapy.Request(absolute_url, headers=headers, callback=self.parse, meta={'proxy': self.get_random_proxy()})

    def get_random_proxy(self):
        return random.choice(self.proxy_list)

    def save_to_mongodb(self, data):
        client = MongoClient(self.database_url)
        db = client[self.database_name]
        collection = db[self.collection_name]
        collection.insert_one(data)
        client.close()

if __name__ == "__main__":
    start_url = "https://www.uol.com.br"
    database_url = "mongodb://ricardo:ricardo@127.0.0.1:27017/my-mongo-db"
    database_name = "my-mongo-db"
    collection_name = "pages"

    process = CrawlerProcess()
    process.crawl(MySpider, start_url=start_url, database_url=database_url, database_name=database_name, collection_name=collection_name)
    process.start()