const puppeteer = require("puppeteer");
const Papa = require('papaparse');
const fs = require('fs');

const csvFilePath = 'scraped_data.csv';
const targetColumn = 'link';
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

(async () => {
    let browser;
    try {
        const csvFile = fs.readFileSync(csvFilePath, 'utf8');

        const results = Papa.parse(csvFile, {
            header: true,
            dynamicTyping: true
        });

        const rows = results.data;

        browser = await puppeteer.launch({ headless: false, slowMo: 0 });
        const page = await browser.newPage();

        for (const row of rows) {
            const url = row[targetColumn];
            console.log(`Processing: ${url}`);

            try {
                await page.goto(url, { waitUntil: 'networkidle2' });

                // Clean the page by removing unwanted elements
                await page.evaluate(() => {
                    const selectorsToRemove = [
                        '.entry-title', '.em-mod-video', '.anchortext', '.module.ad',
                        '.emb-center-well-ad', '.up-show', '.bg-gray-50.border-t.border-b',
                        '.ad-wrapper', '.ia-module-container', '.ad', '.module', '.sidebar',
                        '.recommended-articles', '.em-mod-slideshow', '.global-container-2',
                        '.emb-center-well-ad .default-creative-container', '.instream-related-mod',
                        '.default-creative-container', '[data-v-app]', 'bg-gray-50', 
                        'border-t border-b border-gray-400', 'px-6 py-10'
                    ];
                    selectorsToRemove.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => el.remove());
                    });
                });

                // Selectors
                const articleBodySelector = '.sc-3b6b161a-0.dEGcKf p';
                const dateSelector = '.sc-801dd632-0.eSlECZ .sc-801dd632-2.IvNnh';
                const authorSelector = '.sc-801dd632-0.eSlECZ .sc-801dd632-7.lasLGY';

                await page.waitForSelector(articleBodySelector, { timeout: 5000 });

                // Extract article content until "Xo," is found
                const paragraphs = await page.$$eval(articleBodySelector, elements => {
                    const content = [];
                    for (const el of elements) {
                        const text = el.textContent.trim();
                        if (text === "Read More" || text === "Read More:") break;
                        content.push(text);
                    }
                    return content;
                });


                // Extract date
                let date = 'Unknown';
                try {
                    date = await page.$eval(dateSelector, el => el.textContent.trim());
                } catch {
                    console.warn(`No date found for ${url}`);
                }

                // Extract author
                let author = 'Unknown';
                try {
                    author = await page.$eval(authorSelector, el => el.textContent.trim());
                } catch {
                    console.warn(`No author found for ${url}`);
                }

                // Log and save
                console.log('Date:', date);
                console.log('Author:', author);
                console.log('Paragraphs:', paragraphs);

                row['content'] = paragraphs.join('\n');
                row['author'] = author;
                row['date'] = date;

                await delay(10000); // Wait 3 seconds between pages
            } catch (error) {
                console.error(`Error processing ${url}:`, error);
                row['content'] = 'Error: Could not scrape content';
            }
        }

        // Write updated data back to CSV
        const updatedCsv = Papa.unparse(rows, { header: true });
        fs.writeFileSync(csvFilePath, updatedCsv, 'utf8');
        console.log('Scraped data saved to CSV file.');

    } catch (error) {
        console.error("An error occurred:", error);
    } finally {
        if (browser) await browser.close();
    }
})();
