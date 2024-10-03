from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    favorite_articles = db.relationship('Article', secondary='user_favorites', backref='favorited_by')
    search_history = db.relationship('SearchHistory', backref='user', lazy=True)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    authors = db.Column(db.Text, nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    full_text = db.Column(db.Text)
    summary = db.Column(db.Text)
    publication_date = db.Column(db.DateTime, default=datetime.utcnow)
    arxiv_id = db.Column(db.String(50), unique=True)
    relevance = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_favorite = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Article {self.title}>'

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    query = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

user_favorites = db.Table('user_favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True)
)