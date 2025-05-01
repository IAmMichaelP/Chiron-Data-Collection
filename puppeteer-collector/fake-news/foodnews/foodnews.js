const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");
const csvWriter = require("csv-writer").createObjectCsvWriter;

(async () => {
    let browser;
    try {
        browser = await puppeteer.launch({ headless: false, slowMo: 0 });
        const page = await browser.newPage();

        const baseUrl = 'https://food.news/author/zoeysky/';
        const postSelector = '.Post';

        let results = [];
        let uniqueLinks = new Set();

        for (let pageNumber = 1; pageNumber <= 30; pageNumber++) {
            try {
                const url = pageNumber === 1 ? baseUrl : `${baseUrl}page/${pageNumber}/`;
                await page.goto(url, { waitUntil: 'networkidle2' });
                await page.waitForSelector(postSelector, { timeout: 5000 });

                const articles = await page.evaluate(() => {
                    const base = 'https://food.news/';
                    return Array.from(document.querySelectorAll('.Post')).map(post => {
                        const headlineAnchor = post.querySelector('.Headline a');
                        return headlineAnchor ? {
                            link: base + headlineAnchor.getAttribute('href').replace(/^\//, ''),
                            title: headlineAnchor.innerText.trim()
                        } : null;
                    }).filter(item => item !== null);
                });

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
