const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");
const csvWriter = require("csv-writer").createObjectCsvWriter;

(async () => {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    await page.setViewport({ width: 1200, height: 800 });

    await page.goto('https://www.nbcnews.com/select/wellness/sleep', {
        waitUntil: 'networkidle2',
        timeout: 60000
    });

    const articleSelector = 'div[data-testid="x-by-one__container"]';
    const loadMoreSelector = 'button[data-testid="button-hover-animation"]';

    let results = [];
    const maxIterations = 50;
    const seenLinks = new Set();

    for (let i = 0; i < maxIterations; i++) {
        try {
            console.log(`Processing iteration ${i + 1}`);

            await page.waitForSelector(articleSelector, {
                timeout: 10000,
                visible: true
            });

            const newArticles = await page.evaluate((newByOneSelector) => {
                return Array.from(document.querySelectorAll(newByOneSelector)).map(card => {
                    const titleEl = card.querySelector('a[data-testid="x-by-one__headline__link"]');
                    const tagEl = card.querySelector('span[data-testid="unibrow-text"]');

                    const link = titleEl?.href ?? '';
                    const title = titleEl?.innerText.trim() ?? '';
                    const tags = tagEl?.innerText.trim() ?? '';

                    return { link, title, tags };
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

            // Try to click "Load More" button
            const button = await page.$(loadMoreSelector);
            if (button) {
                const isDisabled = await button.evaluate(b => b.disabled);
                if (isDisabled) {
                    console.log('No more stories to load');
                    break;
                }

                await button.evaluate(b => b.scrollIntoView({ behavior: 'smooth', block: 'center' }));
                await button.evaluate(b => b.click());
                console.log('Clicked Load More');

                await new Promise(resolve => setTimeout(resolve, 2000));
            } else {
                console.log('No Load More button found');
                break;
            }

        } catch (err) {
            console.error(`Error on iteration ${i + 1}:`, err.message);
            await page.screenshot({ path: `error-${i}.png` });
            break;
        }
    }

    const csvPath = path.join(__dirname, "scraped_data.csv");
    const writer = csvWriter({
        path: csvPath,
        header: [
            { id: "link", title: "link" },
            { id: "title", title: "title" },
            { id: "tags", title: "tags" }
        ],
        append: true
    });

    await writer.writeRecords(results);
    console.log(`Scraped ${results.length} articles`);
    await browser.close();
})();
