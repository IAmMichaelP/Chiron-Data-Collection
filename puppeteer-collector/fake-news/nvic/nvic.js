const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");
const csvWriter = require("csv-write-stream");

(async () => {
    let browser;
    try {
        browser = await puppeteer.launch({ headless: false, slowMo: 0 });
        const page = await browser.newPage();
        const baseURL = "https://www.nvic.org";

        await page.goto(`${baseURL}/NewsCategory/PagedArticles`, { waitUntil: 'networkidle2' });

        const articleSelector = '.article';
        const titleSelector = '.title a';
        const authorSelector = '.overlay .author';
        const nextPageSelector = 'a.page-link.next';

        let results = [];
        let uniqueLinks = new Set();

        while (true) {
            try {
                await page.waitForSelector(articleSelector, { timeout: 10000 });

                const articles = await page.evaluate((articleSelector, titleSelector, authorSelector) => {
                    return Array.from(document.querySelectorAll(articleSelector)).map(article => {
                        const titleEl = article.querySelector(titleSelector);
                        const authorEl = article.querySelector(authorSelector);

                        const title = titleEl ? titleEl.innerText.trim() : null;
                        let link = titleEl ? titleEl.getAttribute("href") : null;
                        if (link && !link.startsWith('http')) {
                            link = 'https://www.nvic.org' + link;
                        }
                        const author = authorEl ? authorEl.innerText.trim() : null;

                        return { title, link, author };
                    });
                }, articleSelector, titleSelector, authorSelector);

                const validArticles = articles.filter(article => article.title && article.link);

                validArticles.forEach(article => {
                    if (!uniqueLinks.has(article.link)) {
                        results.push(article);
                        uniqueLinks.add(article.link);
                    }
                });

                console.log(`Collected ${validArticles.length} articles from this page.`);

                const nextPage = await page.$(nextPageSelector);
                if (nextPage) {
                    console.log("Navigating to next page...");
                    await Promise.all([
                        page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 }),
                        nextPage.click()
                    ]);
                } else {
                    console.log("No more pages.");
                    break;
                }
            } catch (error) {
                console.error("Error scraping page:", error);
                break;
            }
        }

        // Save to CSV
        const csvPath = path.join(__dirname, "scraped_data.csv");
        const writer = csvWriter({ headers: ["title", "link", "author"] });
        writer.pipe(fs.createWriteStream(csvPath));
        results.forEach(article => writer.write(article));
        writer.end();

        console.log(`Scraping complete. ${results.length} articles saved to ${csvPath}`);
    } catch (error) {
        console.error("An error occurred:", error);
    } finally {
        if (browser) await browser.close();
    }
})();
