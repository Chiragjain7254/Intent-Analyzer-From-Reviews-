# -*- coding: utf-8 -*-
"""INTENT_PREDICTIVE__MODEL.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1sqs6OzS8vJHPmF9o8oOS1yBVqHhDkIGg

# 1. Data Loading and Exploration

1.1 Importing Libraries and Load the Data
"""

import pandas as pd
import nltk
from nltk.corpus import stopwords
import gensim
from gensim import corpora
from gensim.models import LdaModel
import string
from sklearn.feature_extraction.text import CountVectorizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import SMOTE
from collections import Counter
!pip install pyLDAvis
import pyLDAvis.gensim
import pyLDAvis.gensim_models as gensimvis
import pyLDAvis

# Load the data
data_path = '/content/dataset.csv'
data = pd.read_csv(data_path)
print(f"Dataset shape: {data.shape}")
print(data.head())

"""# 2. Data Preprocessing

2.1 Handle Missing Values
"""

# Handle missing values
data.dropna(subset=['rating', 'rating title', 'Review text', 'Review date', 'Date of Experience', 'rating_procesed'], inplace=True)
print(f"Dataset shape after dropping null values: {data.shape}")

"""2.2 Replace NaN Values in Text Columns

"""

# Replace NaN values with empty strings in text columns to avoid issues during text processing
text_columns = ['rating title', 'Review text', 'Review date', 'Date of Experience']
data[text_columns] = data[text_columns].fillna('')

"""2.3 Data Types and Basic Information


"""

# Data types of the features
print(data.dtypes)
len(data)

"""# 3. Data Analysis and Visualization

3.1 Analyze 'Rating' Column
"""

#Distinct values of 'rating' and its count

print(f"Rating value count: \n{data['rating'].value_counts()}")


# Analyzing 'rating' column
data['rating_procesed'].value_counts().plot.bar(color='red')
plt.title('Rating distribution count')
plt.xlabel('Ratings')
plt.ylabel('Count')
plt.show()

"""3.2 Analyze 'Rating' Column in Pie Chart

"""

print(f"Rating value count - percentage distribution: \n{round(data['rating_procesed'].value_counts()/data.shape[0]*100,2)}")
fig = plt.figure(figsize=(7,7))
colors = ('red', 'green', 'blue', 'orange', 'yellow')
wp = {'linewidth': 1, "edgecolor": 'black'}
tags = data['rating_procesed'].value_counts()/data.shape[0]
explode = (0.1, 0.1, 0.1, 0.1, 0.1)
tags.plot(kind='pie', autopct="%1.1f%%", shadow=True, colors=colors, startangle=90, wedgeprops=wp, explode=explode, label='Percentage wise distribution of rating')
plt.show()

"""3.3 Analyze 'Review Text' Column

"""

# Analyzing 'Review text' column
data['length'] = data['Review text'].apply(len)
# Descriptive statistics of the 'length' column
print(data['length'].describe())

"""3.4 Histogram of review lengths

"""

# Histogram of review lengths
plt.hist(data['length'], bins=50, edgecolor='black')
plt.title('Distribution of Review Lengths')
plt.xlabel('Length of Review')
plt.ylabel('Frequency')
plt.show()

"""3.3 Wordcloud Visualization

3.3.1 Wordcloud for All Reviews
"""

# Wordcloud for all reviews
cv = CountVectorizer(stop_words='english')
words = cv.fit_transform(data['Review text'])
reviews = " ".join([review for review in data['Review text']])
wc = WordCloud(background_color='white', max_words=50)
plt.figure(figsize=(10, 10))
plt.imshow(wc.generate(reviews))
plt.title('Wordcloud for all reviews', fontsize=10)
plt.axis('off')
plt.show()

"""3.3.2 Wordcloud for High and Low Ratings

"""

# Unique words in each rating category
low_ratings_reviews = " ".join([review for review in data[data['rating_procesed'] <= 3]['Review text']]).lower().split()
high_ratings_reviews = " ".join([review for review in data[data['rating_procesed'] > 3]['Review text']]).lower().split()
unique_low = " ".join([x for x in low_ratings_reviews if x not in high_ratings_reviews])
unique_high = " ".join([x for x in high_ratings_reviews if x not in low_ratings_reviews])

wc = WordCloud(background_color='white', max_words=50)
plt.figure(figsize=(10, 10))
plt.imshow(wc.generate(unique_low))
plt.title('Wordcloud for low ratings reviews', fontsize=10)
plt.axis('off')
plt.show()

wc = WordCloud(background_color='white', max_words=50)
plt.figure(figsize=(10, 10))
plt.imshow(wc.generate(unique_high))
plt.title('Wordcloud for high ratings reviews', fontsize=10)
plt.axis('off')
plt.show()

