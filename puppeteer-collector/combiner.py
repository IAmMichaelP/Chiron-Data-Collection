import os
import pandas as pd

# Define the root directory as the current directory (puppeteer-collector)
root_directory = os.getcwd()  # This gets the current working directory

# Output file for consolidated data
output_file = "consolidated-data.csv"

# List to hold all DataFrames
dataframes = []

# Walk through all directories and subdirectories
for dirpath, dirnames, filenames in os.walk(root_directory):
    for filename in filenames:
        if filename == "scraped-data.csv":
            # Construct the full file path
            file_path = os.path.join(dirpath, filename)
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path)
            # Append the DataFrame to the list
            dataframes.append(df)
            print(f"Processed {file_path}: {len(df)} rows")

# Concatenate all DataFrames into a single DataFrame
if dataframes:
    consolidated_df = pd.concat(dataframes, ignore_index=True)
    # Save the consolidated DataFrame to a new CSV file
    consolidated_df.to_csv(output_file, index=False)
    print(f"Consolidation complete. Data saved to {output_file}")
else:
    print("No 'scraped-data.csv' files found.")