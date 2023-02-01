import numpy as np
import pandas as pd
from contextualized_topic_models.models.ctm import CombinedTM
from contextualized_topic_models.utils.data_preparation import TopicModelDataPreparation
from contextualized_topic_models.utils.preprocessing import WhiteSpacePreprocessingStopwords
from contextualized_topic_models.evaluation.measures import Coherence, InvertedRBO,CoherenceUMASS

from data_storage import retrieve_newspaper_data

# Get newspaper data
df = retrieve_newspaper_data()

# prepare data
from nltk.corpus import stopwords as stop_words
nltk.download('stopwords')
stopwords = list(set(stop_words.words('english')))

documents = df["clean_text"].tolist()
sp = WhiteSpacePreprocessingStopwords(documents, stopwords_list=stopwords)
preprocessed_documents, unpreprocessed_corpus, vocab, x = sp.preprocess()

# Model
tp = TopicModelDataPreparation("paraphrase-distilroberta-base-v2")
training_dataset = tp.fit(text_for_contextual=unpreprocessed_corpus, text_for_bow=preprocessed_documents)

num_topics =10
ctm = CombinedTM(bow_size=len(tp.vocab), contextual_size=768, n_components=num_topics, num_epochs=20)
ctm.fit(training_dataset) # run the model

corpus = [d.split() for d in preprocessed_documents]
coh = CoherenceUMASS(ctm.get_topic_lists(10), corpus)
print("coherence score CTM for newspaper data:", coh.score())

# hyperparameter tunning
corpus = [d.split() for d in preprocessed_documents]

num_topics = [5, 10, 15, 20]
num_runs = 5

best_topic_coherence = -999
best_num_topics = 0
for n_components in num_topics:
  for i in range(num_runs):
    print("num topics:", n_components, "/ num run:", i)
    ctm = CombinedTM(bow_size=len(tp.vocab), contextual_size=768, 
                     n_components=n_components, num_epochs=50)
    ctm.fit(training_dataset) # run the model
    coh = CoherenceUMASS(ctm.get_topic_lists(10), corpus)
    coh_score = coh.score()
    print("coherence score:", coh_score)
    if best_topic_coherence < coh_score:
      best_topic_coherence = coh_score
      best_num_topics = n_components
    print("current best coherence", best_topic_coherence, "/ best num topics", best_num_topics)
