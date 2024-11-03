
import pandas as pd
from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest
import time

# Step 1: Read the CSV file using pandas
df = pd.read_csv(r"C:\xampp\htdocs\GitHub\Chiron\dataset_collector\dataset1.csv")
print(df.head(10))
print("Number of rows in final dataframe:", len(df))