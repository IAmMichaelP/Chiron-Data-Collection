const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");
const csvWriter = require("csv-writer").createObjectCsvWriter;

(async () => {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    await page.setViewport({ width: 1200, height: 800 });

    await page.goto('https://apnews.com/hub/public-health', {
        waitUntil: 'networkidle2',
        timeout: 60000
    });

    const articleSelector = '.PageList-items-item';
    const loadMoreSelector = '.PageList-nextPage a.Button';

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

            const newArticles = await page.evaluate((articleSelector) => {
                return Array.from(document.querySelectorAll(articleSelector)).map(article => {
                    const linkEl = article.querySelector('.PagePromo-title a');
                    const titleEl = article.querySelector('.PagePromo-title a span');
                    const dateEl = article.querySelector('.PagePromo-date span');

                    const link = linkEl ? linkEl.href : null;
                    const title = titleEl ? titleEl.innerText.trim() : null;
                    const date = dateEl ? dateEl.innerText.trim() : null;

                    return { link, title, date };
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

            // Load more
            const button = await page.$(loadMoreSelector);
            if (button) {
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

    const csvPath = path.join(__dirname, "scraped_apnews_health.csv");
    const writer = csvWriter({
        path: csvPath,
        header: [
            { id: "link", title: "link" },
            { id: "title", title: "title" },
            { id: "date", title: "date" }
        ],
        // append: true
    });

    await writer.writeRecords(results);
    console.log(`Scraped ${results.length} articles`);
    await browser.close();
})();
