const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");
const csvWriter = require("csv-writer").createObjectCsvWriter;

(async () => {
    const baseUrl = 'https://consciouslifenews.com/category/health-wellness';
    const articleSelector = 'article.jeg_post';
    const maxPages = 130;

    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    await page.setViewport({ width: 1200, height: 800 });

    const results = [];
    const seenLinks = new Set();

    for (let pageNumber = 1; pageNumber <= maxPages; pageNumber++) {
        const url = pageNumber === 1 ? baseUrl : `${baseUrl}/page/${pageNumber}/`;
        console.log(`🧭 Navigating to ${url}`);

        try {
            await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });

            await page.waitForSelector(articleSelector, { timeout: 10000 });

            const newArticles = await page.evaluate((articleSelector) => {
                const articles = Array.from(document.querySelectorAll(articleSelector));
                return articles.map(article => {
                    const linkEl = article.querySelector("h3.jeg_post_title a");
                    const dateEl = article.querySelector(".jeg_meta_date");
                    const authorEl = article.querySelector(".jeg_meta_author a");
                    const tagEl = article.querySelector(".jeg_post_category a");

                    const title = linkEl?.innerText.trim() || null;
                    const link = linkEl?.href || null;
                    const date = dateEl?.innerText.trim() || null;
                    const author = authorEl?.innerText.trim() || "Unknown";
                    const tag = tagEl?.innerText.trim() || "None";

                    return { link, title, date, author, tag };
                });
            }, articleSelector);

            const filtered = newArticles.filter(article =>
                article.link && article.title && !seenLinks.has(article.link)
            );

            filtered.forEach(article => {
                seenLinks.add(article.link);
                results.push(article);
                console.log(`✅ Added: ${article.title}`);
            });

            if (filtered.length === 0) {
                console.log("⚠️ No new articles found on this page. Stopping early.");
                break;
            }

        } catch (err) {
            console.error(`❌ Error on page ${pageNumber}:`, err.message);
            await page.screenshot({ path: `error-page-${pageNumber}.png` });
            break;
        }
    }

    const csvPath = path.join(__dirname, "scraped_consciouslifenews.csv");
    const writer = csvWriter({
        path: csvPath,
        header: [
            { id: "link", title: "link" },
            { id: "title", title: "title" },
            { id: "date", title: "date" },
            { id: "author", title: "author" },
            { id: "tag", title: "tag" }
        ]
    });

    await writer.writeRecords(results);
    console.log(`✅ Scraped ${results.length} articles total.`);
    await browser.close();
})();
