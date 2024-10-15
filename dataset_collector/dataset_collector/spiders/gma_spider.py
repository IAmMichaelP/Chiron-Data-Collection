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

    # Lua script to scroll to the bottom of the page
    lua_script = """
    function main(splash, args)
        splash:go(args.url)
        splash:wait(2)  -- Wait for the page to load

        -- Scroll to the bottom of the page in steps
        local scroll_to_bottom = splash:jsfunc([[
            function () {
                window.scrollTo(0, document.body.scrollHeight);
            }
        ]])

        -- Scroll multiple times to ensure the page is fully loaded
        local max_scrolls = 10
        for i = 1, max_scrolls do
            scroll_to_bottom()
            splash:wait(2)  -- Adjust the wait time for your page
        end

        return {
            html = splash:html(),
            url = splash:url(),
        }
    end
    """

    def start_requests(self):
        url = 'https://www.gmanetwork.com/news/archives/lifestyle-healthandwellness/'
        yield SplashRequest(url=url, callback=self.parse, args={'wait': 8})  # Increase wait time
    
    def parse(self, response):
        yield {
            'link': response.css('.story_link::attr(href)').getall(),
            'title': response.css('.story_link::attr(title)').getall(),
        }