"""# 4. Text Preprocessing

4.1 Download and Load Stopwords
"""

# Download stopwords
nltk.download('stopwords')
stop_words = stopwords.words('english')

"""4.2 Preprocess Text Data

"""

# Preprocess the text data
def preprocess(text):
    text = text.lower()  # Lowercase
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    tokens = [word for word in text.split() if word not in stop_words]  # Tokenize and remove stopwords
    return tokens

data['tokens'] = data['Review text'].apply(preprocess)

"""# 5. Topic Modeling Using LDA

5.1 Create Dictionary and Corpus
"""

# Create a dictionary and corpus for LDA
dictionary = corpora.Dictionary(data['tokens'])
corpus = [dictionary.doc2bow(tokens) for tokens in data['tokens']]

"""5.2 Build LDA Model

"""

# Set parameters for LDA
num_topics = 10
passes = 15

# Build LDA model
lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, passes=passes)

# Print topics with their probabilities
topics = lda_model.print_topics(num_words=200)
for topic in topics:
    print(topic)

"""5.3 Map Topics to Intents

"""

# Assuming data, lda_model, and corpus are already defined and processed correctly

# Function to map topic ID to intent
def map_topic_to_intent(topic):
    intent_mapping = {
        0: "General Setup and Recommendations",
        1: "Technical Issues - Bugs and Errors",
        2: "Customer Support Experience",
        3: "Account Management and Digital Banking",
        4: "Transaction Issues",
        5: "Access and Availability Issues",
        6: "Feature Requests and Improvements",
        7: "Positive Recommendations and Reviews",
        8: "Invoice Management",
        9: "Fraud and Security Concerns"
    }
    return intent_mapping.get(topic, "Unknown")  # Default to "Unknown" if topic ID not found

# Function to get topic distribution for corpus
def get_topic_distribution(model, corpus):
    topics = []
    for doc in corpus:
        topic_distribution = model.get_document_topics(doc)
        topics.append(sorted(topic_distribution, key=lambda x: x[1], reverse=True)[0][0])
    return topics

# Assign intents to reviews based on the most likely topic
data['topic'] = get_topic_distribution(lda_model, corpus)
data['intent'] = data['topic'].apply(map_topic_to_intent)

# Display the first few rows with intents
print(data[['Review text', 'tokens', 'topic', 'intent']].head())

"""5.4 Review Tokens

"""

# Print all tokens for the first few reviews
print("First few reviews and their tokens:")
for index, row in data.head().iterrows():
    print(f"Review {index + 1}: {row['Review text']}")
    print(f"Tokens: {row['tokens']}\n")

# Print tokens for a specific review
specific_index = 0  # Change this to the index of the review you want to inspect
print(f"Specific Review: {data.loc[specific_index, 'Review text']}")
print(f"Tokens: {data.loc[specific_index, 'tokens']}")

"""# 6. Feature Extraction and Model Training

6.1 TF-IDF Vectorization
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from collections import Counter
import pandas as pd

# Create a TF-IDF Vectorizer
tfidf = TfidfVectorizer(max_features=5000, stop_words='english')

# Transform the review text into TF-IDF features
X = tfidf.fit_transform(data['Review text'])

# Target variable
y = data['intent']

# Check the class distribution before applying SMOTE
class_counts = Counter(y)
print(f"Class distribution before SMOTE: {class_counts}")

# Apply SMOTE to balance the dataset with k_neighbors set to 1
smote = SMOTE(random_state=42, k_neighbors=1)
X_resampled, y_resampled = smote.fit_resample(X, y)

# Check the new class distribution
resampled_class_counts = Counter(y_resampled)
print(f"Resampled dataset shape: {resampled_class_counts}")

"""6.2 Train-Test Split Using
Random Forest Model

"""

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from collections import Counter



# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

# Train the Random Forest model
model = RandomForestClassifier(
    n_estimators=100,         # Increased number of trees for better performance
    random_state=2,          # For reproducibility
    max_depth=10,           # Allowing trees to grow fully
    min_samples_split=12,      # Minimum samples to split
    min_samples_leaf=8,       # Minimum samples at leaf
    max_features='log2',      # Number of features to consider when looking for the best split
    bootstrap=True,           # Use bootstrap samples
    oob_score=False,          # Do not use out-of-bag samples for validation
    criterion='gini',         # Use Gini impurity for split quality
    class_weight='balanced'         # All classes have the same weight
)
model.fit(X_train, y_train)

"""6.3 Model Evaluation

"""

# Predict and Evaluate
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
print(f"Accuracy: {accuracy_score(y_test, y_pred)}")

"""# SOME MORE ADDITIONAL CHANGES HERE TO EVALUATE MORE EASILY OUR RESULTS

