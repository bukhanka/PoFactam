import os
import sys
import logging
from datetime import timedelta, datetime
import random
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from download_nltk_data import download_nltk_data

# Call download_nltk_data before any other imports
download_nltk_data()

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, User, Article, SearchHistory
from routes.auth import auth_bp
from routes.search import search_bp
from routes.article import article_bp
from routes.user import user_bp
from services.search_service import search_articles
from nlp.summarizer import summarize_text
from services.arxiv_service import fetch_arxiv_papers

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'ml_mining_research.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(search_bp, url_prefix='/search')
app.register_blueprint(article_bp, url_prefix='/article')
app.register_blueprint(user_bp, url_prefix='/user')

@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception("An error occurred: %s", str(e))
    return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['POST'])
def search_articles():
    query = request.json.get('query', '')
    
    if query:
        articles = Article.query.filter(
            (Article.title.ilike(f'%{query}%')) |
            (Article.abstract.ilike(f'%{query}%')) |
            (Article.full_text.ilike(f'%{query}%'))
        ).all()
    else:
        articles = Article.query.all()
    
    logger.info(f"Search query: '{query}'. Found {len(articles)} articles.")
    
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

@app.route('/trigger_arxiv_fetch', methods=['POST'])
def trigger_arxiv_fetch():
    try:
        logger.info("Starting arXiv fetch process")
        papers = fetch_arxiv_papers()
        logger.info(f"Fetched {len(papers)} papers from arXiv")
        new_papers_count = 0
        for paper in papers:
            logger.debug(f"Processing paper: {paper['title']}")
            existing_paper = Article.query.filter_by(arxiv_id=paper['arxiv_id']).first()
            if not existing_paper:
                new_paper = Article(
                    title=paper['title'],
                    authors=', '.join(paper['authors']),
                    abstract=paper['abstract'],
                    arxiv_id=paper['arxiv_id'],
                    publication_date=paper['publication_date'],
                    full_text=paper['full_text']
                )
                db.session.add(new_paper)
                new_papers_count += 1
                logger.debug(f"Added new paper: {new_paper.title}")
                
                summary = summarize_text(new_paper.full_text)
                new_paper.summary = summary
                logger.debug(f"Generated summary for paper: {new_paper.title}")
        
        logger.info(f"Committing {new_papers_count} new papers to database")
        db.session.commit()
        total_papers = Article.query.count()
        logger.info(f"Added {new_papers_count} new papers. Total papers in database: {total_papers}")
        return jsonify({
            "message": f"Arxiv papers fetched and processed successfully. Added {new_papers_count} new papers.",
            "total_papers": total_papers
        }), 200
    except Exception as e:
        logger.exception("An error occurred while fetching Arxiv papers: %s", str(e))
        return jsonify({"error": str(e)}), 500

from collections import defaultdict

@app.route('/article/graph', methods=['GET'])
def get_article_graph():
    articles = Article.query.all()
    nodes = []
    links = []
    keyword_to_articles = defaultdict(set)
    
    # Create nodes for articles and extract keywords
    for article in articles:
        article_node = {
            "id": f"article_{article.id}",
            "group": 1,
            "label": article.title[:30] + "...",
            "title": article.title,
            "authors": article.authors,
            "abstract": article.abstract[:100] + "..." if article.abstract else "",
            "publication_date": article.publication_date.isoformat() if article.publication_date else None,
            "arxiv_id": article.arxiv_id
        }
        nodes.append(article_node)
        
        # Extract keywords from title and abstract
        text = f"{article.title} {article.abstract}"
        keywords = extract_keywords(text)
        
        # Map keywords to articles
        for keyword in keywords:
            keyword_to_articles[keyword].add(article.id)
    
    # Create links between articles based on shared keywords
    for keyword, article_ids in keyword_to_articles.items():
        for article_id1 in article_ids:
            for article_id2 in article_ids:
                if article_id1 < article_id2:  # Avoid duplicate links
                    links.append({
                        "source": f"article_{article_id1}",
                        "target": f"article_{article_id2}",
                        "value": 1,  # You can adjust this value based on the number of shared keywords
                        "label": keyword
                    })
    
    graph_data = {
        "nodes": nodes,
        "links": links
    }
    return jsonify(graph_data)

