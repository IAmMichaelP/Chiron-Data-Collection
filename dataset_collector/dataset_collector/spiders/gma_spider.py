from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest


class CrawlingSpider(CrawlSpider):
    name = "gmaCrawler"

    # Lua script for Splash to scroll and wait for lazy-loaded content
    lua_script = """
    function main(splash, args)
      splash.private_mode_enabled = false  -- Disable private mode for better performance
      splash:set_viewport_full()  -- Set viewport to full page to handle dynamic content better
      splash:go(args.url)
      splash:wait(5)  -- Wait for the initial page load

      -- Simulate scrolling to the bottom multiple times
      for i = 1, args.scroll_depth do
        splash:runjs("window.scrollTo(0, document.body.scrollHeight);")
        splash:wait(2)  -- Increase wait time for lazy-loaded content
      end

      return {
        html = splash:html(),  -- Return the rendered HTML after scrolling
      }
    end
    """

    def start_requests(self):
        url = 'https://www.gmanetwork.com/news/archives/lifestyle-healthandwellness/'
        # Send a SplashRequest with the Lua script to scroll and load content
        print('first request')
        yield SplashRequest(
            url=url,
            callback=self.parse,
            endpoint='execute',
            args={'lua_source': self.lua_script, 'timeout': 90, 'resource_timeout': 20, 'scroll_depth': 20},
            meta={'scraped_links': set(), 'scroll_count': 1}  # Track scraped links and scroll count
        )

    def parse(self, response):
        print("secondary request")
        # Extract article links and titles
        scraped_links = response.meta['scraped_links']  # Get previously scraped links
        scroll_count = response.meta['scroll_count']  # Get scroll count

        new_links = response.css('.story_link::attr(href)').getall()
        titles = response.css('.story_link::attr(title)').getall()

        has_new_content = False
        # Yield only new links that haven't been scraped yet
        for link, title in zip(new_links, titles):
            if link not in scraped_links:
                title = title.replace('\n', '').replace('\t', '').strip()
                scraped_links.add(link)  # Add to scraped links
                has_new_content = True
                yield {
                    'link': link,
                    'title': title
                }
        # Continue scrolling if there is new content
        if has_new_content:
            scroll_count += 1
            yield SplashRequest(
                url=response.url,
                callback=self.parse,
                endpoint='execute',
                args={'lua_source': self.lua_script, 'timeout': 90, 'resource_timeout': 20, 'scroll_depth': 20},
                meta={'scraped_links': scraped_links, 'scroll_count': scroll_count},
                dont_filter=True  # Avoid filtering duplicate requests
            )
        else:
            print(f"Stopped after {scroll_count} scrolls. No new content found.")
