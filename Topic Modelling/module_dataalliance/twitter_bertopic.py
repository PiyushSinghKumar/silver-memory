import gensim.corpora as corpora
import pandas as pd
import re
from bertopic import BERTopic
from gensim.models.coherencemodel import CoherenceModel
from sentence_transformers import SentenceTransformer

from data_storage import retrieve_twitter_data


# Get twitter data
df = retrieve_twitter_data()
df = df.loc[df.duplicated(subset=['text'])==False]

# Create a list of tweets
docs = df["lemmatized_string"].to_list()

# model
sentence_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")#, device="cuda"
topic_model = BERTopic(language="english",calculate_probabilities=True, verbose=True,n_gram_range=(1, 2),top_n_words=10,embedding_model=sentence_model,nr_topics=10)#,nr_topics=5
topics, probs = topic_model.fit_transform(docs)

# visualize topics
topic_model.visualize_barchart(top_n_topics=11)

# Preprocess Documents
documents = pd.DataFrame({"Document": docs,
                          "ID": range(len(docs)),
                          "Topic": topics})
documents_per_topic = documents.groupby(['Topic'], as_index=False).agg({'Document': ' '.join})
cleaned_docs = topic_model._preprocess_text(documents_per_topic.Document.values)

# Extract vectorizer and analyzer from BERTopic
vectorizer = topic_model.vectorizer_model
analyzer = vectorizer.build_analyzer()

# Extract features for Topic Coherence evaluation
words = vectorizer.get_feature_names()
tokens = [analyzer(doc) for doc in cleaned_docs]
dictionary = corpora.Dictionary(tokens)
corpus = [dictionary.doc2bow(token) for token in tokens]
topic_words = [[words for words, _ in topic_model.get_topic(topic)] 
               for topic in range(len(set(topics))-1)]

# append the topics to the dataframe
for i in topic_words:
  for j in i:
    if j=='':
      i.remove(j)

# Evaluate
coherence_model = CoherenceModel(topics=topic_words, 
                                 texts=tokens, 
                                 corpus=corpus,
                                 dictionary=dictionary, 
                                 coherence='u_mass')
coherence = coherence_model.get_coherence()
print(f'Coherence score: {coherence}')
      
# Joining coherence scores to original dataframe
df_topic = pd.DataFrame({'topic': topics, 'document': docs})
df.reset_index(inplace=True)
df['topic'] = df_topic['topic']
df['document'] = df_topic['document']

# see distribution
df['topic'].value_counts()