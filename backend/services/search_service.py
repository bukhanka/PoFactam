import arxiv
from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import numpy as np

stop_words = set(stopwords.words('english'))

def search_articles(query, filters=None, max_results=50):
    # Create a client with the default configuration
    client = arxiv.Client()

    # Prepare the search query
    search = arxiv.Search(
        query=query,
        max_results=max_results * 2,  # Fetch more results for re-ranking
        sort_by=arxiv.SortCriterion.Relevance,
        sort_order=arxiv.SortOrder.Descending,
    )

    # Perform the search
    results = list(client.results(search))

    # Process the results
    articles = []
    for result in results:
        article = {
            'id': result.entry_id,
            'title': result.title,
            'authors': [author.name for author in result.authors],
            'abstract': result.summary,
            'publicationDate': result.published.strftime("%Y-%m-%d"),
            'url': result.pdf_url,
        }
        articles.append(article)

    # Re-rank articles using BM25
    tokenized_query = [word.lower() for word in word_tokenize(query) if word.lower() not in stop_words]
    tokenized_corpus = [[word.lower() for word in word_tokenize(doc['title'] + ' ' + doc['abstract']) if word.lower() not in stop_words] for doc in articles]

    bm25 = BM25Okapi(tokenized_corpus)
    bm25_scores = bm25.get_scores(tokenized_query)

    for article, score in zip(articles, bm25_scores):
        article['relevance'] = score

    # Sort articles by relevance score
    articles.sort(key=lambda x: x['relevance'], reverse=True)

    return articles[:max_results]