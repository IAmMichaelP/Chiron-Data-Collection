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
#             'title': response.css('.subsection::text').get(),
#             # 'body': response.css('.story_main p::text').getall(),
#         }

#  ---------------------------- fetch('http://localhost:8050/render.html?url=https://www.gmanetwork.com/news/lifestyle/healthandwellness/922501/phasing-out-teen-smoking-could-save-1-2-million-lives-who-cancer-agency-study/story/')
# fetch('http://localhost:8050/render.html?url=https://www.gmanetwork.com/news/archives/lifestyle-healthandwellness/')
# class CrawlingSpider(CrawlSpider):
#     name = "chironCrawler"

#     def start_requests(self):
#         url = 'https://www.gmanetwork.com/news/archives/lifestyle-healthandwellness/'
#         yield SplashRequest(url=url, callback=self.parse, args={'wait': 8})  # Increase wait time
    
#     def parse(self, response):
#         yield {
#             'title': response.css('.story_link::attr(href)').getall(),
#             # 'body': response.css('.story_main p::text').getall(),
#         }



class CrawlingSpider(CrawlSpider):
    name = "gmaCrawler"

    # Lua script for Splash to scroll and wait for lazy-loaded content
    lua_script = """
    function main(splash, args)
      splash.private_mode_enabled = false  -- Disable private mode for better page performance
      splash:set_viewport_full()  -- Set viewport to full page to handle dynamic content better
      splash:go(args.url)
      splash:wait(5)  -- Wait for the initial page load
      
      -- Simulate scrolling to the bottom multiple times
      for i = 1, 20 do
        splash:runjs("window.scrollTo(0, document.body.scrollHeight);")
        splash:wait(2)  -- Increase wait time for lazy-loaded content
      end

      return {
        html = splash:html(),  -- Return the rendered HTML after scrolling
      }
    end
    """

    def start_requests(self):
        url = 'https://www.gmanetwork.com/news/archives/lifestyle-healthandwellness/'
        # Send a SplashRequest with the Lua script to scroll and load content
        yield SplashRequest(
            url=url, 
            callback=self.parse, 
            endpoint='execute',  # Execute the Lua script
            args={'lua_source': self.lua_script, 'timeout': 90, 'resource_timeout': 20}
        )

    def parse(self, response):
        # Extract article links and titles
        yield {
            'link': response.css('.story_link::attr(href)').getall(),
            'title': response.css('.story_link::attr(title)').getall(),
        }
