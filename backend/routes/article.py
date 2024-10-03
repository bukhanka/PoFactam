from flask import Blueprint, jsonify
from models import Article

article_bp = Blueprint('article', __name__)

@article_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    # Fetch some articles from the database
    recommendations = Article.query.limit(5).all()
    
    recommendations_data = []
    for article in recommendations:
        publication_date = article.publication_date.isoformat() if article.publication_date else None
        
        recommendations_data.append({
            'id': article.id,
            'title': article.title,
            'authors': article.authors.split(', '),
            'abstract': article.abstract,
            'publicationDate': publication_date,
            'relevance': article.relevance or 0
        })
    
    return jsonify(recommendations_data)

@article_bp.route('/graph', methods=['GET'])
def get_article_graph():
    # This is a placeholder implementation. You should implement the actual graph generation logic.
    graph_data = {
        "nodes": [
            {"id": "ML", "group": 1},
            {"id": "Mining", "group": 2},
            {"id": "Data Analysis", "group": 3}
        ],
        "links": [
            {"source": "ML", "target": "Mining"},
            {"source": "ML", "target": "Data Analysis"},
            {"source": "Mining", "target": "Data Analysis"}
        ]
    }
    return jsonify(graph_data)