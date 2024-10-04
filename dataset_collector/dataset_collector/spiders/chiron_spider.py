from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest

class CrawlingSpider(CrawlSpider):
    name = "chironCrawler"
    allowed_domains = ["gmanetwork.com"]
    start_urls = ["https://www.gmanetwork.com/news/lifestyle/healthandwellness/"]

    # Modify the rule to match health and wellness article links more precisely
    rules = (
        Rule(LinkExtractor(allow=r"lifestyle/healthandwellness/\d+/.+/story/"), callback="parse_item", follow=True),
    )

    # This method processes the response using SplashRequest
    def parse_item(self, response):
        # Instead of directly parsing the item, use SplashRequest for JS rendering
        yield SplashRequest(url=response.url, callback=self.parse_with_splash, args={'wait': 5})

    # This method parses the response after rendering with Splash
    def parse_with_splash(self, response):
        yield {
            "url": response.url,  # The URL being scraped
            "title": response.css('.story_links::text').get(),  # Extract the title
            "body": response.css('.story_main p::text').getall(),  # Extract the body
        }
