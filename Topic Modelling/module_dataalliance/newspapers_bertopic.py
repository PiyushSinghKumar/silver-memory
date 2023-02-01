import gensim.corpora as corpora
import pandas as pd
import tensorflow_hub
from bertopic import BERTopic
from gensim.models.coherencemodel import CoherenceModel

from data_storage import retrieve_newspaper_data

# Data
df = retrieve_newspaper_data()
docs = df["lemmatized_string"].to_list()

# Model
embedding_model = tensorflow_hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
topic_model = BERTopic(verbose=True, embedding_model=embedding_model,n_gram_range=(1, 2),nr_topics='auto')
topics, _ = topic_model.fit_transform(docs)

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

# Evaluate
coherence_model = CoherenceModel(topics=topic_words, 
                                 texts=tokens, 
                                 corpus=corpus,
                                 dictionary=dictionary, 
                                 coherence='u_mass')
coherence = coherence_model.get_coherence()
print(f'Coherence score: {coherence}')

# Visualization
topic_model.visualize_barchart(top_n_topics=11)