
import pandas as pd
from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest
import time
import random
import re

# Step 1: Read the CSV file using pandas
df = pd.read_csv(r"C:\Users\agaro\Documents\GitHub\Chiron\dataset_collector\naturalnews_updated.csv")
df = df.iloc[500:1000]
print(df.head(10))

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
    name = "naturalnewsScraper"

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
        for index, row in df.iterrows():
            url = row['link']  # Get the URL for each row
            proxy = get_random_proxy()  # Get a random proxy for each request
            time.sleep(2)
            yield SplashRequest(
                url=url,
                callback=self.parse,
                endpoint='execute',
                args={'lua_source': self.lua_script, 'timeout': 90, 'resource_timeout': 20},
                splash_headers={'proxy': f'http://{proxy}'},  # Pass the proxy to Splash
                meta={'index': index, 'title': row['title']}  # Pass the index and title to the next step
            )

    # Step 3: Define the parse method to scrape the content
    def parse(self, response):
        # Scrape content from the page
        # Extract article links and titles
        
        content = response.css('div#Article *::text').getall()
        content = ' '.join(content)
        content = re.sub(r'\s+', ' ', content).strip()
        content = content.split('Sources for this article include')[0]

        # Get the index and title from the meta information passed
        index = response.meta['index']
        title = response.meta['title']

        # Step 4: Append the scraped content to the corresponding row in the DataFrame
        df.at[index, 'content'] = content  # Add the scraped content to the DataFrame

        # Optionally, print or log the progress
        print(f"Scraped content for: {title}")

    # Step 5: Define the method to write the results to CSV after scraping is done
    def closed(self, reason):
        # Write the updated DataFrame with content to a new CSV file
        # df.to_csv('dataset3.csv', index=False)
        df.to_csv('dataset3.csv', mode='a', index=False, header=False)
