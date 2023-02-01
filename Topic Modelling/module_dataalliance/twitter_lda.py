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
import gensim.corpora as corpora
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pickle 
import pyLDAvis
import pyLDAvis.gensim_models
import seaborn as sns
import tqdm
from gensim.models import CoherenceModel
from wordcloud import WordCloud

from data_storage import retrieve_twitter_data

# %%
df = retrieve_twitter_data()

# %% [markdown]
# #### Create corpus, dictionary

# %%
# Create Corpus
texts = df['lemmatized_text'].values

# Create Dictionary
id2word = corpora.Dictionary(texts)

# Term Document Frequency
corpus = [id2word.doc2bow(text) for text in texts]

# %% [markdown]
# # LDA
# Hyperparameters:
# - Alpha - higher means documents are assumed to be made up of more topics - try 0.1
# - Beta - controls distribution of words per topic, higher means topics have more words
#
# *default = 1.0 for both*

# %%
# Build LDA model
lda_model = gensim.models.LdaMulticore(corpus=corpus,
                                       id2word=id2word,
                                       num_topics=6, 
                                       random_state=100,
                                       chunksize=100,
                                       passes=2,
                                       per_word_topics=True)

# %% [markdown]
# #### Coherence scores
# The overall coherence score of a topic is the average of the distances between words.
# For u_mass the closer to 0 the better. It is a logarithmic function.

# %%
# Compute Coherence Score - 'c_v' is the best coherence score, but slow
#                         - 'u_mass' requires corpus
coherence_model_lda = CoherenceModel(model=lda_model,
                                     corpus=corpus,
                                     texts=texts,
                                     dictionary=id2word,
                                     coherence='u_mass') 

coherence_lda = coherence_model_lda.get_coherence()

print('\nCoherence Score: ', coherence_lda)

# %% [markdown]
# #### Visualization

# %%
pyLDAvis.enable_notebook()
LDAvis_prepared = pyLDAvis.gensim_models.prepare(lda_model, corpus, id2word)
LDAvis_prepared

# %% [markdown]
# #### Interpretation of results per topic
# 1. Covid health (symptom, feel, bad, long, sick)
# 2. Covid politics (government, public, official, lockdown, people)
# 3. Covid measures (mask, wear, infection, high, rate, variant)
# 4. Unninterpretable
# 5. Covid vaccine (vaccine, child, booster, risk, dose, study)
# 6. Covid results (test, case, positive, death, new, day, report, daily, rise)
# 7. Covid conspiracy (virus, tell, try, lie, wonder, policy, fake)
# 8. Unninterpretable
# 9. Covid vaccine (vaccine, update, kid, young, vaccination, booost, pfizer)
# 10. Unninterpretable

# %% [markdown]
# ## Save the topics and interpretation in the dataframe

# %%
df_copy = df.copy()


# %%
def format_topics_sentences(ldamodel=lda_model, corpus=corpus, texts=df):
    # Init output
    sent_topics_df = pd.DataFrame()

    # Get main topic in each document
    for i, row in enumerate(ldamodel[corpus]):
        row = sorted(row, key=lambda x: (x[1]), reverse=True)
        # Get the Dominant topic, Perc Contribution and Keywords for each document
        for j, (topic_num, prop_topic) in enumerate(row):
            if j == 0:  # => dominant topic
                wp = ldamodel.show_topic(topic_num)
                topic_keywords = ", ".join([word for word, prop in wp])
                sent_topics_df = sent_topics_df.append(pd.Series([int(topic_num), round(prop_topic,4), topic_keywords]), ignore_index=True)
            else:
                break
    sent_topics_df.columns = ['Dominant_Topic', 'Perc_Contribution', 'Topic_Keywords']

    return(sent_topics_df)

df_dominant_topic = format_topics_sentences(ldamodel=lda_model, corpus=corpus, texts=df["lemmatized_text"])

# Format
df_dominant_topic = df_dominant_topic.reset_index()
df_dominant_topic.drop(['index'], axis=1, inplace=True)

# %%
# merge dataframes
final_df = pd.concat([df_copy.reset_index(drop=True), df_dominant_topic.reset_index(drop=True)], axis=1)

# %% [markdown]
# ## Save final dataframe

