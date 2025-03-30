const puppeteer = require("puppeteer");
const fs = require("fs");
const Papa = require("papaparse");
const path = require("path");

const outputCsvPath = path.join(__dirname, "medical_news_today.csv");

(async () => {
    const browser = await puppeteer.launch({ headless: false, slowMo: 50 });
    const page = await browser.newPage();

    const url = "https://www.medicalnewstoday.com/"; 
    await page.goto(url, { waitUntil: "networkidle2" });

    console.log("🔎 Scrolling to load more articles...");

    // Scroll to load more articles
    await page.evaluate(async () => {
        await new Promise(resolve => {
            let totalHeight = 0;
            const distance = 500;
            const timer = setInterval(() => {
                window.scrollBy(0, distance);
                totalHeight += distance;
                if (totalHeight >= document.body.scrollHeight) {
                    clearInterval(timer);
                    resolve();
                }
            }, 300);
        });
    });

    console.log("🔎 Scraping article links...");

    // Extract article links
    const articleLinks = await page.$$eval("a", anchors =>
        anchors
            .map(a => a.href.trim())
            .filter(href => href.includes("medicalnewstoday.com/articles/") && href.startsWith("https"))
    );    

    // Remove duplicates
    const uniqueLinks = [...new Set(articleLinks)];

    console.log(`✅ Found ${uniqueLinks.length} articles.`);
    
    let articles = [];

    for (let link of uniqueLinks) {
        console.log(`📄 Scraping: ${link}`);
        
        try {
            const articlePage = await browser.newPage();
            await articlePage.goto(link, { waitUntil: "networkidle2" });

            const title = await articlePage.$eval("h1", el => el.innerText.trim());
            
            const content = await articlePage.$$eval("p", paragraphs => 
                paragraphs.map(p => p.innerText.trim()).join(" ")
            );

            let author = "Unknown";
            try {
                author = await articlePage.$eval("a.css-u1nnpx", el => el.innerText.trim());
            } catch (error) {
                console.log("⚠️ Author not found.");
            }            

            articles.push({ link, title, content, author });
            await articlePage.close();

        } catch (error) {
            console.error(`❌ Error scraping ${link}: ${error.message}`);
        }
    }

    // Convert to CSV format
    const csvData = Papa.unparse(articles);
    fs.writeFileSync(outputCsvPath, csvData, "utf8");

    console.log(`✅ Data saved to: ${outputCsvPath}`);

    await browser.close();
})();
