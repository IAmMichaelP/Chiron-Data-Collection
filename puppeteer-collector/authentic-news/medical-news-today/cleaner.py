import pandas as pd

# Read CSV
csv_file = "medical_news_today.csv"
data = pd.read_csv(csv_file)

# Strip spaces from column names (fix potential errors)
data.columns = data.columns.str.strip()

# Ensure 'Link' column exists
if 'Link' in data.columns:
    # Remove unnecessary prefix
    data['Link'] = data['Link'].str.replace("https://www.medicalnewstoday.com/", "", regex=False)

    # Save cleaned data
    cleaned_file = "cleaned_scraped_data.csv"
    data.to_csv(cleaned_file, index=False)
    print(f"✅ Cleaned data saved to {cleaned_file}")
else:
    print("❌ Error: 'Link' column not found in CSV.")
