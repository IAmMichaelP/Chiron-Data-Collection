const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");
const createCsvWriter = require("csv-writer").createObjectCsvWriter;

(async () => {
    let browser;
    try {
        browser = await puppeteer.launch({ headless: false, slowMo: 0 });
        const page = await browser.newPage();
        await page.goto('https://www.theatlantic.com/politics/');

        const articleSelector = '.LandingRiver_promoItem__SLYUT';
        const titleSelector = '.LandingRiver_title__wdvvu';
        const descriptionSelector = '.LandingRiver_dek__OyPEv';

        let results = [];
        let uniqueLinks = new Set();

        for (let i = 0; i < 10; i++) {
            try {
                await page.waitForSelector(articleSelector, { timeout: 5000 });

                const articles = await page.evaluate((articleSelector, titleSelector, descriptionSelector) => {
                    return Array.from(document.querySelectorAll(articleSelector)).map(article => {
                        const linkElement = article.querySelector('a');
                        const link = linkElement ? linkElement.href : null;
                        const titleElement = article.querySelector(titleSelector);
                        const title = titleElement ? titleElement.innerText.trim() : "";
                        const descriptionElement = article.querySelector(descriptionSelector);
                        const description = descriptionElement ? descriptionElement.innerText.trim() : "";
                        const fullTitle = description ? `${title} - ${description}` : title;
                        return { link, title: fullTitle };
                    });
                }, articleSelector, titleSelector, descriptionSelector);

                for (const article of articles) {
                    if (article.link && article.title && article.title !== "No Title" && article.title.trim() !== "" && !uniqueLinks.has(article.link)) {
                        console.log(`Parsed: ${article.title}\nLink: ${article.link}\n`);
                        results.push(article);
                        uniqueLinks.add(article.link);
                    }
                }

                // Find "More Stories" link based on href containing "after="
                const moreHref = await page.evaluate(() => {
                    const links = Array.from(document.querySelectorAll('a.LandingRiver_paginationLink__4oDwT'));
                    const moreLink = links.find(link => link.href.includes('after='));
                    return moreLink ? moreLink.href : null;
                });

                if (moreHref) {
                    console.log(`Navigating to next page: ${moreHref}\n`);
                    await page.goto(moreHref, { waitUntil: 'networkidle2' });
                } else {
                    console.log("No more pages found. Ending.");
                    break;
                }

            } catch (error) {
                console.error(`Error during iteration ${i + 1}:`, error);
                break;
            }
        }

        // Append to CSV
        const csvPath = path.join(__dirname, "scraped_data.csv");
        const writer = createCsvWriter({
            path: csvPath,
            append: true, // <== enables appending
            header: [
                { id: "link", title: "link" },
                { id: "title", title: "title" }
            ]
        });

        await writer.writeRecords(results);
        console.log(`Scraping complete. ${results.length} articles saved to ${csvPath}`);
    } catch (error) {
        console.error("An error occurred:", error);
    } finally {
        if (browser) await browser.close();
    }
})();

