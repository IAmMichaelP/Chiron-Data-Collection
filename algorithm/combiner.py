import pandas as pd
import os

# Step 1: Read the CSV file
input_file = r"dataset5.csv"
df = pd.read_csv(input_file)

# Step 2: Specify and verify the required columns
required_columns = ['link', 'title', 'health_annotation', 'content']
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    raise ValueError(f"The input CSV file is missing the required columns: {', '.join(missing_columns)}")

# Step 3: Select only the required columns
df = df[required_columns]

# Step 4: Preprocess the 'content' column to clean text
df['content'] = df['content'].str.replace('\n', ' ', regex=True)
df['content'] = df['content'].str.replace(r'\s+', ' ', regex=True)
df['content'] = df['content'].str.strip()

# Step 5: Define output file path
output_file = r"./general_dataset1.csv"

# Step 6: Write or append to the output CSV, only with required columns
if not os.path.exists(output_file):
    df.to_csv(output_file, index=False)  # Write with headers
else:
    df.to_csv(output_file, mode='a', index=False, header=False)  # Append without headers

print("Data processing complete. Check 'general_dataset.csv' for the results.")
