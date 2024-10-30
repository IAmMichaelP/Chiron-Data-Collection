# from scrapy.spiders import CrawlSpider
# from scrapy_splash import SplashRequest

# class CrawlingSpider(CrawlSpider):
#     name = "absCbnCrawler"

#     # Lua script for Splash to scroll, click pagination and wait for lazy-loaded content
#     lua_script = """
#     function main(splash, args)
#       splash.private_mode_enabled = false  -- Disable private mode for better page performance
#       splash:set_viewport_full()  -- Set viewport to full page to handle dynamic content better
#       splash:go(args.url)
#       splash:wait(5)  -- Wait for the initial page load

#       -- Simulate scrolling to the bottom multiple times for lazy-loaded content
#       for i = 1, 3 do
#         splash:runjs("window.scrollTo(0, document.body.scrollHeight);")
#         splash:wait(5)  -- Increase wait time for lazy-loaded content
#       end

#       -- Simulate clicking the pagination button (if exists)
#       local has_next_page = splash:evaljs("document.querySelector('.css-16g1r8o') !== null")
#       if has_next_page then
#         splash:runjs("document.querySelector('.pagination-next-class').click();")
#         splash:wait(5)  -- Wait for the new page to load
#       end

#       return {
#         html = splash:html(),  -- Return the rendered HTML after clicking pagination
#         url = splash:url(),
#       }
#     end
#     """

#     def start_requests(self):
#         url = 'https://news.abs-cbn.com/lifestyle/health-wellness'
#         # Send a SplashRequest with the Lua script to scroll, click pagination and load content
#         yield SplashRequest(
#             url=url,
#             callback=self.parse,
#             endpoint='execute',  # Execute the Lua script
#             args={'lua_source': self.lua_script, 'timeout': 90, 'resource_timeout': 20}
#         )

#     def parse(self, response):
#         # Extract article links and titles
#         yield {
#             'link': response.css('.css-cs6pc5::attr(href)').getall(),
#             'title': response.css('.css-izavx0::text').getall(),
#         }

#         # Check if there is another page to crawl
#         has_next_page = response.css('.css-16g1r8o')
#         if has_next_page:
#             next_page_url = response.urljoin(has_next_page.attrib['href'])
#             yield SplashRequest(
#                 url=next_page_url,
#                 callback=self.parse,
#                 endpoint='execute',
#                 args={'lua_source': self.lua_script, 'timeout': 90, 'resource_timeout': 20}
#             )
# fetch('http://localhost:8050/render.html?url=https://news.abs-cbn.com/lifestyle/health-wellness')

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest
from scrapy.utils.request import fingerprint

# For example, in a spider that relies on fingerprinting, change request_fingerprint to fingerprint
# Example usage


class CrawlingSpider(CrawlSpider):
    name = "absCbnCrawler"

    lua_script = """
    function main(splash, args)
      splash.private_mode_enabled = false
      splash:set_viewport_full()
      splash:go(args.url)
      splash:wait(5)

      -- Scroll for lazy-loaded content
      for i = 1, 3 do
        splash:runjs("window.scrollTo(0, document.body.scrollHeight);")
        splash:wait(5)
      end

      -- Click on pagination button if it exists
      local has_next_page = splash:evaljs("document.querySelector('.pagination-next-class') !== null")
      if has_next_page then
        splash:runjs("document.querySelector('.css-16g1r8o').click();")
        splash:wait(5)
      end

      return {
        html = splash:html(),
        url = splash:url(),
      }
    end
    """

    allowed_domains = ["abs-cbn.com", "localhost"]
    start_urls = ["https://news.abs-cbn.com/lifestyle/health-wellness"]

    # Define rules to follow links and parse them
    rules = (
        Rule(
            LinkExtractor(allow="/lifestyle/health-wellness/"),
            callback="parse_item",
            follow=True
        ),
    )

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(
                url=url,
                callback=self.parse_start_page,
                endpoint='execute',
                args={'lua_source': self.lua_script, 'timeout': 90, 'resource_timeout': 20}
            )

    def parse_start_page(self, response):
        # Process the response and follow links using Scrapy's rules
        for link in LinkExtractor(allow="/lifestyle/health-wellness/").extract_links(response):
            yield SplashRequest(
                url=link.url,
                callback=self.parse_item,
                endpoint='execute',
                args={'lua_source': self.lua_script, 'timeout': 90, 'resource_timeout': 20}
            )

    def parse_item(self, response):
        # Extract article links and titles
        yield {
            'title': response.css('h1::text').get(),
            'link': response.url,
            'content': response.css('.body').get()
        }
