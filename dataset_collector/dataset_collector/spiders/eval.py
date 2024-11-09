
import pandas as pd
from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest
import time

# Step 1: Read the CSV file using pandas
# df = pd.read_csv(r"C:\xampp\htdocs\GitHub\Chiron\dataset_collector\dataset1.csv")
# print(df.head(10))
# print("Number of rows in final dataframe:", len(df))
import random  # To randomly pick a proxy from the list

# Step 1: Read the CSV file using pandas
df = pd.read_csv(r"C:\xampp\htdocs\GitHub\Chiron\dataset_collector\TSE.csv")
print(df.head(10))

# Proxy list
PROXY_LIST = [
    '54.248.238.110:80',
    '52.196.1.182:80',
    '35.72.118.126:80',
    '13.38.176.104:3128',
    '5.9.238.29:80',
    # Add as many proxies as needed...
]

def get_random_proxy():
    """Pick a random proxy from the proxy list."""
    return random.choice(PROXY_LIST)

class CrawlingSpider(CrawlSpider):
    name = "evalScraper"

    # Lua script for Splash to scroll and wait for lazy-loaded content
    lua_script = """
    function main(splash, args)
      splash.private_mode_enabled = false  -- Disable private mode for better performance
      splash:set_viewport_full()  -- Set viewport to full page to handle dynamic content better
      splash:go(args.url)
      splash:wait(2)  -- Wait for the initial page load
      
      return {
        html = splash:html(),  -- Return the rendered HTML after scrolling
      }
    end
    """

    # Step 2: Define the start_requests method to iterate over links
    def start_requests(self):

        # url = df['link']  # Get the URL for each row
        url = 'https://www.eaglenews.ph/zimbabwe-reports-first-two-mpox-cases-of-unspecified-variant/'
        proxy = get_random_proxy()  # Get a random proxy for each request
        yield SplashRequest(
            url=url,
            callback=self.parse,
            endpoint='execute',
            args={'lua_source': self.lua_script, 'timeout': 90, 'resource_timeout': 20},
            splash_headers={'proxy': f'http://{proxy}'},  # Pass the proxy to Splash
            
        )

    # Step 3: Define the parse method to scrape the content
    def parse(self, response):
        content = response.css('.entry-content p::text').getall()
        content = ''.join(content).strip()
        yield {
            'title': content,
        }




# fetch('http://localhost:8050/render.html?url=https://www.gmanetwork.com/news/lifestyle/healthandwellness/925712/iya-villania-s-no-1-tip-on-how-to-raise-four-kids-and-carry-a-fifth-be-fit-and-healthy/story/')

# fetch('http://localhost:8050/render.html?url=https://www.gmanetwork.com/news/archives/lifestyle-healthandwellness/')
# fetch('http://localhost:8050/render.html?url=https://www.thesummitexpress.com/2024/10/miracle-doc-willie-ong-cancer-shrank-60-percent.html')
# fetch('http://localhost:8050/render.html?url=https://books.toscrape.com/catalogue/category/books_1/index.html')