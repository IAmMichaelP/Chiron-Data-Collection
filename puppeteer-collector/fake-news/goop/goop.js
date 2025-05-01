const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");
const csvWriter = require("csv-writer").createObjectCsvWriter;

(async () => {
    let browser;
    try {
        browser = await puppeteer.launch({ headless: false, slowMo: 0 });
        const page = await browser.newPage();

        const baseUrl = 'https://goop.com/wellness/health/';
        const articleCardSelector = 'div[class*="DetailWrapper"]'; // Matches all the new article cards

        let results = [];
        let uniqueLinks = new Set();

        for (let pageNumber = 1; pageNumber <= 50; pageNumber++) {
            try {
                const url = pageNumber === 1 ? baseUrl : `${baseUrl}page/${pageNumber}/`;
                await page.goto(url, { waitUntil: 'networkidle2' });
                await page.waitForSelector(articleCardSelector, { timeout: 5000 });

                const articles = await page.evaluate((selector) => {
                    const cards = Array.from(document.querySelectorAll(selector));
                    return cards.map(card => {
                        const linkEl = card.querySelector('a[href^="https://goop.com"]');
                        const titleEl = card.querySelector('h3');

                        const link = linkEl?.href || null;
                        const title = titleEl?.innerText.trim() || null;

                        return { link, title };
                    }).filter(article => article.link && article.title);
                }, articleCardSelector);

                articles.forEach(article => {
                    if (!uniqueLinks.has(article.link)) {
                        console.log(`"${article.title}" → ${article.link}`);
                        results.push(article);
                        uniqueLinks.add(article.link);
                    }
                });

                console.log(`Page ${pageNumber} done. Articles scraped: ${articles.length}`);
            } catch (error) {
                console.error(`Error scraping page ${pageNumber}:`, error);
                break;
            }
        }

        const csvPath = path.join(__dirname, "scraped_data.csv");
        const writer = csvWriter({
            path: csvPath,
            header: [
                { id: "link", title: "link" },
                { id: "title", title: "title" }
            ]
        });

        await writer.writeRecords(results);
        console.log(`✅ Scraping complete. Saved ${results.length} articles to ${csvPath}`);
    } catch (error) {
        console.error("❌ An error occurred:", error);
    } finally {
        if (browser) await browser.close();
    }
})();
