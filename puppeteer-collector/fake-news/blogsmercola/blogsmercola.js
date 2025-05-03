const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");
const csvWriter = require("csv-write-stream");

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

(async () => {
    const MAX_CLICKS = 5; // Set how many times to click "Load more Blogs"

    let browser;
    try {
        browser = await puppeteer.launch({ headless: false, slowMo: 0 });
        const page = await browser.newPage();
        await page.goto('https://blogs.mercola.com/', { waitUntil: 'networkidle2' });

        const articleSelector = '.article-list';
        const loadMoreButtonSelector = '#BtnLoadMore';

        let results = [];
        let uniqueLinks = new Set();

        // Click the button a fixed number of times
        for (let i = 0; i < MAX_CLICKS; i++) {
            const loadMoreButton = await page.$(loadMoreButtonSelector);
            if (!loadMoreButton) {
                console.log("No more 'Load more Blogs' button found.");
                break;
            }

            console.log(`Clicking 'Load more Blogs' (${i + 1}/${MAX_CLICKS})...`);
            await loadMoreButton.click();
            await sleep(2000); // Wait for new content to load (adjust if needed)
        }

        // Extract all article data
        const articles = await page.evaluate(() => {
            const articleNodes = document.querySelectorAll('.article-list');
            return Array.from(articleNodes).map(article => {
                const titleAnchor = article.querySelector('h2 a');
                const title = titleAnchor?.innerText.trim() || null;
                const link = titleAnchor?.href || null;
                const spans = article.querySelectorAll('div.article-desc span');
                const date = spans[0]?.innerText.trim() || null;
                return { title, link, date };
            });
        });

        const validArticles = articles.filter(a => a.title && a.link);
        validArticles.forEach(article => {
            if (!uniqueLinks.has(article.link)) {
                results.push(article);
                uniqueLinks.add(article.link);
            }
        });

        // Save to CSV
        const csvPath = path.join(__dirname, "scraped_data.csv");
        const writer = csvWriter({ headers: ["title", "link", "date"] });
        writer.pipe(fs.createWriteStream(csvPath));
        results.forEach(result => writer.write(result));
        writer.end();

        console.log(`Scraped ${results.length} articles. Data saved to ${csvPath}`);
    } catch (error) {
        console.error("An error occurred:", error);
    } finally {
        if (browser) await browser.close();
    }
})();
