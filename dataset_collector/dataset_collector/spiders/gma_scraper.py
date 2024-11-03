
import pandas as pd
from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest
import time

# Step 1: Read the CSV file using pandas
df = pd.read_csv(r"C:\xampp\htdocs\GitHub\Chiron\dataset_collector\chopped_dataset.csv")
print(df.head(10))

class CrawlingSpider(CrawlSpider):
    name = "gmaScraper"

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
            time.sleep(2)
            yield SplashRequest(
                url=url,
                callback=self.parse,
                endpoint='execute',
                args={'lua_source': self.lua_script, 'timeout': 90, 'resource_timeout': 20},
                meta={'index': index, 'title': row['title']}  # Pass the index and title to the next step
            )

    # Step 3: Define the parse method to scrape the content
    def parse(self, response):
        # Scrape content from the page
        # Extract article links and titles
        
        headline = response.css('h1.story_links::text').getall()
        content = response.css('.story_main p::text').getall()
        content = ''.join(content)
        content = f"{headline} {content}"
        

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
        df.to_csv('dataset1.csv', index=False)
