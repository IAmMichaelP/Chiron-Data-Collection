import pandas as pd

# Load the CSV file into a pandas DataFrame
df = pd.read_csv(r"C:\Users\agaro\Documents\GitHub\Chiron\dataset_collector\naturalnews.csv")

# Define a function to add 'https://' if the link doesn't start with it
def add_https(link):
    if not link.startswith('http://') and not link.startswith('https://'):
        return 'https://naturalnews.com/' + link
    return link

# Apply the function to the 'links' column
df['link'] = df['link'].apply(add_https)

# Save the updated DataFrame back to a CSV file
df.to_csv('naturalnews_updated.csv', index=False)

print("CSV file updated with 'https://' added to the links!")
