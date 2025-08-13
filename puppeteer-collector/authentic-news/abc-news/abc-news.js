const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");
const csvWriter = require("csv-writer").createObjectCsvWriter;

(async () => {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    await page.setViewport({ width: 1200, height: 800 });
    
    await page.goto('https://www.abc.net.au/news/health', { 
        waitUntil: 'networkidle2',
        timeout: 60000 
    });

    const articleSelector = '.DetailCard_card__oooSN';
    const titleSelector = '.DetailCard_link__qM1Oi';
    const tagSelector = 'a[data-component="SubjectTag"] p';
    const loadMoreSelector = 'button[data-component="PaginationLoadMoreButton"]';

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

            // Extract articles
            const newArticles = await page.evaluate((articleSelector, titleSelector, tagSelector) => {
                return Array.from(document.querySelectorAll(articleSelector)).map(article => {
                    const linkElement = article.querySelector(titleSelector);
                    const link = linkElement ? linkElement.href : null;
                    const title = linkElement ? linkElement.innerText.trim() : null;
                    
                    const tagElements = article.querySelectorAll(tagSelector);
                    const tags = Array.from(tagElements).map(tag => tag.innerText.trim());
                    
                    return { link, title, tags: tags.join(', ') };
                });
            }, articleSelector, titleSelector, tagSelector);

            // Filter and store new articles
            const filtered = newArticles.filter(article =>
                article.link && article.title && !seenLinks.has(article.link)
            );
            
            filtered.forEach(article => {
                seenLinks.add(article.link);
                results.push(article);
                console.log(`Added: ${article.title}`);
            });

            // Try to click load more button
            try {
                const button = await page.$(loadMoreSelector);
                if (button) {
                    const isDisabled = await button.evaluate(b => b.disabled);
                    if (isDisabled) {
                        console.log('No more stories to load');
                        break;
                    }
                    console.log('Found load more button');
                    
                    // Scroll into view
                    await button.evaluate(b => b.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    }));
                    
                    // Click using JavaScript directly
                    await button.evaluate(b => b.click());
                    
                    console.log('Clicked load more button');
                    
                    // Wait for new content to load
                    // await page.waitForFunction(
                    //     selector => {
                    //         const lastArticle = document.querySelector(selector);
                    //         return lastArticle && lastArticle.getBoundingClientRect().top > 0;
                    //     },
                    //     { timeout: 10000 },
                    //     articleSelector
                    // );
                    
                    await new Promise(resolve => setTimeout(resolve, 2000));
                } else {
                    console.log('No more load more button found');
                    break;
                }
            } catch (err) {
                console.log('Failed to click load more button:', err.message);
                break;
            }
            
        } catch (err) {
            console.error(`Error on iteration ${i + 1}:`, err);
            await page.screenshot({ path: `error-${i}.png` });
            break;
        }
    }

    // Save results
    const csvPath = path.join(__dirname, "scraped_data.csv");
    const writer = csvWriter({
        path: csvPath,
        header: [
            { id: "link", title: "link" },
            { id: "title", title: "title" },
            { id: "tags", title: "tags" }
        ]
    });

    await writer.writeRecords(results);
    console.log(`Scraped ${results.length} articles`);
    await browser.close();
})();