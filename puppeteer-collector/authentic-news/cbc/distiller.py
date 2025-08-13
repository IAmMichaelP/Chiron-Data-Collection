import pandas as pd

# Tags to exclude (not related to health/wellness)
unwanted_keywords = {
    "activism and lobbying", "adventure travel", "afl", "air incidents", "air transport industry",
    "animals", "art", "artificial intelligence", "australian federal elections", "birds",
    "black deaths in custody", "careers", "courts", "cricket", "crime", "cycling", "dogs",
    "drug offences", "drugs", "elections", "emergency services", "food and drink", "gender identity",
    "government and politics", "history", "homicide", "hospitality industry", "human interest",
    "human rights", "indigenous australians", "law", "lgbt", "marathon", "marine biology", "men",
    "police", "public housing", "refugees", "royalty", "safety", "scams and fraud", "sports organisations",
    "stabbings", "travel and tourism", "weather", "workplace accidents and incidents", "world politics",
    "big pharma", "5g", "politics"
}

# Tags to explicitly keep (even if borderline)
explicitly_allowed = {
    "abortion", "cannabis", "meditation and prayer", "sustainable living"
}

# Convert to topic-format for matching
unwanted_topics = {f"topic:\n{tag.lower()}" for tag in unwanted_keywords if tag.lower() not in explicitly_allowed}

# Load CSV
df = pd.read_csv("scraped_data.csv")

def contains_unwanted_topic(tag_field):
    if pd.isna(tag_field):
        return False
    tag_field = tag_field.lower()
    return any(unwanted in tag_field for unwanted in unwanted_topics)

# Filter out rows with unwanted tags
filtered_df = df[~df["tags"].fillna("").apply(contains_unwanted_topic)]

# Save the filtered dataset
filtered_df.to_csv("filtered_scraped_data.csv", index=False)
print(f"✅ Saved filtered data with {len(filtered_df)} rows to 'filtered_scraped_data.csv'")
