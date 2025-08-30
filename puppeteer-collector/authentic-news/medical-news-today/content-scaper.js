const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());
const fs = require("fs");
const Papa = require("papaparse");
const path = require("path");

const csvFilePath = path.join(__dirname, "medical_news_today.csv"); // Path to CSV
const targetColumn = "Link"; // Column with URLs

(async () => {
    const browser = await puppeteer.launch({ headless: false, slowMo: 50 });
    const page = await browser.newPage();

    // Load CSV file
    const csvFile = fs.readFileSync(csvFilePath, "utf8");
    const results = Papa.parse(csvFile, { header: true, dynamicTyping: true });

    // Process each article
    for (const row of results.data) {
        const url = row[targetColumn]; // URL should already be full
        if (!url) continue;

        console.log(`🔎 Processing: ${url}`);

        try {
            await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 }); // 60s timeout

            // Wait for content to load
            const articleBodySelector = "div.css-15zq5p1 p"; // Updated for actual article text
            await page.waitForSelector(articleBodySelector, { timeout: 100000 });

            // Extract elements safely
            const getTextContent = async (selector, defaultText = "Not Found") => {
                try {
                    return await page.$eval(selector, (el) => el.textContent.trim());
                } catch {
                    return defaultText;
                }
            };

            // Extract title, author, date, and article content
            const title = await getTextContent("h1", "Title not found");
            const author = await getTextContent("p.css-cbz3gh a", "Author not found");
            const date = await getTextContent("time[data-testid='article-published-date']", "Date not found");

            const paragraphs = await page.$$eval(articleBodySelector, (elements) =>
                elements.map((el) => el.textContent.trim()).join("\n")
            );

            console.log(`✅ Title: ${title}`);
            console.log(`👤 Author: ${author}`);
            console.log(`📅 Date: ${date}`);
            console.log(`📜 Content: ${paragraphs.slice(0, 100)}...`); // Preview first 100 chars

            // Save scraped data to row
            row["Title"] = title;
            row["Author"] = author;
            row["Date"] = date;
            row["Content"] = paragraphs;

        } catch (error) {
            console.error(`❌ Error processing ${url}:`, error);
            row["Content"] = "Error: Could not scrape content";
        }
    }

    // Save updated CSV
    const updatedCsv = Papa.unparse(results.data, { header: true });
    fs.writeFileSync(csvFilePath, updatedCsv, "utf8");

    console.log("✅ Scraped data saved to CSV file.");

    await browser.close();
})();
