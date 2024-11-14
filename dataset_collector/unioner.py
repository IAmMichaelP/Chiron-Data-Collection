import pandas as pd
import re

df = pd.read_csv(r"C:\xampp\htdocs\GitHub\Chiron\dataset_collector\dataset1.csv")

print(df.head(100))
# Define a function to add 'https://' if the link doesn't start with it
def edit_content(content):
    content = re.sub(r'\s+', ' ', content).strip()
    return content

# Apply the function to the 'links' column
df['content'] = df['content'].apply(edit_content)

# Save the updated DataFrame back to a CSV file

# df.to_csv('./dataset_collector/chiron.csv', index=False)
df.to_csv('chiron.csv', mode='a', index=False, header=False)
