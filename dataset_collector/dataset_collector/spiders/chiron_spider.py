from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest
# fetch('http://localhost:8050/render.html?url=https://www.gmanetwork.com/news/lifestyle/healthandwellness/922501/phasing-out-teen-smoking-could-save-1-2-million-lives-who-cancer-agency-study/story/')

class CrawlingSpider(CrawlSpider):
    name = "chironCrawler"
    
    # S
    # 
    tart requests method
    def start_requests(self):
        url = 'https://news.abs-cbn.com/lifestyle/health-wellness/2024/10/3/pink-crossing-in-celebration-of-breast-cancer-awareness-month-1433'
        yield SplashRequest(url=url, callback=self.parse)
    
    # Parsing the response
    def parse(self, response):
        yield {
            'title': response.css('.css-u1oaus h2::texscrt').get(),  # Adjust this selector if needed
            'body': response.css('#bodyTopPart p::text').getall(),  # Adjust this selector if needed
        }
