from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest
import time
import random

# Proxy list
PROXY_LIST = [
    '52.196.1.182:80',
    '43.201.121.81:80',
    '44.195.247.145:80',
    '13.38.176.104:3128',
    '44.219.175.186:80',
    '18.185.169.150:3128',
    '18.228.149.161:80',
    '3.212.148.199:80',
    '3.78.92.159:3128'
]

def get_random_proxy():
    """Pick a random proxy from the proxy list."""
    return random.choice(PROXY_LIST)

class CrawlingSpider(CrawlSpider):
    name = "naturalnewsCrawler"

    lua_script = """
    function main(splash, args)
      splash.private_mode_enabled = false
      splash:set_viewport_full()
      splash:go(args.url)
      splash:wait(5)

      -- Scroll to the bottom for lazy-loaded content
      splash:runjs("window.scrollTo(0, document.body.scrollHeight);")
      splash:wait(5)

      return {
        html = splash:html(),
        url = splash:url(),
      }
    end
    """

    def start_requests(self):
        # Start crawling from the first page
        initial_url = 'https://naturalnews.com/category/health/page/2/'
        proxy = get_random_proxy()  # Get a random proxy for each request
        time.sleep(2)

        yield SplashRequest(
            url=initial_url,
            callback=self.parse,
            endpoint='execute',
            args={'lua_source': self.lua_script, 'timeout': 90, 'resource_timeout': 20},
            splash_headers={'proxy': f'http://{proxy}'},  # Pass the proxy to Splash
            meta={'page': 2, 'scraped_links': set()}  # Track current page and scraped links
        )

    def parse(self, response):
        scraped_links = response.meta['scraped_links']
        current_page = response.meta['page']  # Get the current page number

        # Scrape links and titles
        new_links = response.css('.Headline a::attr(href)').getall()
        titles = response.css('.Headline a::text').getall()

        # Yield only new links that haven't been scraped yet
        for link, title in zip(new_links, titles):
            if link not in scraped_links:
                scraped_links.add(link)
                yield {
                    'link': link,
                    'title': title
                }

        # Increment the page number for the next request
        next_page = current_page + 1
        next_page_url = f'https://naturalnews.com/category/health/page/{next_page}/'

        # Check if there is still a next page by looking for the next page URL
        if len(new_links) > 0:  # This assumes the presence of new links indicates the next page exists
            proxy = get_random_proxy()
            yield SplashRequest(
                url=next_page_url,
                callback=self.parse,
                endpoint='execute',
                args={'lua_source': self.lua_script, 'timeout': 90, 'resource_timeout': 20},
                splash_headers={'proxy': f'http://{proxy}'},  # Rotate the proxy for each request
                meta={'page': next_page, 'scraped_links': scraped_links},  # Pass the updated page and links
                dont_filter=True  # Avoid filtering the same URL
            )

# fetch('http://localhost:8050/render.html?url=https://naturalnews.com/category/health/')
