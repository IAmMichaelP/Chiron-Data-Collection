import pandas as pd

# Step 1: Read the CSV file using pandas
df = pd.read_csv(r"C:\xampp\htdocs\GitHub\Chiron\dataset_collector\gma_new.csv")
# df = pd.read_csv(r"C:\xampp\htdocs\GitHub\Chiron\dataset_collector\exploded_eagleNews.csv")

# Step 2: Limit the DataFrame to the first 100 rows
# df = df.head(100)  # This will select only the first 100 rows
df = df.iloc[901:1001]
print(df.head(100))
        
# Step 4: Create a new DataFrame from the processed rows
exploded_df = pd.DataFrame(df)

# Step 5: Write the new exploded DataFrame to a CSV file
exploded_df.to_csv('./dataset_collector/chopped_dataset.csv', index=False)
