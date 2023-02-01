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
import pandas as pd
import seaborn as sns

from data_storage import retrieve_newspaper_data
from data_storage import retrieve_twitter_data

# %% [markdown]
# #### Data preparation

# %%
# Data
df_news = retrieve_newspaper_data()
df_twitter = retrieve_twitter_data()

df_news['Dominant_Topic'] = df_news['Dominant_Topic'].astype(int)

# %%
# creating topics translation
twitter_topics = {0: 'Covid tests', 1: 'Vaccination', 2: 'Covid news', 
                  3: 'How people are feeling', 4: 'Booster vaccination', 5: 'Corona measures'}

news_topics = {0: 'Covid mortality', 1: 'Politics', 2: 'Global food crisis', 3: 'Economy', 
               4: 'Student life', 5: 'Back to office life', 6: 'Vaccination', 7: 'Covid news',
               8: 'Corona measures', 9: 'Testing covid in youngsters'}

# %%
# appending topics title to dataframe
df_news['topic'] = df_news['Dominant_Topic'].map(lambda x: news_topics[x])
df_twitter['topic'] = df_twitter['Dominant_Topic'].map(lambda x: twitter_topics[x])

# %%
df_twitter['topic'].count()

# %% [markdown]
# #### Visualization

# %%
df_twitter['topic'].value_counts()

# %%
(40223+33884)/df_twitter.shape[0]

# %%
df_news['topic'].value_counts()

# %%
71/df_news.shape[0]

# %%
for topic in df_twitter['topic'].unique():
    pol = df_twitter.loc[df_twitter['topic'] == topic,'polarity'].mean()
    print(f'{topic}: {pol}')

# %%
for topic in df_news['topic'].unique():
    pol = df_news.loc[df_news['topic'] == topic,'polarity'].mean()
    print(f'{topic}: {pol}')

# %%
df_twitter.loc[df_twitter['topic'] == 'How people are feeling', 'sentiment'].value_counts()

# %%
#define data
data = [8205, 5870, 3558]
labels = ['Neutral', 'Positive', 'Negative']

#define Seaborn color palette to use
colors = sns.color_palette('pastel')[0:5]

#create pie chart
plt.pie(data, labels = labels, colors = colors, autopct='%.0f%%')
plt.title('Distribution of sentiment in "How people are feeling"')
plt.show()

# %%
df_news.loc[df_news['topic'] == 'Vaccination', 'sentiment'].value_counts()

# %%
#define data
data = [10, 39, 22]
labels = ['Neutral', 'Positive', 'Negative']

#define Seaborn color palette to use
colors = sns.color_palette('pastel')[0:5]

#create pie chart
plt.pie(data, labels = labels, colors = colors, autopct='%.0f%%')
plt.title('Distribution of sentiment in newspaper "Vaccination"')
plt.show()

# %%
df_twitter.loc[(df_twitter['topic']=='Vaccination') | (df_twitter['topic']=='Booster vaccination'), 'sentiment'].value_counts()

# %%
#define data
data = [24247, 28218, 21642]
labels = ['Neutral', 'Positive', 'Negative']

#define Seaborn color palette to use
colors = sns.color_palette('pastel')[0:5]

#create pie chart
plt.pie(data, labels = labels, colors = colors, autopct='%.0f%%')
plt.title('Distribution of sentiment in twitter "Vaccination"')
plt.show()
