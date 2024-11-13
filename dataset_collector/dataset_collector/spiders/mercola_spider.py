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

class MercolaCrawler(CrawlSpider):
    name = "mercolaCrawler"

    lua_script = """
    function main(splash, args)
      splash.private_mode_enabled = false
      splash:set_viewport_full()
      splash:go(args.url)
      splash:wait(3)

      -- Simulate selecting the month and year
      local month_dropdown = splash:select('select[name="ctl00$ctl00$ctl00$bcr$bcr$bcr$ddlMonth"]')
      local year_dropdown = splash:select('select[name="ctl00$ctl00$ctl00$bcr$bcr$bcr$ddlYear"]')
      
      month_dropdown:select(args.month)  -- Select the month
      year_dropdown:select(args.year)    -- Select the year
      splash:wait(1)  -- Wait for the dropdown selections to take effect

      -- Simulate clicking the 'Previous Month' button
      local submit_button = splash:select('input[type="submit"][name="ctl00$ctl00$ctl00$bcr$bcr$bcr$btnPrevious"]')
      submit_button:click()
      splash:wait(5)

      return {
        html = splash:html(),
        url = splash:url(),
      }
    end
    """

    def start_requests(self):
        url = 'https://articles.mercola.com/sites/newsletter/newsletter-archive.aspx'
        initial_month = "11"  # November
        initial_year = "2024"
        proxy = get_random_proxy()  # Get a random proxy for each request
        
        yield SplashRequest(
            url=url,
            callback=self.parse,
            endpoint='execute',
            args={'lua_source': self.lua_script, 'month': initial_month, 'year': initial_year, 'timeout': 90, 'resource_timeout': 20},
            splash_headers={'proxy': f'http://{proxy}'},  # Pass the proxy to Splash
            meta={'scraped_links': set(), 'month': initial_month, 'year': initial_year}
        )

    def parse(self, response):
        scraped_links = response.meta['scraped_links']
        month = response.meta['month']
        year = response.meta['year']

        # Scrape links and titles
        new_links = response.css('.current-desc a::attr(href)').getall()
        titles = response.css('.current-desc a span::text').getall()

        # Yield only new links that haven't been scraped yet
        for link, title in zip(new_links, titles):
            if link not in scraped_links:
                scraped_links.add(link)
                yield {
                    'link': link,
                    'title': title
                }

        # Handle form submission for previous months
        # Reduce the month number or change the year if month goes below 1
        next_month = int(month) - 1
        if next_month < 1:
            next_month = 12
            next_year = str(int(year) - 1)
        else:
            next_year = year

        # Only continue if the year is within a valid range
        if int(next_year) >= 2008:  # Assuming the site has content from 2008 onwards
            yield SplashRequest(
                url=response.url,
                callback=self.parse,
                endpoint='execute',
                args={'lua_source': self.lua_script, 'month': str(next_month), 'year': next_year, 'timeout': 90, 'resource_timeout': 20},
                meta={'scraped_links': scraped_links, 'month': str(next_month), 'year': next_year},
                dont_filter=True
            )


# fetch('http://localhost:8050/render.html?url=https://articles.mercola.com/sites/newsletter/newsletter-archive.aspx')