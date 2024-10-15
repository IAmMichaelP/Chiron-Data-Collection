from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest

class CrawlingSpider(CrawlSpider):
    name = "philstarCrawler"
    allowed_domains = ["philstar.com"]
    start_urls = ["https://www.philstar.com/pilipino-star-ngayon/"]

    # Modify the rule to match health and wellness article links more precisely
    rules = (
        Rule(),
        # Rule(LinkExtractor(allow="healthandwellness"), follow=True),
        # Rule(LinkExtractor(allow="archives/lifestyle-healthandwellness/")),
        # Rule(LinkExtractor(allow=r"lifestyle/healthandwellness/\d+/*")),
        # Rule(LinkExtractor(allow=r"lifestyle/healthandwellness/\d+/.+/story/"), callback="parse_item", follow=True),
        
    )