# %%
final_df.to_parquet(os.getcwd()+'/data_storage/data/twitter_data.parquet.gzip', compression='gzip')

# %% [markdown]
# # Hyperparameter tuning

# %% [markdown]
# #### Elbow method to decide K number of clusters

# %%
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


# %%
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

# %% [markdown]
# #### Tune parameters alpha and eta

# %%
# Set number of topics based on elbow method result
k = 6


# %%
def optimize_lda(k):
    results = []

    # Alpha parameter
    alpha = list(np.arange(0.01, 1, 0.3))
    alpha.append('symmetric')
    alpha.append('asymmetric')

    # Beta parameter
    beta = list(np.arange(0.01, 1, 0.3))
    beta.append('symmetric')
    
    for a in alpha:
        for b in beta:
            lda_model = gensim.models.LdaMulticore(corpus=corpus,
                                    id2word=id2word,
                                    num_topics=k, 
                                    random_state=100,
                                    chunksize=100,
                                    passes=2,
                                    per_word_topics=True,
                                    alpha=a,
                                    eta=b
                                    )

            coherence_model_lda = CoherenceModel(model=lda_model,
                                                corpus=corpus,
                                                texts=texts,
                                                dictionary=id2word,
                                                coherence='u_mass') 

            # get coherence value
            coherence_lda = coherence_model_lda.get_coherence()

            # save results
            results_dict = {'alpha': a,
                            'beta': b,
                            'K': k,
                            'Coherence score': coherence_lda}
            
            results.append(results_dict)
    
    return results


# %%
optimization_results = optimize_lda(6)

# %% [markdown]
# #### Save model

# %%
from gensim.test.utils import datapath

# Save model to disk.
temp_file = datapath("model")
lda.save(temp_file)

# Load a potentially pretrained model from disk.
lda = LdaModel.load(temp_file)


# %% [markdown]
# #### More hyperparameter tunning (don't have the machine for it)

# %%
# supporting function
def compute_coherence_values(corpus, dictionary, k, a, b):
    
    lda_model = gensim.models.LdaMulticore(corpus=corpus,
                                           id2word=dictionary,
                                           num_topics=k, 
                                           random_state=100,
                                           chunksize=100,
                                           passes=2,
                                           alpha=a,
                                           eta=b)
    
    coherence_model_lda = CoherenceModel(model=lda_model,
                                        corpus=corpus,
                                        texts=texts,
                                        dictionary=id2word,
                                        coherence='u_mass')
    
    return coherence_model_lda.get_coherence()


# %%
grid = {}
grid['Validation_Set'] = {}

# Alpha parameter
alpha = list(np.arange(0.01, 1, 0.3))
alpha.append('symmetric')
alpha.append('asymmetric')

# Beta parameter
beta = list(np.arange(0.01, 1, 0.3))
beta.append('symmetric')

# Validation sets
num_of_docs = len(corpus)
corpus_sets = [gensim.utils.ClippedCorpus(corpus, int(num_of_docs*0.75)), corpus]
corpus_title = ['75% Corpus', '100% Corpus']
model_results = {'Validation_Set': [],
                 'Topics': [],
                 'Alpha': [],
                 'Beta': [],
                 'Coherence': []
                }

# Can take a long time to run
if 1 == 1:
    pbar = tqdm.tqdm(total=540)
    
    # iterate through validation corpuses
    for i in range(len(corpus_sets)):
        # iterate through alpha values
        for a in alpha:
            # iterare through beta values
            for b in beta:
                # get the coherence score for the given parameters
                cv = compute_coherence_values(corpus=corpus_sets[i], dictionary=id2word, 
                                                k=k, a=a, b=b)
                # Save the model results
                model_results['Validation_Set'].append(corpus_title[i])
                model_results['Topics'].append(k)
                model_results['Alpha'].append(a)
                model_results['Beta'].append(b)
                model_results['Coherence'].append(cv)
                
                pbar.update(1)
    pd.DataFrame(model_results).to_csv(os.getcwd()+'/models/lda_tuning_results.csv', index=False)
    pbar.close()

# %%
# Read results
df_results = pd.read_csv(os.getcwd()+'/models/lda_tuning_results.csv')

df_results
