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

#%%
!wget http://mallet.cs.umass.edu/dist/mallet-2.0.8.zip
!unzip mallet-2.0.8.zip
os.environ['MALLET_HOME'] = '/content/mallet-2.0.8'
mallet_path = '/content/mallet-2.0.8/bin/mallet'

#%%

# Data
df = retrieve_newspaper_data()

# Create Corpus
texts = df['lemmatized_text'].values
# Create Dictionary
id2word = corpora.Dictionary(texts)
# Term Document Frequency
corpus = [id2word.doc2bow(text) for text in texts]

# Model
ldamallet = gensim.models.wrappers.LdaMallet(mallet_path, corpus=corpus, num_topics=10, id2word=id2word)

# Compute Coherence Score
coherence_model_ldamallet = CoherenceModel(model=ldamallet, texts=texts, dictionary=id2word, coherence='u_mass')
coherence_ldamallet = coherence_model_ldamallet.get_coherence()
print('\nCoherence Score: ', coherence_ldamallet)

# Visualization
# Wordcloud for each topic
cols = [color for name, color in mcolors.TABLEAU_COLORS.items()]  # more colors: 'mcolors.XKCD_COLORS'

cloud = WordCloud(background_color='white',
                  width=2500,
                  height=1800,
                  max_words=10,
                  colormap='tab10',
                  color_func=lambda *args, **kwargs: cols[i],
                  prefer_horizontal=1.0)

topics = ldamallet.show_topics(formatted=False)

fig, axes = plt.subplots(2, 5, figsize=(10,10), sharex=True, sharey=True)

for i, ax in enumerate(axes.flatten()):
    fig.add_subplot(ax)
    topic_words = dict(topics[i][1])
    cloud.generate_from_frequencies(topic_words, max_font_size=300)
    plt.gca().imshow(cloud)
    plt.gca().set_title('Topic ' + str(i), fontdict=dict(size=16))
    plt.gca().axis('off')


plt.subplots_adjust(wspace=0, hspace=0)
plt.axis('off')
plt.margins(x=0, y=0)
plt.tight_layout()
plt.show()

# pydavis
mallet_model = gensim.models.wrappers.ldamallet.malletmodel2ldamodel(ldamallet)
pyLDAvis.enable_notebook()
vis = pyLDAvis.gensim.prepare(mallet_model, corpus, dictionary=mallet_model.id2word)
vis

# hyperparameter tuning
def compute_coherence_values_mallet(dictionary, corpus, texts, limit, start=2, step=3):
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
    coherence_values_mallet = []
    model_list_mallet = []
    for num_topics in range(start, limit, step):
        model_mallet = gensim.models.wrappers.LdaMallet(mallet_path, corpus=corpus, num_topics=num_topics, id2word=id2word)
        model_list_mallet.append(model_mallet)
        coherencemodel = CoherenceModel(model=model_mallet, texts=texts, dictionary=dictionary, coherence='u_mass')
        coherence_values_mallet.append(coherencemodel.get_coherence())

    return model_list_mallet, coherence_values_mallet

# Can take a long time to run.
model_list_mallet, coherence_values_mallet = compute_coherence_values_mallet(dictionary=id2word, corpus=corpus, texts=texts, start=5, limit=100, step=5)

# Show graph
limit=100; start=5; step=5;
x = range(start, limit, step)
plt.plot(x, coherence_values_mallet)
plt.xlabel("Num Topics")
plt.ylabel("Coherence score")
plt.legend(("coherence_values"), loc='best')
plt.show()

# Print the coherence scores
for m, cv in zip(x, coherence_values_mallet):
    print("Num Topics =", m, " has Coherence Value of", round(cv, 4))

# Add model 
def format_topics_sentences(ldamodel=ldamallet, corpus=corpus, texts=df):
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

    # Add original text to the end of the output
    contents = pd.Series(df["text"])
    #sent_topics_df = pd.concat([sent_topics_df], axis=1)
    return(sent_topics_df)
df_topic_sents_keywords = format_topics_sentences(ldamodel=ldamallet, corpus=corpus, texts=df["lemmatized_text"])

# Format
df_dominant_topic = df_topic_sents_keywords.reset_index()
df_dominant_topic.columns = ['Document_No', 'Dominant_Topic', 'Topic_Perc_Contrib', 'Keywords']

# merge dataframes
final_df = pd.concat([df.reset_index(drop=True), df_dominant_topic.reset_index(drop=True)], axis=1)

# save dataframe
final_df.to_parquet(os.getcwd()+'/data_storage/data/newspaper_data.parquet.gzip', compression='gzip')