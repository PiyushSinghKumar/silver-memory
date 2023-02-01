import gensim
import gensim.corpora as corpora
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os
import pandas as pd
from gensim.models.coherencemodel import CoherenceModel
from top2vec import Top2Vec
from wordcloud import WordCloud
%matplotlib inline

from data_storage import retrieve_newspaper_data

# Data
df = retrieve_newspaper_data()

# Model
model_with_universal_encoder = Top2Vec(df['lemmatized_string'].values, embedding_model='universal-sentence-encoder')

#Viewing number of topics
model_with_universal_encoder.get_num_topics()

# Visualize
topic_words, word_scores, topic_scores, topic_nums = model_with_universal_encoder.search_topics(keywords=["covid"], num_topics=10)

longstring = []
i=0
while i < len(topic_words):
    #print(i)
    stringlong = ','.join(topic_words[i])
    longstring.append(stringlong)
    i=i+1

wordcloud = WordCloud(width = 1000, height = 500,background_color="black",  contour_width=3, contour_color='steelblue')
for num in range(0,len(longstring)):
  print("Topic number: ",num)
  wordcloud.generate(longstring[num])
  plt.figure(figsize = (8, 8), facecolor = None)
  plt.imshow(wordcloud)
  plt.axis("off")
  plt.tight_layout(pad = 0)
  plt.show()

# Extract features for Topic Coherence evaluation
tokens = df['lemmatized_text'].values
dictionary = corpora.Dictionary(tokens)
corpus = [dictionary.doc2bow(token) for token in tokens]

# Evaluate
coherence_model = CoherenceModel(topics=topic_words,
                                 #model = model_with_universal_encoder,
                                 texts=tokens, 
                                 corpus=corpus,
                                 dictionary=dictionary, 
                                 coherence='u_mass')
coherence = coherence_model.get_coherence()

print(f'Coherence Score for top2vec using newspaper data: {coherence}')