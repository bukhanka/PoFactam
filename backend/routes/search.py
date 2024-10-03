from flask import Blueprint, request, jsonify
from models import Article

search_bp = Blueprint('search', __name__)

@search_bp.route('/', methods=['POST'])
def search():
    query = request.json.get('query', '')
    
    # Search in the database
    articles = Article.query.filter(
        (Article.title.ilike(f'%{query}%')) |
        (Article.abstract.ilike(f'%{query}%')) |
        (Article.full_text.ilike(f'%{query}%'))
    ).all()
    
    # Convert to dictionary for JSON response
    articles_data = []
    for article in articles:
        publication_date = article.publication_date.isoformat() if article.publication_date else None
        
        articles_data.append({
            'id': article.id,
            'title': article.title,
            'authors': article.authors.split(', '),
            'abstract': article.abstract,
            'publicationDate': publication_date,
            'relevance': article.relevance or 0,
            'arxiv_id': article.arxiv_id
        })
    
    return jsonify(articles_data)