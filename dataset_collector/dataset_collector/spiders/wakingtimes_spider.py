from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest

class CrawlingSpider(CrawlSpider):
    name = "wakingtimesCrawler"

    lua_script = """
    function main(splash, args)
      splash.private_mode_enabled = false  -- Disable private mode for better performance
      splash:set_viewport_full()  -- Set viewport to full page to capture all content
      splash:go(args.url)
      splash:wait(5)  -- Wait for the page to load

      -- Simulate scrolling to load more content and click "Load More"
      for i = 1, 5 do
        splash:runjs("window.scrollTo(0, document.body.scrollHeight);")
        splash:wait(5)  -- Wait for new content to load
        local load_more = splash:evaljs("document.querySelector('.ctis-load-more button')")
        if load_more then
          splash:runjs("document.querySelector('.ctis-load-more button').click();")
          splash:wait(2)  -- Wait for more articles to load
        else
          break  -- No more content to load
        end
      end

      return {
        html = splash:html(),
        url = splash:url(),
      }
    end
    """

    def start_requests(self):
        url = 'https://www.wakingtimes.com/category/conscious-body/'
        yield SplashRequest(
            url=url,
            callback=self.parse,
            endpoint='execute',
            args={'lua_source': self.lua_script, 'timeout': 90, 'resource_timeout': 20},
            meta={'scraped_links': set()}  # Track scraped links to avoid duplicates
        )

    def parse(self, response):
        scraped_links = response.meta['scraped_links']  # Get previously scraped links
        new_links = response.css('.entry-title a::attr(href)').getall()
        titles = response.css('.entry-title a::text').getall()

        # Yield only new links that haven't been scraped yet
        for link, title in zip(new_links, titles):
            if link not in scraped_links:
                scraped_links.add(link)  # Add to scraped links
                yield {
                    'link': link,
                    'title': title
                }

        # Find the "Load More" button's data-url attribute and use it for the next page
        load_more_button = response.css('.ctis-load-more button').get()
        if load_more_button:
            next_page_url = response.urljoin(load_more_button)  # Get the next page URL
            yield SplashRequest(
                url=next_page_url,
                callback=self.parse,
                endpoint='execute',
                args={'lua_source': self.lua_script, 'timeout': 90, 'resource_timeout': 20},
                meta={'scraped_links': scraped_links},  # Pass the updated scraped links
                dont_filter=True  # Avoid filtering the same URL
            )

# fetch('http://localhost:8050/render.html?url=https://www.wakingtimes.com/category/conscious-body/')