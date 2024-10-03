from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def compute_article_embeddings(articles):
    abstracts = [article['abstract'] for article in articles]
    embeddings = model.encode(abstracts)
    return embeddings

def content_based_recommendations(user_articles, all_articles, top_n=5):
    user_embeddings = compute_article_embeddings(user_articles)
    all_embeddings = compute_article_embeddings(all_articles)

    user_profile = np.mean(user_embeddings, axis=0)
    similarities = cosine_similarity([user_profile], all_embeddings)[0]

    # Get indices of top similar articles
    top_indices = similarities.argsort()[-top_n:][::-1]

    return [all_articles[i] for i in top_indices]

def collaborative_filtering(user_article_matrix, user_id, top_n=5):
    user_similarities = cosine_similarity(user_article_matrix)
    user_similarity_scores = user_similarities[user_id]

    # Get indices of top similar users
    similar_users = user_similarity_scores.argsort()[-top_n-1:-1][::-1]

    recommendations = []
    for similar_user in similar_users:
        user_articles = user_article_matrix[similar_user]
        recommendations.extend([i for i, val in enumerate(user_articles) if val > 0])

    # Remove duplicates and articles the user has already interacted with
    recommendations = list(set(recommendations) - set(user_article_matrix[user_id].nonzero()[0]))

    return recommendations[:top_n]