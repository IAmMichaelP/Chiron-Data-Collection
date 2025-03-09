import pandas as pd

# Step 1: Read the CSV file
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream:dataset_collector/unioner.py
input_file = r"C:\Users\agaro\Documents\GitHub\Chiron\dataset_collector\annotated_dataset4.csv"
=======
input_file = r"C:\Users\agaro\Documents\GitHub\Chiron\annotated_info_war.csv"
>>>>>>> Stashed changes:unioner.py
=======
input_file = r"C:\Users\agaro\Documents\GitHub\Chiron\annotated_info_war.csv"
>>>>>>> Stashed changes
=======
input_file = r"C:\Users\agaro\Documents\GitHub\Chiron\annotated_info_war.csv"
>>>>>>> Stashed changes
df = pd.read_csv(input_file)

# Step 2: Verify and select only the required columns
required_columns = ['link', 'title', 'annotation', 'content']

# Check if the required columns exist in the DataFrame
if all(column in df.columns for column in required_columns):
    df = df[required_columns]  # Select only the required columns
else:
    raise ValueError("The input CSV file does not contain the required columns: link, title, annotation, content.")

<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream:dataset_collector/unioner.py
# Step 3: Define the output file path
output_file = r"./dataset_collector/chiron_authentic.csv"
=======
# Step 3: Preprocess the 'content' column to remove newlines
df['content'] = df['content'].str.replace('\n', ' ', regex=True)  # Replace newlines with spaces
>>>>>>> Stashed changes:unioner.py
=======
# Step 3: Preprocess the 'content' column to remove newlines
df['content'] = df['content'].str.replace('\n', ' ', regex=True)  # Replace newlines with spaces
>>>>>>> Stashed changes
=======
# Step 3: Preprocess the 'content' column to remove newlines
df['content'] = df['content'].str.replace('\n', ' ', regex=True)  # Replace newlines with spaces
>>>>>>> Stashed changes

# Step 4: Define the output file path
output_file = r"./chiron_content.csv"

# Step 5: Check if the output file already exists
if not pd.io.common.file_exists(output_file):
    # If the file does not exist, write the DataFrame with headers
    df.to_csv(output_file, index=False)
else:
    # If the file exists, append the DataFrame without headers
    df.to_csv(output_file, mode='a', index=False, header=False)

print("Data processing complete. Check 'chiron_content.csv' for the results.")