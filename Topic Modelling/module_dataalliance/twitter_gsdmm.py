# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     custom_cell_magics: kql
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3.9.13 ('dataalliance')
#     language: python
#     name: python3
# ---

# +
import gensim
import gensim.corpora as corpora
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pickle 
import pyLDAvis
import seaborn as sns
import tqdm
from gensim.models import CoherenceModel
from gsdmm import MovieGroupProcess
from wordcloud import WordCloud

from data_storage import retrieve_twitter_data
# -

df = retrieve_twitter_data()

# #### Model

# +
# Create Corpus
texts = df['lemmatized_text'].values

# Create Dictionary
id2word = corpora.Dictionary(texts)

# Term Document Frequency
corpus = [id2word.doc2bow(text) for text in texts]

# create variable containing length of dictionary/vocab
vocab_length = len(id2word)

# initialize GSDMM
gsdmm = MovieGroupProcess(K=10, alpha=0.1, beta=0.3, n_iters=15)

# fit GSDMM model
y = gsdmm.fit(texts, vocab_length)
# -

# #### Topics

# +
# print number of documents per topic
doc_count = np.array(gsdmm.cluster_doc_count)
print('Number of documents per topic :', doc_count)

# Topics sorted by the number of document they are allocated to
top_index = doc_count.argsort()[-10:][::-1]
print('Most important clusters (by number of docs inside):', top_index)

# define function to get top words per topic
def top_words(cluster_word_distribution, top_cluster, values):
    for cluster in top_cluster:
        sort_dicts = sorted(cluster_word_distribution[cluster].items(), key=lambda k: k[1], reverse=True)[:values]
        print("\nCluster %s : %s"%(cluster, sort_dicts))

# get top words in topics
top_words(gsdmm.cluster_word_distribution, top_index, 20)


# -

# #### Coherence score

# define function to get words in topics (to compute coherence score)
def get_topics_lists(model, top_clusters, n_words):
    '''
    Gets lists of words in topics as a list of lists.
    
    model: gsdmm instance
    top_clusters:  numpy array containing indices of top_clusters
    n_words: top n number of words to include
    
    '''
    # create empty list to contain topics
    topics = []

    # check for empty topics and remove then
    null_topics = (doc_count == 0).sum()
    if null_topics != 0:
        top_clusters = top_clusters[:-null_topics]
    
    # iterate over top n clusters
    for cluster in top_clusters:
        #create sorted dictionary of word distributions
        sorted_dict = sorted(model.cluster_word_distribution[cluster].items(), key=lambda k: k[1], reverse=True)[:n_words]
        
        #create empty list to contain words
        topic = []
        
        #iterate over top n words in topic
        for k,v in sorted_dict:
            #append words to topic list
            topic.append(k)
            
        #append topics to topics list    
        topics.append(topic)
    
    return topics


# get topics to feed to coherence model
topics_sample = get_topics_lists(gsdmm, top_index, 20)

# +
# evaluate model using Topic Coherence score
cm_gsdmm = CoherenceModel(topics=topics_sample,
                          dictionary=id2word, 
                          corpus=corpus, 
                          texts=texts, 
                          coherence='u_mass') # 'c_v' for precise scores

# get coherence value
coherence_gsdmm = cm_gsdmm.get_coherence() 

print('Coherence Score: ', coherence_gsdmm)
# -

# ## Optimize Number of K -> adapt code for GSDMM

# +
from gensim.models.ldamodel import LdaModel

def compute_coherence_values(dictionary, corpus, texts, limit, start=2, step=3):
    """
    Compute u_mass coherence for various number of topics

    Parameters:
    ----------
    dictionary : Gensim dictionary
    corpus : Gensim corpus
    texts : List of input texts
    limit : Max num of topics

    Returns:
    -------
    model_list : List of LDA topic models
    coherence_values : Coherence values corresponding to the LDA model with respective number of topics
    """
    coherence_values = []
    model_list = []
    for num_topics in range(start, limit, step):
        model=LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics)
        model_list.append(model)
        coherencemodel = CoherenceModel(model=model, texts=texts, dictionary=dictionary, coherence='u_mass')
        coherence_values.append(coherencemodel.get_coherence())

    return model_list, coherence_values


# +
model_list, coherence_values = compute_coherence_values(dictionary=id2word, corpus=corpus, texts=texts, start=2, limit=20, step=4)

# Show graph
import matplotlib.pyplot as plt
limit=20; start=2; step=4;
x = range(start, limit, step)
plt.plot(x, coherence_values)
plt.xlabel("Num Topics")
plt.ylabel("Coherence score")
plt.legend(("coherence_values"), loc='best')
plt.show()
# -

# #### Analyse best models topics -> To be worked on
#
# - Topic 0: 
# - Topic 1: Spiritual / Emotional
# - Topic 2: Political: Syria, Sudan, Iran, Qatar, President, Parliament, Army, Republic
# - Topic 3: Sports and misc.
# - Topic 4: Stopwords
# - Topic 5: Advertising / Commercial
# - Topic 6: Political: Syria, Damascus, Tehran, Army, Asad, etc.
# - Topic 7: Religious
# - Topic 8: Stopwords
# - Topic 9: Sexual: Sex, Whore, Bitch, Video, Film, Violence (few documents: 327)
