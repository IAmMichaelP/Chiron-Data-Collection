const puppeteer = require("puppeteer");
const Papa = require('papaparse');
const fs = require('fs');

const csvFilePath = 'scraped_data.csv'; // Replace with your CSV file path
const targetColumn = 'link'; // Replace with the name of the column you want to sift through

// Read the CSV file
const csvFile = fs.readFileSync(csvFilePath, 'utf8');

// Define the delay function
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

(async () => {
    let browser;
    try {
        // Parse the CSV file
        Papa.parse(csvFile, {
            header: true, // Treat the first row as headers
            dynamicTyping: true, // Automatically convert numeric values to numbers
            complete: async (results) => {
                // Access the parsed data
                const rows = results.data;

                // Sift through the target column
                for (const row of rows) {
                    const columnValue = row[targetColumn];
                    console.log(`Processing: ${columnValue}`);

                    // Launch Puppeteer and process the URL
                    const browser = await puppeteer.launch({ headless: false, slowMo: 0 }); // Set headless: true for faster execution
                    const page = await browser.newPage();

                    try {
                        await page.goto(columnValue, { waitUntil: 'networkidle2' });

                        // Remove unwanted elements (e.g., video containers and elements with data-v-app)
                        await page.evaluate(() => {
                            // Select all elements with the class 'em-mod-video' or other specific selectors
                            const elementsToRemove = document.querySelectorAll(
                                '.em-mod-video, .anchortext, .module.ad, .emb-center-well-ad, .up-show, .ad-wrapper, .ia-module-container, .ad, .module, .sidebar, .recommended-articles, .em-mod-slideshow, .global-container-2, .emb-center-well-ad .default-creative-container, .instream-related-mod, .default-creative-container, [data-v-app]'
                            );
                            elementsToRemove.forEach(element => element.remove());
                        });

                        const articleBodySelector = '.article__body p'; // Selector for the article body

                        // Wait for the selector to appear on the page
                        await page.waitForSelector(articleBodySelector, { timeout: 5000 });

                        // Extract the entire article body HTML for debugging
                        const paragraphs = await page.$$eval(articleBodySelector, (elements) => {
                            return elements.map(el => el.textContent.trim());
                        });

                        // Log the article body HTML for inspection
                        console.log('Article Body HTML:', paragraphs);

                        // Add the scraped content to the row
                        row['content'] = paragraphs.join('\n'); // Combine paragraphs into a single string

                        // Introduce a 15-second delay before processing the next row
                        await delay(3000);
                    } catch (error) {
                        console.error(`Error processing ${columnValue}:`, error);
                        row['content'] = 'Error: Could not scrape content'; // Add error message to the row
                    } finally {
                        await browser.close();
                    }
                }

                // Save the updated data back to the CSV file
                const updatedCsv = Papa.unparse(rows, { header: true });
                fs.writeFileSync(csvFilePath, updatedCsv, 'utf8');
                console.log('Scraped data saved to CSV file.');
            },
            error: (error) => {
                console.error('Error parsing CSV file:', error);
            },
        });
    } catch (error) {
        console.error("An error occurred:", error);
    } finally {
        if (browser) await browser.close();
    }
})();