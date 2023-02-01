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

from data_storage import retrieve_newspaper_data

# %%
df = retrieve_newspaper_data()

# %%
df.head()

# %% [markdown]
# # EDA

# %%
# Number of articles
nr_articles = df.shape[0]


original_values = (f"We have {nr_articles} tweets related to Covid-19\n"
                   f"Dates range from {df['dates'].values.min()} to {df['dates'].values.max()}")

print(original_values)

# %%
# Check missing values
if df.columns.isna().sum() == 0:
    missing_values = 'There are no missing values'
    print(missing_values)
else:
    missing_values = df.columns.isna().sum()
    display(missing_values)

# %%
# Check for duplicates
unique_articles = df.text.nunique()
duplicated_values = f"There are {nr_articles-unique_articles} duplicated articles"

print(duplicated_values)

# %% [markdown]
# #### Wordclouds

# %%
# Create a WordCloud object
wordcloud = WordCloud(width = 1000, height = 500,background_color="white",  contour_width=3, contour_color='steelblue')

# Generate a word cloud
wordcloud.generate(','.join(list(df['clean_text'].values)))

# Visualize the word cloud
wordcloud.to_image()

# %%
# Save the image
wordcloud.to_file("images/newspaper_wordcloud_text.png")

# %%
# Create a WordCloud object
wordcloud = WordCloud(width = 1000, height = 500,background_color="white",  contour_width=3, contour_color='steelblue')

# Generate a word cloud
wordcloud.generate(','.join(list(df['lemmatized_string'].values)))

# Visualize the word cloud
wordcloud.to_image()

# %%
# Save the image
wordcloud.to_file("images/newspaper_wordcloud_lemmatizedtext.png")

# %% [markdown]
# ## Save stats about the data and the transformations made

# %%
list_of_insights = [original_values, duplicated_values, missing_values]
insights = '\n\n'.join(list_of_insights)

print(insights)

# %%
# Save insights to a text file
text_file = open(os.getcwd() + "/images/newspaper_lda.txt", "w")
text_file.write(insights)
text_file.close()
