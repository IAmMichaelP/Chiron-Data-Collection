const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");
const csvWriter = require("csv-writer").createObjectCsvWriter;

(async () => {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    await page.setViewport({ width: 1200, height: 800 });

    await page.goto('https://www.foodmatters.com/articles', {
        waitUntil: 'networkidle2',
        timeout: 60000
    });

    const articleSelector = '.row.row-gutter--lg';
    const loadMoreSelector = '.endless_more';

    let results = [];
    const seenLinks = new Set();
    const maxIterations = 100;

    for (let i = 0; i < maxIterations; i++) {
        try {
            console.log(`Iteration ${i + 1}...`);
            await page.waitForSelector(articleSelector, { timeout: 10000 });

            const newArticles = await page.evaluate((articleSelector) => {
                return Array.from(document.querySelectorAll(articleSelector)).map(row => {
                    const linkEl = row.querySelector("a.list-item--link");
                    const titleEl = row.querySelector("h3.list-item--heading");
                    const authorEl = row.querySelector(".article-stats a");

                    const link = linkEl ? "https://www.foodmatters.com" + linkEl.getAttribute("href") : null;
                    const title = titleEl ? titleEl.innerText.trim() : null;
                    const author = authorEl ? authorEl.innerText.trim() : "Unknown";

                    return { link, title, author };
                });
            }, articleSelector);

            const filtered = newArticles.filter(article =>
                article.link && article.title && !seenLinks.has(article.link)
            );

            filtered.forEach(article => {
                seenLinks.add(article.link);
                results.push(article);
                console.log(`Added: ${article.title}`);
            });

            const loadMoreButton = await page.$(loadMoreSelector);
            if (loadMoreButton) {
                await page.evaluate(el => el.scrollIntoView(), loadMoreButton);
                await loadMoreButton.click();
                console.log("Clicked 'Show More Articles'");
                await new Promise(resolve => setTimeout(resolve, 2000));
            } else {
                console.log("No more articles to load.");
                break;
            }

        } catch (err) {
            console.error(`Error during iteration ${i + 1}: ${err.message}`);
            await page.screenshot({ path: `error-${i + 1}.png` });
            break;
        }
    }

    const csvPath = path.join(__dirname, "scraped_data.csv");
    const writer = csvWriter({
        path: csvPath,
        header: [
            { id: "link", title: "Link" },
            { id: "title", title: "Title" },
            { id: "author", title: "Author" }
        ]
    });

    await writer.writeRecords(results);
    console.log(`✅ Scraped ${results.length} articles.`);
    await browser.close();
})();
