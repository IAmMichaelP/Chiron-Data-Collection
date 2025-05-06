const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");
const csvWriter = require("csv-writer").createObjectCsvWriter;

(async () => {
    const browser = await puppeteer.launch({ headless: false, slowMo: 0 });
    const page = await browser.newPage();
    await page.goto('https://www.abc.net.au/news/sport', { waitUntil: 'networkidle2' });

    const articleSelector = '.DetailCard_card__oooSN';
    const titleSelector = '.DetailCard_link__qM1Oi';

    const loadMoreSelector = 'button[data-component="PaginationLoadMoreButton"]';

    let results = [];
    const maxIterations = 3;
    const seenLinks = new Set();

    for (let i = 0; i < maxIterations; i++) {
        try {
            await page.waitForSelector(articleSelector, { timeout: 5000 });

            const newArticles = await page.evaluate((articleSelector, titleSelector) => {
                return Array.from(document.querySelectorAll(articleSelector)).map(article => {
                    const linkElement = article.querySelector(titleSelector);
                    const link = linkElement ? linkElement.href : null;
                    const title = linkElement ? linkElement.innerText.trim() : null;
                    return { link, title };
                });
            }, articleSelector, titleSelector);

            const filtered = newArticles.filter(article =>
                article.link &&
                article.title &&
                article.title !== "No Title" &&
                !seenLinks.has(article.link)
            );

            filtered.forEach(article => {
                console.log(`Parsed: ${article.title} - ${article.link}`);
                seenLinks.add(article.link);
                results.push(article);
            });

            const loadMoreButton = await page.$(loadMoreSelector);
            if (loadMoreButton) {
                await Promise.all([
                    page.waitForResponse(res => res.url().includes("pagination") && res.status() === 200),
                    loadMoreButton.click(),
                ]);
                await new Promise(resolve => setTimeout(resolve, 3000));

            } else {
                console.log("No more 'Load more stories' button found.");
                break;
            }

        } catch (err) {
            console.error(`Error on iteration ${i + 1}:`, err);
            break;
        }
    }

    // Save to CSV with append mode
    const csvPath = path.join(__dirname, "scraped_data.csv");
    const writer = csvWriter({
        path: csvPath,
        header: [
            { id: "link", title: "link" },
            { id: "title", title: "title" }
        ],
        append: true
    });

    await writer.writeRecords(results);
    console.log(`Scraping complete. ${results.length} articles saved to ${csvPath}`);
    await browser.close();
})();
