import pandas as pd

# Load the CSV file into a pandas DataFrame
df = pd.read_csv(r"C:\Users\agaro\Documents\GitHub\Chiron\chiron.csv", delimiter=',')

print(df.head(10))
# Convert 'content' column to strings
df['content'] = df['content'].astype(str)

# Print the first 10 rows
print(df.head(10))

# Access a specific row (like index 217) safely
index_to_check = 216
if index_to_check in df.index:
    content = df['content'][index_to_check]
    print(f'Here is the content at index {index_to_check}: {content}')
else:
    print(f'Index {index_to_check} is out of bounds in the DataFrame.')


# # Define a function to add 'https://' if the link doesn't start with it
# def add_https(link):
#     if not link.startswith('http://') and not link.startswith('https://'):
#         return 'https://naturalnews.com/' + link
#     return link

# # Apply the function to the 'links' column
# df['link'] = df['link'].apply(add_https)

# # Save the updated DataFrame back to a CSV file
# df.to_csv('naturalnews_updated.csv', index=False)

# print("CSV file updated with 'https://' added to the links!")
