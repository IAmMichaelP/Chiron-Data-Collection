import pandas as pd

# Step 1: Read the CSV file
input_file = r"annotated_goop.csv"
df = pd.read_csv(input_file)

# Step 2: Verify and select only the required columns
required_columns = ['link', 'title', 'annotation', 'content']

# Check if the required columns exist in the DataFrame
if all(column in df.columns for column in required_columns):
    df = df[required_columns]  # Select only the required columns
else:
    raise ValueError("The input CSV file does not contain the required columns: link, title, annotation, content.")

# Step 3: Preprocess the 'content' column to remove newlines and extra spaces
df['content'] = df['content'].str.replace('\n', ' ', regex=True)  # Replace newlines with spaces
df['content'] = df['content'].str.replace('\s+', ' ', regex=True)  # Replace multiple spaces with a single space
df['content'] = df['content'].str.strip()  # Remove leading and trailing spaces

# Step 4: Define the output file path
output_file = r"./dataset3.csv"

# Step 5: Check if the output file already exists
if not pd.io.common.file_exists(output_file):
    # If the file does not exist, write the DataFrame with headers
    df.to_csv(output_file, index=False)
else:
    # If the file exists, append the DataFrame without headers
    df.to_csv(output_file, mode='a', index=False, header=False)

print("Data processing complete. Check 'dataset1.csv' for the results.")