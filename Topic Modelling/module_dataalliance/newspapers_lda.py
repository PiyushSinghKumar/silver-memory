import gensim
import gensim.corpora as corpora
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os
import pandas as pd
import pyLDAvis.gensim
from gensim.models.coherencemodel import CoherenceModel
from wordcloud import WordCloud
%matplotlib inline

from data_storage import retrieve_newspaper_data

# Data
df = retrieve_newspaper_data()

# Create Corpus
texts = df['lemmatized_text'].values
# Create Dictionary
id2word = corpora.Dictionary(texts)
# Term Document Frequency
corpus = [id2word.doc2bow(text) for text in texts]

# Model
lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                           id2word=id2word,
                                           num_topics=10, 
                                           random_state=100,
                                           update_every=1,
                                           chunksize=100,
                                           passes=10,
                                           alpha='auto',
                                           per_word_topics=True)

# Compute Coherence Score
coherence_model_lda = CoherenceModel(model=lda_model, texts=data_lemmatized, dictionary=id2word, coherence='u_mass')
coherence_lda = coherence_model_lda.get_coherence()
print('\nCoherence Score: ', coherence_lda)

# Visualization
pyLDAvis.enable_notebook()
vis = pyLDAvis.gensim.prepare(lda_model, corpus, dictionary=lda_model.id2word)
vis

# Hyperparameter tuning
def compute_coherence_values_lda(dictionary, corpus, texts, limit, start=2, step=3):
    """
    Compute c_v coherence for various number of topics

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
    coherence_values_lda = []
    model_list_lda = []
    for num_topics in range(start, limit, step):
        lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,id2word=id2word,num_topics=num_topics,random_state=100,update_every=1,chunksize=100,passes=10,alpha='auto',per_word_topics=True)
        #model = gensim.models.wrappers.LdaMallet(mallet_path, corpus=corpus, num_topics=num_topics, id2word=id2word)
        model_list_lda.append(lda_model)
        coherencemodel = CoherenceModel(model=lda_model, texts=texts, dictionary=dictionary, coherence='u_mass')
        coherence_values_lda.append(coherencemodel.get_coherence())

    return model_list_lda, coherence_values_lda

# Can take a long time to run.
model_list_lda, coherence_values_lda = compute_coherence_values_lda(dictionary=id2word, corpus=corpus, texts=texts, start=5, limit=100, step=5)

# Show graph
limit=100; start=5; step=5;
x = range(start, limit, step)
plt.plot(x, coherence_values_lda)
plt.xlabel("Num Topics")
plt.ylabel("Coherence score")
plt.legend(("coherence_values"), loc='best')
plt.show()

# Print the coherence scores
for m, cv in zip(x, coherence_values_lda):
    print("Num Topics =", m, " has Coherence Value of", round(cv, 4))