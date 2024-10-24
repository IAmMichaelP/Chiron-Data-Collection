# This is both a scraper for Philippine Inquirer Health and Wellness News Dataset.

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest


class CrawlingSpider(CrawlSpider):
    name = "pICrawler"

    # Lua script for Splash to scroll and wait for lazy-loaded content
    lua_script = """
    function main(splash, args)
      splash.private_mode_enabled = false  -- Disable private mode for better page performance
      splash:set_viewport_full()  -- Set viewport to full page to handle dynamic content better
      splash:go(args.url)
      splash:wait(5)  -- Wait for the initial page load
      
      -- Simulate scrolling to the bottom multiple times
      for i = 1, 30 do
        splash:runjs("window.scrollTo(0, document.body.scrollHeight);")
        splash:wait(2)  -- Increase wait time for lazy-loaded content
      end

      return {
        html = splash:html(),  -- Return the rendered HTML after scrolling
      }
    end
    """

    def start_requests(self):
        url = 'https://lifestyle.inquirer.net/category/latest-stories/wellness/'
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
            'link': response.css('.elementor-post__thumbnail__link::attr(href)').getall(),
            'title': response.css('.elementor-post__title a::text').getall(),
        }
