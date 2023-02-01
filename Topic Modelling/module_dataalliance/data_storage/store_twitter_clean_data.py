# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     custom_cell_magics: kql
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: Python 3.9.13 ('dataalliance')
#     language: python
#     name: python3
# ---

# %%
import gensim
import neattext.functions as nfx
import nltk
import os
import pandas as pd
import re
import spacy
from gensim.utils import simple_preprocess
from nltk.corpus import stopwords
from textblob import TextBlob

from utils import read_records, create_collection

# %% [markdown]
# ## Get twitter data previously stored in mongodb

# %%
collection = create_collection("covid-19_final")
tweets = [tweet for tweet in read_records(collection)]
df = pd.DataFrame(tweets)

# %% [markdown]
# #### Remove unwanted columns and set data types

# %%
df['created_at'] = pd.to_datetime(df['created_at'])
df['id'] = pd.to_numeric(df['_id'])
df.drop(['withheld', '_id'], axis=1, inplace=True)

# reorder columns
cols = df.columns.to_list()
cols = cols[-1:] + cols[:-1]
df = df[cols]

# %% [markdown]
# ## Add new columns with useful transformations

# %% [markdown]
# #### Data cleaning 
# + remove mentions & userhandles
# + remove multiple spaces & new lines
# + remove hashtags
# + remove stop words
# + remove punctuation
# + remove urls
# + remove emojis
# + remove special char
# + lowercase all text

# %%
# remove hashtags 
df['clean_text'] = df.text.apply(nfx.remove_hashtags)

# remove users handle 
df['clean_text'] = df['clean_text'].apply(lambda x: nfx.remove_userhandles(x))
df['clean_text'] = df['clean_text'].map(lambda x: re.sub('@[A-Za-z0-9\.-_:]+', '', x))

# remove multiple spaces
df['clean_text'] = df['clean_text'].apply(nfx.remove_multiple_spaces)

# remove urls
df['clean_text'] = df['clean_text'].apply(nfx.remove_urls)
df['clean_text'] = df['clean_text'].map(lambda x: re.sub('(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w\.-]*)', '', x))

# remove emojis
df['clean_text'] = df['clean_text'].apply(nfx.remove_emojis)

# remove punctuation
df['clean_text'] = df['clean_text'].apply(nfx.remove_puncts)
df['clean_text'] =  df['clean_text'].map(lambda x: re.sub('[:;,\.!?]', '', x))
df['clean_text'] =  df['clean_text'].map(lambda x: re.sub('_', ' ', x))

# remove stop words
df['clean_text'] = df['clean_text'].apply(nfx.remove_stopwords)

# lowercasing
df['clean_text'] = df['clean_text'].map(lambda x: x.lower())

# removing RT (retweets)
df['clean_text'] = df['clean_text'].map(lambda x: re.sub('RT', '', x))

# remove new lines
df['clean_text'] = df['clean_text'].map(lambda x: re.sub('\n', ' ', x))

# %% [markdown]
# #### Tokenization

# %%
df['tokenized_text'] = df['clean_text'].map(lambda x: gensim.utils.simple_preprocess(str(x), deacc=True))

# %% [markdown]
# #### Bigrams and Trigrams

# %%
words = df['tokenized_text'].values.tolist()

# build the models
bigram = gensim.models.Phrases(words, min_count=5, threshold=100) # higher threshold fewer phrases.
trigram = gensim.models.Phrases(bigram[words], threshold=100)

# Faster way to get a sentence clubbed as a trigram/bigram
bigram_mod = gensim.models.phrases.Phraser(bigram)
trigram_mod = gensim.models.phrases.Phraser(trigram)

# Form Bigrams
df['tokenized_text'] = df['tokenized_text'].map(lambda x: bigram_mod[x])

# Form Trigrams
df['tokenized_text'] = df['tokenized_text'].map(lambda x: trigram_mod[x])

# %% [markdown]
# #### Remove stopwords

# %%
nltk.download('stopwords')

stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use', 'the', 'of', 'and', 'in', 'for', 'to'])

df['no_stopwords_text'] = df['tokenized_text'].map(lambda x: [word for word in simple_preprocess(str(x)) 
                                                              if word not in stop_words])

# %% [markdown]
# #### Lemmatization

# %%
# Initialize spacy 'en' model, keeping only tagger component (for efficiency)
nlp = spacy.load("en_core_web_sm", disable=['parser', 'ner'])

# Do lemmatization keeping only noun, adj, vb, adv
df['lemmatized_text'] = df['no_stopwords_text'].map(lambda x: [token.lemma_ for token in nlp(" ".join(x)) 
                                                        if token.pos_ in ['NOUN', 'ADJ', 'VERB', 'ADV']])

# column with lemmatized as a string
df['lemmatized_string'] = [' '.join(map(str, l)) for l in df['lemmatized_text']]


# %% [markdown]
# #### Sentiment Analysis

# %%
def get_sentiment(text):
    '''Returns a dictionary with the sentiment, 
    polarity and subjectivy of the text passed'''
    blob = TextBlob(text)
    sentiment_polarity = blob.sentiment.polarity
    sentiment_subjectivity = blob.sentiment.subjectivity

    if sentiment_polarity > 0:
        sentiment_label = 'Positive'
    elif sentiment_polarity < 0:
        sentiment_label = 'Negative'
    else:
        sentiment_label = 'Neutral'

    result = {'polarity':sentiment_polarity,
              'subjectivity':sentiment_subjectivity,
              'sentiment':sentiment_label}
    
    return result


# %%
# create column with the sentiment scores
df['sentiment_results'] = df['clean_text'].apply(get_sentiment)

# unpack the column into a column for each score
df = df.join(pd.json_normalize(df['sentiment_results']))

# drop original column
df.drop(['sentiment_results'], axis=1, inplace=True)

# %%
df.head()

# %% [markdown]
# ## Save dataframe to parquet

# %%
df.to_parquet(os.getcwd()+'/data/twitter_data.parquet.gzip', compression='gzip')
