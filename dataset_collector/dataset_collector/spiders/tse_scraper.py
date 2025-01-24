import pandas as pd
from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest
import time
import random  # To randomly pick a proxy from the list

# Step 1: Read the CSV file using pandas
df = pd.read_csv(r"C:\xampp\htdocs\GitHub\Chiron\dataset_collector\TSE.csv")
print(df.head(10))

# # Proxy list
# PROXY_LIST = [
#     '54.248.238.110:80',
#     '52.196.1.182:80',
#     '35.72.118.126:80',
#     '13.38.176.104:3128',
#     '5.9.238.29:80',
#     # Add as many proxies as needed...
# ]

# def get_random_proxy():
#     """Pick a random proxy from the proxy list."""
#     return random.choice(PROXY_LIST)

class CrawlingSpider(CrawlSpider):
    name = "tseScraper"

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
            # proxy = get_random_proxy()  # Get a random proxy for each request
            time.sleep(2)

            yield SplashRequest(
                url=url,
                callback=self.parse,
                endpoint='execute',
                args={'lua_source': self.lua_script, 'timeout': 90, 'resource_timeout': 20},
                # splash_headers={'proxy': f'http://{proxy}'},  # Pass the proxy to Splash
                meta={'index': index, 'title': row['title']}  # Pass the index and title to the next step
            )

    # Step 3: Define the parse method to scrape the content
    def parse(self, response):
        # Scrape content from the page
        content = response.css('#post-body p::text').getall()
        content = ''.join(content).strip()

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
        df.to_csv('dataset3.csv', index=False)
