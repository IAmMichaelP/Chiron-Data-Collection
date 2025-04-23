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
                            // Find the heading
                            const heading = Array.from(document.querySelectorAll('p, h2, h3')).find(el => 
                                el.textContent.includes('You might also be interested in')
                            );
                            if (heading) {
                                // Traverse up to the top-level container and remove it
                                let parent = heading.closest('div.max-w-screen-xl, div.max-w-screen-xl.mx-auto');
                                if (parent) parent.remove();
                            }
                            // Select all elements with the class 'em-mod-video' or other specific selectors
                            const elementsToRemove = document.querySelectorAll(
                                '.em-mod-video, .anchortext, .module.ad, .emb-center-well-ad, .up-show, .bg-gray-50.border-t.border-b, .ad-wrapper, .ia-module-container, .ad, .module, .sidebar, .recommended-articles, .em-mod-slideshow, .global-container-2, .emb-center-well-ad .default-creative-container, .instream-related-mod, .default-creative-container, [data-v-app], bg-gray-50, border-t border-b border-gray-400, px-6 py-10'
                            );
                            elementsToRemove.forEach(element => element.remove());
                        });

                        const articleBodySelector = '.content-repository-content'; // Selector for the article body
                        const dateSelector = 'time[datetime]'; // Selector for the date
                        const authorSelector = 'address a[rel="author"]'; // Selector for the author

                        // Wait for the selector to appear on the page
                        await page.waitForSelector(articleBodySelector, { timeout: 5000 });

                        // Extract the entire article body HTML for debugging
                        const paragraphs = await page.$$eval(articleBodySelector, (elements) => {
                            return elements.map(el => el.textContent.trim());
                        });

                        // Extract the publication date
                        let date = 'Unknown';
                        try {
                            date = await page.$eval(dateSelector, (el) => el.textContent.trim());
                        } catch (error) {
                            console.error(`Could not extract date for ${columnValue}:`, error);
                        }

                        // Extract the author name
                        let author = 'Unknown';
                        try {
                            author = await page.$eval(authorSelector, (el) => el.textContent.trim());
                        } catch (error) {
                            console.error(`Could not extract author for ${columnValue}:`, error);
                        }

                        // Log the extracted data for inspection
                        console.log('Article Body:', paragraphs);
                        console.log('Date:', date);
                        console.log('Author:', author);

                        // Add the scraped data to the row
                        row['content'] = paragraphs.join('\n'); // Combine paragraphs into a single string
                        row['author'] = author; // Add the author
                        row['date'] = date; // Add the date
                        
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