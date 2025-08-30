import nltk
import pandas as pd
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from collections import Counter
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

# Download NLTK resources (only needed once)
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Download NLTK resources (only needed once)
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

data = r"C:\Users\agaro\Documents\GitHub\Chiron\dataset1.csv"

df = pd.DataFrame(data)

# Initialize the WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

# Function to remove punctuation
def remove_punctuation(text):
    # Check if the input is a string
    if isinstance(text, str):
        punctuationfree = "".join([i for i in text if i not in string.punctuation and i not in ["'", '"', '—']])
        return punctuationfree
    else:
        # Return an empty string or the original value for non-string inputs
        return ""

# Function to preprocess text
def preprocess_text(text):
    # Remove punctuation
    text = remove_punctuation(text)
    # Convert to lowercase
    text = text.lower()
    # Tokenize the text
    tokens = word_tokenize(text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    # Lemmatize the tokens
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return tokens

# Apply preprocessing to the 'title' column
df['msg_tokenized'] = df['content'].apply(preprocess_text)

# Display the preprocessed tokens
print("Preprocessed Tokens:")
print(df['msg_tokenized'])

# Create a word pool (frequency distribution)
word_pool = Counter()
for tokens in df['msg_tokenized']:
    word_pool.update(tokens)

# Display the most common words
print("\nWord Pool (Top 20):")
print(word_pool.most_common(20))

# Generate a Word Cloud
wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_pool)

# Plot the Word Cloud
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title("Word Cloud of Most Frequent Words")
plt.show()