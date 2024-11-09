from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest

class CrawlingSpider(CrawlSpider):
    name = "businessmirrorCrawler"

    # Lua script for Splash to scroll, click pagination and wait for lazy-loaded content
    lua_script = """
    function main(splash, args)
      splash.private_mode_enabled = false  -- Disable private mode for better page performance
      splash:set_viewport_full()  -- Set viewport to full page to handle dynamic content better
      splash:go(args.url)
      splash:wait(5)  -- Wait for the initial page load

      -- Simulate scrolling to the bottom multiple times for lazy-loaded content
      for i = 1, 3 do
        splash:runjs("window.scrollTo(0, document.body.scrollHeight);")
        splash:wait(5)  -- Increase wait time for lazy-loaded content
      end

      -- Simulate clicking the pagination button (if exists)
      local has_next_page = splash:evaljs("document.querySelector('.next.page-numbers') !== null")
      if has_next_page then
        splash:runjs("document.querySelector('.next.page-numbers').click();")
        splash:wait(5)  -- Wait for the new page to load
      end

      return {
        html = splash:html(),  -- Return the rendered HTML after clicking pagination
        url = splash:url(),
      }
    end
    """

    def start_requests(self):
        url = 'https://businessmirror.com.ph/features/healthandfitness/'
        # Send a SplashRequest with the Lua script to scroll, click pagination and load content
        yield SplashRequest(
            url=url,
            callback=self.parse,
            endpoint='execute',  # Execute the Lua script
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

        # Check if there is another page to crawl
        has_next_page = response.css('.next.page-numbers')
        if has_next_page:
            next_page_url = response.urljoin(has_next_page.attrib['href'])
            yield SplashRequest(
                url=next_page_url,
                callback=self.parse,
                endpoint='execute',
                args={'lua_source': self.lua_script, 'timeout': 90, 'resource_timeout': 20},
                meta={'scraped_links': scraped_links},  # Pass the updated scraped links
                dont_filter=True  # Avoid filtering the same URL
            )
# fetch('http://localhost:8050/render.html?url=https://news.abs-cbn.com/lifestyle/health-wellness')
