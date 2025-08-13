const puppeteer = require("puppeteer");
const Papa = require("papaparse");
const fs = require("fs");
const path = require("path");

const EDGE_PATH = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const csvFilePath = "scraped_data.csv";
const targetColumn = "link";
const BATCH_SIZE = 10;
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function scrapePage(browser, row, url) {
    const page = await browser.newPage();
    try {
        console.log(`Processing: ${url}`);
        await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });

        await page.evaluate(() => {
            const selectorsToRemove = [
                ".entry-title", ".expanded-byline-contributors", ".articleBylineContainer", ".em-mod-video", ".anchortext", ".module.ad",
                ".emb-center-well-ad", ".up-show", ".bg-gray-50.border-t.border-b",
                ".ad-wrapper", ".ia-module-container", ".ad", ".module", ".sidebar",
                ".recommended-articles", ".em-mod-slideshow", ".global-container-2",
                ".emb-center-well-ad .default-creative-container", ".instream-related-mod",
                ".default-creative-container", "[data-v-app]", "bg-gray-50",
                "border-t border-b border-gray-400", "px-6 py-10"
            ];
            selectorsToRemove.forEach(selector => {
                document.querySelectorAll(selector).forEach(el => el.remove());
            });
        });

        const articleBodySelector = ".article-body__content p";
        const dateSelector = ".article-body__date-source time";
        const authorSelector = "span.byline-name a";

        await page.waitForSelector(articleBodySelector, { timeout: 5000 });

        const paragraphs = await page.$$eval(articleBodySelector, (elements) => {
            const content = [];
            for (const el of elements) {
                const text = el.textContent.trim();
                if (el.classList.contains("endmark") || text === "Read More" || text === "Read More:") break;
                content.push(text);
            }
            return content;
        });

        let date = "Unknown";
        try {
            date = await page.$eval(dateSelector, (el) => el.textContent.trim());
        } catch {
            console.warn(`No date found for ${url}`);
        }

        let authors = ["Unknown"];
        try {
            authors = await page.$$eval(authorSelector, (authorLinks) =>
                authorLinks.map((el) => el.textContent.trim())
            );
            if (authors.length === 0) authors = ["Unknown"];
        } catch {
            console.warn(`No authors found for ${url}`);
        }

        row["content"] = paragraphs.join("\n");
        row["author"] = authors.join(", ");
        row["date"] = date;

        console.log("Date:", date);
        console.log("Authors:", authors.join(", "));
        console.log("Paragraphs:", paragraphs.length);

    } catch (error) {
        console.error(`Error processing ${url}:`, error);
        row["content"] = "Error: Could not scrape content";
    } finally {
        await page.close(); // Free memory
        await delay(10000);
    }
}

async function run() {
    const csvFile = fs.readFileSync(csvFilePath, "utf8");
    const results = Papa.parse(csvFile, { header: true, dynamicTyping: true });
    const rows = results.data;

    for (let i = 0; i < rows.length; i += BATCH_SIZE) {
        const batch = rows.slice(i, i + BATCH_SIZE);
        console.log(`--- Starting batch ${i / BATCH_SIZE + 1} ---`);

        const browser = await puppeteer.launch({
            headless: false,
            slowMo: 0,
            executablePath: EDGE_PATH,
        });

        for (const row of batch) {
            const url = row[targetColumn];
            if (!url || row["content"]) continue; // Skip empty or already-scraped
            await scrapePage(browser, row, url);
        }

        await browser.close();
        console.log(`--- Batch ${i / BATCH_SIZE + 1} complete ---`);

        // Save after every batch
        const updatedCsv = Papa.unparse(rows, { header: true });
        fs.writeFileSync(csvFilePath, updatedCsv, "utf8");
    }

    console.log("✅ All batches done. Scraped data saved to CSV.");
}

run();
