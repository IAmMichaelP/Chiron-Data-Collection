import pandas as pd
import ast

# Step 1: Read the CSV file using pandas
df = pd.read_csv(r"C:\xampp\htdocs\GitHub\Chiron\dataset_collector\eagleNews.csv")

# Step 2: Function to split a string by commas and create an array
def parse_string_to_array(val):
    # Strip leading/trailing brackets or spaces, then split by commas
    array = val.strip("[]").split(",")
    # Strip extra spaces or quotes from each element
    return [item.strip().strip("'").strip('"') for item in array]

# Step 3: Apply the parsing function to both 'link' and 'title' columns
df['link'] = df['link'].apply(parse_string_to_array)
df['title'] = df['title'].apply(parse_string_to_array)

# Step 4: Manually iterate through each row, match the index of link and title,
# and create new rows for each matched pair, stopping at the shorter length
rows = []
for index, row in df.iterrows():
    links = row['link']
    titles = row['title']

    # Match each link with the corresponding title until one array is exhausted
    min_length = min(len(links), len(titles))
    for i in range(min_length):
        rows.append({'link': links[i], 'title': titles[i], 'annotation': 1})

    # Optional: You can log a warning for mismatched array lengths
    if len(links) != len(titles):
        print(f"Warning: Row {index} has mismatched arrays.")
        print(f"Links: {links}")
        print(f"Titles: {titles}")
        
# Step 5: Create a new DataFrame from the processed rows
exploded_df = pd.DataFrame(rows)

# Step 6: Write the new exploded DataFrame to a CSV file
exploded_df.to_csv('exploded_eagleNews.csv', index=False)
# exploded_df.to_csv('exploded_file.csv', mode='a', index=False, header=False)

print("Data processing complete. Check 'exploded_file.csv' for the results.")

# Add debugging print statements to check the data
print("\nDebugging Information:")
print("First row link array:", df['link'][0])
print("First row title array:", df['title'][0])
print("Number of rows in final dataframe:", len(exploded_df))