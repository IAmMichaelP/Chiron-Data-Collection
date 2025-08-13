import pandas as pd

input_file = r"dataset6.csv"
input_file2 = r"./batch4/dataset4.csv"
output_file = r"dataset7.csv"

# Read both CSV files
df1 = pd.read_csv(input_file)
df2 = pd.read_csv(input_file2)

# Create a dictionary from df2 with title as key and annotation as value
title_to_annotation = dict(zip(df2['title'], df2['annotation']))

# If df1 already has an annotation column and you want to preserve existing values
if 'annotation' in df1.columns:
    # Only update annotations where the title matches and the current annotation is empty
    mask = df1['title'].isin(title_to_annotation.keys()) & df1['annotation'].isna()
    df1.loc[mask, 'annotation'] = df1.loc[mask, 'title'].map(title_to_annotation)
else:
    # If no annotation column exists, create it
    df1['annotation'] = df1['title'].map(title_to_annotation)

# Filter rows where health_annotation == 1
filtered_df = df1[df1['health_annotation'] == 1]

# Save to new CSV
filtered_df.to_csv(output_file, index=False)
print(f"Filtered data with added annotations saved to {output_file}")