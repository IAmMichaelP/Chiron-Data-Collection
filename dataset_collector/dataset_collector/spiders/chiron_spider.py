from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest

# class CrawlingSpider(CrawlSpider):
#     name = "chironCrawler"
#     allowed_domains = ["gmanetwork.com"]
#     start_urls = ["https://www.gmanetwork.com/news"]

#     # Modify the rule to match health and wellness article links more precisely
#     rules = (
#         Rule(LinkExtractor(allow="lifestyle/healthandwellness")),
#         Rule(LinkExtractor(allow="healthandwellness"), follow=True),
#         Rule(LinkExtractor(allow="archives/lifestyle-healthandwellness/")),
#         Rule(LinkExtractor(allow=r"lifestyle/healthandwellness/\d+/*")),
#         # Rule(LinkExtractor(allow=r"lifestyle/healthandwellness/\d+/.+/story/"), callback="parse_item", follow=True),
        
#     )



# from scrapy_splash import SplashRequest
# from scrapy.spiders import CrawlSpider

# class CrawlingSpider(CrawlSpider):
#     name = "chironCrawler"

#     def start_requests(self):
#         url = 'https://www.gmanetwork.com/news/lifestyle/healthandwellness/922501/phasing-out-teen-smoking-could-save-1-2-million-lives-who-cancer-agency-study/story/'
#         yield SplashRequest(url=url, callback=self.parse, args={'wait': 5})  # Increase wait time
    
#     def parse(self, response):
#         yield {
#             'title': response.css('.story_links::text').get(),
#             'body': response.css('.story_main p::text').getall(),
#         }

#  ----------------------------

class CrawlingSpider(CrawlSpider):
    name = "chironCrawler"

    def start_requests(self):
        url = 'https://www.gmanetwork.com/news/archives/lifestyle-healthandwellness/'
        yield SplashRequest(url=url, callback=self.parse, args={'wait': 5})  # Increase wait time
    
    def parse(self, response):
        yield {
            'title': response.css('.story_link::text').getall(),
            # 'body': response.css('.story_main p::text').getall(),
        }