from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class CrawlingSpider(CrawlSpider):
    name = "chironCrawler"
    allowed_domains = ["gmanetwork.com"]
    start_urls = ["https://www.gmanetwork.com"] 

    rules = (
        Rule(LinkExtractor(), callback="parse_item", follow=True),
        # Rule(LinkExtractor(allow="catalogue", deny="category"), callback="parse_item"), 
    )

    def parse_item(self, response):
        yield {
            "title": response.css('.story_links::text').get(),
            "body": response.css('.story_main p::text').getall(),
        }
