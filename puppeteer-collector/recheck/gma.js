const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");
const csvWriter = require("csv-writer").createObjectCsvWriter;

(async () => {
    let browser;
    try {
        browser = await puppeteer.launch({ headless: false, slowMo: 0 }); // Set headless: true for faster execution
        const page = await browser.newPage();
        await page.goto('https://www.gmanetwork.com/news/archives/lifestyle-healthandwellness/', { waitUntil: 'networkidle2' });

        const articleSelector = '.story'; // Selector for each article block
        const titleSelector = '.story_link.story'; // Selector for the title
        // const authorSelector = 'span._author_1l3h4_57'; // Selector for the author
        // const dateSelector = 'span._date_1l3h4_65'; // Selector for the date

        let results = [];
        let uniqueLinks = new Set(); // To track unique articles

        // Function to scroll down the page
        const scrollDown = async () => {
            await page.evaluate(() => {
                window.scrollBy(0, window.innerHeight); // Scroll down by one viewport height
            });
            await new Promise(resolve => setTimeout(resolve, 1000)); // Wait for new content to load
        };

        // Scroll and scrape multiple times
        const scrollCount = 50; // Number of times to scroll down
        for (let i = 0; i < scrollCount; i++) {
            console.log(`Scrolling ${i + 1}/${scrollCount}...`);
            await scrollDown();

            // Extract articles after each scroll
            const articles = await page.evaluate((articleSelector, titleSelector) => {
                return Array.from(document.querySelectorAll(articleSelector)).map(article => {
                    const linkElement = article.querySelector(titleSelector);
                    const link = linkElement ? `${linkElement.href}` : null; // Construct full URL
                    const title = linkElement ? linkElement.title.trim() : "No Title";
                    console.log(`"${title}" → ${link}`);
                    return { link, title };
                });
            }, articleSelector, titleSelector);

            // Add new articles to results, avoiding duplicates
            articles.forEach(article => {
                if (article.link && article.title && !uniqueLinks.has(article.link)) {
                    console.log(`"${article.title}" → ${article.link}`);
                    results.push(article);
                    uniqueLinks.add(article.link);
                }
            });

            console.log(`Articles found so far: ${results.length}`);
        }

        // Save results to CSV
        const csvPath = path.join(__dirname, "scraped_data.csv");
        const writer = csvWriter({
            path: csvPath,
            header: [
                { id: "link", title: "link" },
                { id: "title", title: "title" },
            ]
        });

        await writer.writeRecords(results);
        console.log(`Scraping complete. Data saved to ${csvPath}`);
    } catch (error) {
        console.error("An error occurred:", error);
    } finally {
        if (browser) await browser.close();
    }
})();
