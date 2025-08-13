# extract_unique_tags.py

import pandas as pd

# Load CSV
df = pd.read_csv("scraped_data.csv")

# Assume the 'tag' column contains comma-separated tags
all_tags = set()

for tags in df["tags"].dropna():
    for tag in tags.split(","):
        all_tags.add(tag.strip().lower())

# Display sorted unique tags
print("✅ Unique Tags Found:")
for tag in sorted(all_tags):
    print(tag)
