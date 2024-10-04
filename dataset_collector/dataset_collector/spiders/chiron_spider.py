from scrapy_splash import SplashRequest
from scrapy.spiders import CrawlSpider

class CrawlingSpider(CrawlSpider):
    name = "chironCrawler"

    def start_requests(self):
        url = 'https://www.gmanetwork.com/news/lifestyle/healthandwellness/922501/phasing-out-teen-smoking-could-save-1-2-million-lives-who-cancer-agency-study/story/'
        yield SplashRequest(url=url, callback=self.parse, args={'wait': 5})  # Increase wait time
    
    def parse(self, response):
        yield {
            'title': response.css('.story_links::text').get(),
            'body': response.css('.story_main p::text').getall(),
        }
