from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class CrawlingSpider(CrawlSpider):
    name = "chironCrawler"
    allowed_domains = ["abs-cbn.com"]
    start_urls = ["https://news.abs-cbn.com/"]

    rules = (
        Rule(LinkExtractor(allow="lifestyle/health-wellness/*")),
        # Rule(LinkExtractor(allow="catalogue", deny="category"), callback="parse_item"), 
    )

    def parse_item(self, response):
        yield {
            "body": response.css("#bodyTopPart h5 div p::text").get(),
            # "price": response.css(".price_color::text").get(),
            # "availability": response.css(".availability::text")[1].get().strip(),
        }
