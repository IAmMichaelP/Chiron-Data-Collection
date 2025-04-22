const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");
const csvWriter = require("csv-writer").createObjectCsvWriter;

(async () => {
    let browser;
    try {
        browser = await puppeteer.launch({ headless: false, slowMo: 0 });
        const page = await browser.newPage();

        const baseUrl = 'https://healthimpactnews.com';
        const articleSelector = 'h2.entry-title';
        const titleSelector = 'a'; // Selector for anchor within entry-title

        let results = [];
        let uniqueLinks = new Set();

        for (let pageNumber = 1; pageNumber <= 3; pageNumber++) {
            try {
                const url = pageNumber === 1 ? baseUrl : `${baseUrl}/page/${pageNumber}/`;
                await page.goto(url, { waitUntil: 'networkidle2' });
                await page.waitForSelector(articleSelector, { timeout: 5000 });

                const articles = await page.evaluate((articleSelector, titleSelector) => {
                    return Array.from(document.querySelectorAll(articleSelector)).map(article => {
                        const anchor = article.querySelector(titleSelector);
                        const link = anchor ? anchor.href : null;
                        const title = anchor ? anchor.innerText.trim() : null;
                        return { link, title };
                    });
                }, articleSelector, titleSelector);

                articles.forEach(article => {
                    if (article.link && article.title && !uniqueLinks.has(article.link)) {
                        console.log(`Page title "${article.title}" with link: ${article.link} is scraped.`);
                        results.push(article);
                        uniqueLinks.add(article.link);
                    }
                });

                console.log(`Page ${pageNumber} scraped. Articles found: ${articles.length}`);
            } catch (error) {
                console.error(`Error during iteration ${pageNumber}:`, error);
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
        console.log(`Scraping complete. Data saved to ${csvPath}`);
    } catch (error) {
        console.error("An error occurred:", error);
    } finally {
        if (browser) await browser.close();
    }
})();