# 7. Add Intent and Topic Columns to the Dataset

7.1 Assign Intents and Topics
"""

# Assign intents to reviews based on the most likely topic
def get_topic_distribution(model, corpus):
    topics = []
    for doc in corpus:
        topic_distribution = model.get_document_topics(doc)
        topics.append(sorted(topic_distribution, key=lambda x: x[1], reverse=True)[0][0])
    return topics

data['topic'] = get_topic_distribution(lda_model, corpus)
data['intent'] = data['topic'].apply(map_topic_to_intent)

# Add intent number
data['intent_number'] = data['topic']

"""7.2 Display the Modified DataFrame

"""

# Display the first few rows with intents
print(data[['Review text', 'tokens', 'topic', 'intent', 'intent_number']].head())

"""7.3 Create a New Dataset with Additional Columns

"""

# Create a new DataFrame with the additional columns
new_data = data.copy()

# Save the new dataset to an Excel file
new_data.to_excel('/content/new_dataset.xlsx', index=False)

"""7.4  Save and Download the New Dataset to a EXCEL File

"""

# Provide a button to download the new dataset
from google.colab import files
files.download('/content/new_dataset.xlsx')

"""7.5 Save and Download the New Dataset to a CSV File


"""

# Save the new dataset to a CSV file
new_data.to_csv('/content/new_dataset.csv', index=False)

### 6.2 Provide a Download Button in Colab
from google.colab import files

# Provide a button to download the new dataset
files.download('/content/new_dataset.csv')

"""7.6 Display the First and Last 5 Rows of the New DataFrame

"""

# Display the first 5 rows of the new dataset
print("First 5 rows of the new dataset:")
print(new_data.head())

# Display the last 5 rows of the new dataset
print("Last 5 rows of the new dataset:")
print(new_data.tail())

"""# Load the New Dataset

"""

import pandas as pd

# Load the new dataset
new_data_path = '/content/new_dataset.csv'
new_data = pd.read_csv(new_data_path)
print(f"New dataset shape: {new_data.shape}")

"""#7.2 Visualize the Percentage of Each Intent

"""

import matplotlib.pyplot as plt

# Calculate the percentage of each intent
intent_counts = new_data['intent'].value_counts()
intent_percentages = intent_counts / len(new_data) * 100

# Plot the bar graph
plt.figure(figsize=(12, 6))
intent_percentages.plot(kind='bar', color=plt.cm.Paired.colors)
plt.title('Percentage Distribution of Intents')
plt.xlabel('Intent')
plt.ylabel('Percentage')
plt.xticks(rotation=45)  # Rotate x-labels for better readability
plt.grid(axis='y', linestyle='--', alpha=0.7)  # Add horizontal grid lines
for i, v in enumerate(intent_percentages):
    plt.text(i, v + 0.5, f"{v:.2f}%", ha='center', va='bottom', fontsize=9)  # Display percentage on top of each bar
plt.tight_layout()
plt.show()

"""# 7.3 Visualize the Count of Each Intent


"""

import seaborn as sns

# Plot the bar chart
plt.figure(figsize=(12, 6))
sns.barplot(x=intent_counts.index, y=intent_counts.values, palette='Paired')
plt.title('Count of Each Intent')
plt.xlabel('Intent')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')
plt.show()

"""#  Analyze Review Length by Intent"""

# Calculate the length of each review
new_data['length'] = new_data['Review text'].apply(len)

# Plot the distribution of review lengths by intent
plt.figure(figsize=(12, 6))
sns.boxplot(x='intent', y='length', data=new_data, palette='Paired')
plt.title('Distribution of Review Lengths by Intent')
plt.xlabel('Intent')
plt.ylabel('Length of Review')
plt.xticks(rotation=45, ha='right')
plt.show()

"""# Save and Download Visualizations"""

# Save the pie chart
pie_chart_path = '/content/intent_pie_chart.png'
plt.figure(figsize=(10, 7))
intent_percentages.plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
plt.title('Percentage Distribution of Intents')
plt.ylabel('')
plt.savefig(pie_chart_path)
plt.show()

# Save the bar chart
bar_chart_path = '/content/intent_bar_chart.png'
plt.figure(figsize=(12, 6))
sns.barplot(x=intent_counts.index, y=intent_counts.values, palette='Paired')
plt.title('Count of Each Intent')
plt.xlabel('Intent')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')
plt.savefig(bar_chart_path)
plt.show()

# Provide download buttons for the visualizations
files.download(pie_chart_path)
files.download(bar_chart_path)

# Visualize the topics using pyLDAvis
vis_data = gensimvis.prepare(lda_model, corpus, dictionary)
pyLDAvis.display(vis_data)

"""#                       THE END"""