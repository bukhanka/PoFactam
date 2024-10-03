from transformers import pipeline
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text, max_length=150, min_length=50):
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text']
    return summary

def extractive_summarize(text, num_sentences=3):
    sentences = sent_tokenize(text)
    stop_words = set(stopwords.words('english'))

    # Create sentence similarity matrix
    sentence_similarity_matrix = np.zeros((len(sentences), len(sentences)))
    for i in range(len(sentences)):
        for j in range(len(sentences)):
            if i != j:
                sentence_similarity_matrix[i][j] = sentence_similarity(sentences[i], sentences[j], stop_words)

    # Use PageRank algorithm to rank sentences
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_matrix)
    scores = nx.pagerank(sentence_similarity_graph)

    # Sort sentences by score and select top sentences
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    summary_sentences = [ranked_sentences[i][1] for i in range(min(num_sentences, len(ranked_sentences)))]

    return ' '.join(summary_sentences)

def sentence_similarity(sent1, sent2, stop_words):
    words1 = [word.lower() for word in sent1.split() if word.lower() not in stop_words]
    words2 = [word.lower() for word in sent2.split() if word.lower() not in stop_words]

    all_words = list(set(words1 + words2))

    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    for w in words1:
        vector1[all_words.index(w)] += 1
    for w in words2:
        vector2[all_words.index(w)] += 1

    return 1 - cosine_distance(vector1, vector2)