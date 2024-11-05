
import pandas as pd
from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest
import time

# Step 1: Read the CSV file using pandas
# df = pd.read_csv(r"C:\xampp\htdocs\GitHub\Chiron\dataset_collector\dataset1.csv")
# print(df.head(10))
# print("Number of rows in final dataframe:", len(df))
df = pd.read_csv(r"C:\xampp\htdocs\GitHub\Chiron\dataset_collector\gma_new.csv")

class CrawlingSpider(CrawlSpider):
    name = "testScraper"

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

        url = df['link']  # Get the URL for each row
        url = url[0]

        yield SplashRequest(
            url=url,
            callback=self.parse,
            endpoint='execute',
            args={'lua_source': self.lua_script, 'timeout': 90, 'resource_timeout': 20},
        )

    # Step 3: Define the parse method to scrape the content
    def parse(self, response):
        # Scrape content from the page
        # Extract article links and titles
        
        headline = response.css('h1::text').getall()
        content = response.css('p::text').getall()
        yield {
            'headline': headline,
            'content': content,
        }


# fetch('http://localhost:8050/render.html?url=https://www.gmanetwork.com/news/lifestyle/healthandwellness/925712/iya-villania-s-no-1-tip-on-how-to-raise-four-kids-and-carry-a-fifth-be-fit-and-healthy/story/')fetch('http://localhost:8050/render.html?url=https://www.gmanetwork.com/news/lifestyle/healthandwellness/925712/iya-villania-s-no-1-tip-on-how-to-raise-four-kids-and-carry-a-fifth-be-fit-and-healthy/story/')

# fetch('http://localhost:8050/render.html?url=https://www.gmanetwork.com/news/archives/lifestyle-healthandwellness/')