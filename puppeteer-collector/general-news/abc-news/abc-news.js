const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");
const csvWriter = require("csv-writer").createObjectCsvWriter;

(async () => {
    const browser = await puppeteer.launch({ headless: false, slowMo: 0 });
    const page = await browser.newPage();
    await page.goto('https://www.abc.net.au/news/topic/books', { waitUntil: 'networkidle2' });

    const articleSelector = '.DetailCard_card__oooSN';
    const titleSelector = '.DetailCard_link__qM1Oi';
    const loadMoreSelector = 'button[data-component="PaginationLoadMoreButton"]';

    let results = [];
    const maxIterations = 20;
    const seenLinks = new Set();

    for (let i = 0; i < maxIterations; i++) {
        try {
            await page.waitForSelector(articleSelector, { timeout: 5000 });

            const newArticles = await page.evaluate((articleSelector, titleSelector) => {
                return Array.from(document.querySelectorAll(articleSelector)).map(article => {
                    const linkElement = article.querySelector(titleSelector);
                    const link = linkElement ? linkElement.href : null;
                    const title = linkElement ? linkElement.innerText.trim() : null;

                    const tags = Array.from(article.querySelectorAll('.Tag_link__PE2t9.Tag_tag__TMEI2.CardTag_tag__2hWFV'))
                        .map(tag => tag.textContent.trim());

                    return { link, title, tags };
                });
            }, articleSelector, titleSelector);
            // Add this loop to print the tags outside page.evaluate
            newArticles.forEach(article => {
                console.log(`Title: ${article.title}`);
                console.log(`Tags: ${article.tags.join(', ')}`);
            });

            const filtered = newArticles.filter(article =>
                article.link &&
                article.title &&
                article.title !== "No Title" &&
                !seenLinks.has(article.link) &&
                !article.tags.includes("Topic:Health") // Skip Health-tagged articles
            );

            filtered.forEach(article => {
                console.log(`Parsed: ${article.title} - ${article.link}`);
                seenLinks.add(article.link);
                results.push({ link: article.link, title: article.title });
            });

            const loadMoreButton = await page.$(loadMoreSelector);
            if (loadMoreButton) {
                console.log(`Clicking 'Load more stories' button at iteration ${i + 1}`);

                // Count current number of articles
                const previousCount = await page.$$eval(articleSelector, els => els.length);

                // Scroll to button and click
                await page.evaluate(el => el.scrollIntoView(), loadMoreButton);

                await Promise.all([
                    loadMoreButton.click(),
                    page.waitForFunction(
                        (selector, oldCount) =>
                            document.querySelectorAll(selector).length > oldCount,
                        { timeout: 10000 },
                        articleSelector,
                        previousCount
                    )
                ]);

                console.log("New articles loaded.");
                await new Promise(resolve => setTimeout(resolve, 2000));

            } else {
                console.log("No more 'Load more stories' button found.");
                break;
            }


        } catch (err) {
            console.error(`Error on iteration ${i + 1}:`, err);
            break;
        }
    }

    // Save to CSV
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
