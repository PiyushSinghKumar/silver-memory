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
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud

from data_storage import retrieve_twitter_data

# %% [markdown]
# #### Getting the twitter test data

# %%
df = retrieve_twitter_data()

# %% [markdown]
# # EDA

# %% [markdown]
# ### Overview

# %%
df.head()

# %%
nr_tweets = df.shape[0]

original_values = (f"Originally we had {nr_tweets} tweets related to Covid-19\n"
                   f"Dates range from {df['created_at'].values.min()} to {df['created_at'].values.max()}")

print(original_values)

# %% [markdown]
# ### Check missing values

# %%
# Columns with missing values + Number of missing values
if df.columns.isna().sum() == 0:
    print('There are no missing values')
else:
    print('Detected')
    display(df.columns.isna().sum())

# %%
# Check for lemmatization without words
nr_tweets_empty = df.loc[df['lemmatized_string']==''].shape[0]
empty_values = f'There are {nr_tweets_empty} tweets with an empty string after lemmatization'

print(empty_values)

# %% [markdown]
# #### Drop missing tweets after lemmatization

# %%
# Filter out these tweets
df = df.loc[df['lemmatized_string']!='']

# %% [markdown]
# ###  Check for duplicates

# %%
unique_tweets = df.text.nunique()
duplicated_values = f"There are {nr_tweets - unique_tweets} duplicated tweets"

print(duplicated_values)

# %%
df_duplicates = df.loc[df.duplicated(subset=['text'])==True]

# %%
df_duplicates.head()

# %% [markdown]
# #### Wordcloud of duplicated tweets

# %%
# Start with one review:
text = " ".join(text for text in df_duplicates['clean_text'])

# Create and generate a word cloud image:
wordcloud = WordCloud(width=1800, height=700, max_words=100, background_color='white').generate(text)

# %%
# Display the generated image:
fig, ax = plt.subplots(figsize=[20,10])
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()

# %%
# Save the image
wordcloud.to_file("images/twitter_duplicates_wordcloud_cleantext.png")

# %% [markdown]
# #### Wordcloud of the lemmatized text

# %%
# Start with one review:
text = " ".join(text for sublist in df_duplicates['lemmatized_text'] for text in sublist)

# Create and generate a word cloud image:
wordcloud = WordCloud(width=1800, height=700, max_words=100, background_color='white').generate(text)

# %%
# Display the generated image:
fig, ax = plt.subplots(figsize=[20,10])
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()

# %%
# Save the image
wordcloud.to_file("images/twitter_duplicates_wordcloud_lemmatizedtext.png")

# %% [markdown]
# ### Drop Duplicates

# %%
df_ = df.loc[df.duplicated(subset=['text'])==False]

# %%
nr_tweets_ = df_.shape[0]

final_values = (f"In the end we are left with {nr_tweets_} tweets related to Covid-19\n"
                   f"Dates range from {df['created_at'].values.min()} to {df['created_at'].values.max()}")

print(final_values)

# %% [markdown]
# ## Distribution of dates

# %%
# Plot histogram
plt.figure(figsize=(18,6))
plot = sns.histplot(data=df_, x='created_at', bins=20)
plt.show()

# %%
# Save plot
fig = plot.get_figure()
fig.savefig('images/twitter_dates_hist.png')

# %%
perc_of_original = f"Percentage of original tweets: {round(100*(nr_tweets_/nr_tweets), 1)}%"

print(perc_of_original)

# %% [markdown]
# ## Wordclouds

# %%
# Start with one review:
text = " ".join(text for text in df_['clean_text'])

# Create and generate a word cloud image:
wordcloud = WordCloud(width=1800, height=700, max_words=100, background_color='white').generate(text)

# %%
# Display the generated image:
fig, ax = plt.subplots(figsize=[20,10])
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()

# %%
# Save the image
wordcloud.to_file("images/twitter_wordcloud_cleantext.png")

# %% [markdown]
# #### Wordcloud for lemmatized_text

# %%
# Start with one review:
text = " ".join(text for sublist in df_['lemmatized_text'] for text in sublist)

# Create and generate a word cloud image:
wordcloud = WordCloud(width=1800, height=700, max_words=100, background_color='white').generate(text)

# %%
# Display the generated image:
fig, ax = plt.subplots(figsize=[20,10])
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()

# %%
# Save the image
wordcloud.to_file("images/twitter_wordcloud_lemmatizedtext.png")

# %% [markdown]
# ## Save stats about the data and the transformations made

# %%
list_of_insights = [original_values, empty_values, duplicated_values, final_values, perc_of_original]
insights = '\n\n'.join(list_of_insights)

print(insights)

# %%
# Save insights to a text file
text_file = open(os.getcwd() + "/images/twitter_lda.txt", "w")
text_file.write(insights)
text_file.close()

# %% [markdown]
# ## Save new dataframe

# %%
df_.to_parquet(os.getcwd()+'/data_storage/data/twitter_data.parquet.gzip', compression='gzip')