@app.route('/article/count', methods=['GET'])
def get_article_count():
    article_count = Article.query.count()
    return jsonify({'article_count': article_count})

@app.route('/database_status', methods=['GET'])
def database_status():
    try:
        article_count = Article.query.count()
        logger.info(f"Database status check: {article_count} articles found")
        return jsonify({
            "status": "ok",
            "article_count": article_count,
            "message": f"Database contains {article_count} articles."
        }), 200
    except Exception as e:
        logger.exception("An error occurred while checking database status: %s", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/populate_sample_data', methods=['POST'])
def populate_sample_data():
    try:
        # Check if the database is already populated
        article_count = Article.query.count()
        if article_count > 0:
            return jsonify({
                "message": f"Database already contains {article_count} articles. No new data added.",
                "article_count": article_count
            }), 200

        # Sample data
        sample_articles = [
            {
                "title": "Deep Learning in Mining",
                "authors": "John Doe, Jane Smith",
                "abstract": "This paper explores the applications of deep learning in the mining industry.",
                "publication_date": datetime(2023, 1, 15),
                "arxiv_id": "2301.12345"
            },
            {
                "title": "Machine Learning for Mineral Exploration",
                "authors": "Alice Johnson, Bob Williams",
                "abstract": "We present a novel machine learning approach for mineral exploration.",
                "publication_date": datetime(2023, 2, 20),
                "arxiv_id": "2302.67890"
            },
            {
                "title": "AI-driven Mining Operations Optimization",
                "authors": "Charlie Brown, Diana Clark",
                "abstract": "This study demonstrates how AI can optimize mining operations.",
                "publication_date": datetime(2023, 3, 10),
                "arxiv_id": "2303.11111"
            }
        ]

        # Add sample articles to the database
        for article_data in sample_articles:
            article = Article(**article_data)
            db.session.add(article)

        db.session.commit()

        return jsonify({"message": f"Added {len(sample_articles)} sample articles to the database."}), 200
    except Exception as e:
        logger.exception("An error occurred while populating sample data: %s", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/article/favorite', methods=['POST', 'DELETE'])
def handle_favorite_article():
    article_id = request.json.get('article_id')
    if not article_id:
        return jsonify({"error": "Article ID is required"}), 400

    article = Article.query.get(article_id)
    if not article:
        return jsonify({"error": "Article not found"}), 404

    if request.method == 'POST':
        # Add to favorites (you might want to associate this with a user in the future)
        article.is_favorite = True
        db.session.commit()
        return jsonify({"message": "Article added to favorites"}), 200
    elif request.method == 'DELETE':
        # Remove from favorites
        article.is_favorite = False
        db.session.commit()
        return jsonify({"message": "Article removed from favorites"}), 200

@app.route('/api/visualization-data', methods=['GET'])
def get_visualization_data():
    try:
        articles = Article.query.all()
        
        # Publications per month
        pub_per_month = defaultdict(int)
        for article in articles:
            if article.publication_date:
                month_key = article.publication_date.strftime('%Y-%m')
                pub_per_month[month_key] += 1
        
        # Research topics distribution
        vectorizer = TfidfVectorizer(stop_words='english', max_features=5)
        tfidf_matrix = vectorizer.fit_transform([article.abstract for article in articles if article.abstract])
        feature_names = vectorizer.get_feature_names_out()
        tfidf_sums = tfidf_matrix.sum(axis=0).A1
        top_topics = [feature_names[i] for i in tfidf_sums.argsort()[-5:][::-1]]
        topic_counts = [int(tfidf_sums[tfidf_sums.argsort()[-5:][i]]) for i in range(5)]
        
        # Citations over time (simulated data)
        current_year = datetime.now().year
        citations_over_time = {str(year): random.randint(50, 200) for year in range(current_year-5, current_year+1)}
        
        # Citations vs Publication Year
        citations_vs_year = [{'x': article.publication_date.year if article.publication_date else 0, 
                              'y': random.randint(0, 50)} for article in articles]
        
        # Research Impact (simulated data)
        research_impact = [{'x': random.randint(0, 100), 'y': random.randint(0, 100), 'r': random.randint(5, 25)} 
                           for _ in range(20)]
        
        return jsonify({
            'publicationsPerMonth': dict(pub_per_month),
            'researchTopics': {'labels': top_topics, 'data': topic_counts},
            'citationsOverTime': citations_over_time,
            'citationsVsYear': citations_vs_year,
            'researchImpact': research_impact
        }), 200
    except Exception as e:
        logger.exception("An error occurred while fetching visualization data: %s", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai-insights', methods=['GET'])
def get_ai_insights():
    try:
        articles = Article.query.all()
        
        # Trending topics
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,2), max_features=100)
        tfidf_matrix = vectorizer.fit_transform([article.abstract for article in articles if article.abstract])
        feature_names = vectorizer.get_feature_names_out()
        tfidf_sums = tfidf_matrix.sum(axis=0).A1
        trending_topics = [feature_names[i] for i in tfidf_sums.argsort()[-3:][::-1]]
        
        # Collaboration opportunities (simulated)
        collaborations = [
            f"Researchers from University {chr(65+i)} and Company {chr(88+i)} have complementary work in '{topic}'"
            for i, topic in enumerate(trending_topics)
        ]
        
        # Emerging fields (based on recent papers)
        recent_papers = sorted(articles, key=lambda x: x.publication_date or datetime.min, reverse=True)[:10]
        emerging_fields = [article.title.split(':')[0] for article in recent_papers[:2]]
        
        # Research gaps (simulated)
        research_gaps = [
            f"Limited studies on '{topic} Ethics' present an opportunity for impactful work"
            for topic in trending_topics
        ]
        
        insights = [
            f"Trending topic: '{trending_topics[0]}' has seen a significant increase in publications recently.",
            collaborations[0],
            f"Emerging field: '{emerging_fields[0]}' is showing rapid growth in citations.",
            research_gaps[0]
        ]
        
        return jsonify(insights), 200
    except Exception as e:
        logger.exception("An error occurred while generating AI insights: %s", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    try:
        # Get all articles
        articles = Article.query.all()
        
        if len(articles) < 2:
            return jsonify({"message": "Not enough articles for recommendations"}), 200

        # Create a TF-IDF vectorizer
        vectorizer = TfidfVectorizer(stop_words='english')
        
        # Fit and transform the articles' abstracts
        tfidf_matrix = vectorizer.fit_transform([article.abstract for article in articles if article.abstract])
        
        # Compute cosine similarity
        cosine_similarities = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        # Get top 5 recommendations for each article
        recommendations = []
        for i, article in enumerate(articles):
            similar_indices = cosine_similarities[i].argsort()[:-6:-1]  # Top 5 similar articles (excluding itself)
            similar_articles = [articles[index] for index in similar_indices if index != i]
            
            article_recommendations = []
            for similar_article in similar_articles:
                article_recommendations.append({
                    'id': similar_article.id,
                    'title': similar_article.title,
                    'authors': similar_article.authors.split(', '),
                    'abstract': similar_article.abstract[:200] + '...' if similar_article.abstract else '',
                    'publicationDate': similar_article.publication_date.isoformat() if similar_article.publication_date else None,
                    'similarity': float(cosine_similarities[i][similar_indices[similar_articles.index(similar_article)]])
                })
            
            recommendations.append({
                'article': {
                    'id': article.id,
                    'title': article.title
                },
                'recommendations': article_recommendations
            })
        
        return jsonify(recommendations), 200
    except Exception as e:
        logger.exception("An error occurred while generating recommendations: %s", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This will create the tables based on your models
    app.run(debug=True)