const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");
const csvWriter = require("csv-writer").createObjectCsvWriter;

(async () => {
    let browser;
    try {
        browser = await puppeteer.launch({ headless: false, slowMo: 0 });
        const page = await browser.newPage();
        await page.goto('https://www.bbc.com/sport');

        const articleSelector = '.sc-225578b-0.btdqbl'; // Selector for each article
        const titleSelector = '.sc-9d830f2a-3.gCxBuB'; // Selector for the title

        let results = [];
        let uniqueLinks = new Set(); // To track unique articles

        for (let pageNumber = 1; pageNumber <= 10; pageNumber++) {
            try {
                await page.waitForSelector(articleSelector, { timeout: 5000 });

                // Extract links and titles
                const articles = await page.evaluate((articleSelector, titleSelector) => {
                    return Array.from(document.querySelectorAll(articleSelector)).map(article => {
                        const linkElement = article.querySelector('a');
                        const link = linkElement ? `${linkElement.href}` : null;
                        const titleElement = article.querySelector(titleSelector);
                        const title = titleElement ? titleElement.innerText.trim() : "";
                        return { link, title };
                    });
                }, articleSelector, titleSelector);

                const filteredArticles = articles.filter(article =>
                    article.link && article.title && !uniqueLinks.has(article.link)
                );

                // Log the parsed links and titles for this page
                console.log(`\n--- Page ${pageNumber} Articles ---`);
                filteredArticles.forEach(article => {
                    console.log(`Title: ${article.title}`);
                    console.log(`Link: ${article.link}`);
                    console.log('---');
                });

                // Add to results and track unique links
                filteredArticles.forEach(article => {
                    results.push(article);
                    uniqueLinks.add(article.link);
                });

                // Navigate to next page
                for (let pageNumber = 1; pageNumber <= 20; pageNumber++) {
                    try {
                        await page.waitForSelector(articleSelector, { timeout: 5000 });
                
                        const articles = await page.evaluate((articleSelector, titleSelector) => {
                            return Array.from(document.querySelectorAll(articleSelector)).map(article => {
                                const linkElement = article.querySelector('a');
                                const link = linkElement ? `${linkElement.href}` : null;
                                const titleElement = article.querySelector(titleSelector);
                                const title = titleElement ? titleElement.innerText.trim() : "";
                                return { link, title };
                            });
                        }, articleSelector, titleSelector);
                
                        const filteredArticles = articles.filter(article =>
                            article.link && article.title && !uniqueLinks.has(article.link)
                        );
                
                        console.log(`\n--- Page ${pageNumber} Articles ---`);
                        filteredArticles.forEach(article => {
                            console.log(`Title: ${article.title}`);
                            console.log(`Link: ${article.link}`);
                            console.log('---');
                        });
                
                        filteredArticles.forEach(article => {
                            results.push(article);
                            uniqueLinks.add(article.link);
                        });
                
                        // Attempt to click the "Next" button
                        const nextButtonSelector = '[data-testid="pagination-next-button"]';
                        const nextButton = await page.$(nextButtonSelector);
                        if (nextButton) {
                            await Promise.all([
                                page.waitForNavigation({ waitUntil: 'networkidle2' }),
                                nextButton.click()
                            ]);
                        } else {
                            console.log("No more pages.");
                            break;
                        }
                
                    } catch (error) {
                        console.error(`Error on page ${pageNumber}:`, error);
                        break;
                    }
                }
                
            } catch (error) {
                console.error(`Error during iteration ${pageNumber}:`, error);
                break;
            }
        }

        // Save results to CSV
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
        console.log(`Scraping complete. Data saved to ${csvPath}`);
    } catch (error) {
        console.error("An error occurred:", error);
    } finally {
        if (browser) await browser.close();
    }
})();
