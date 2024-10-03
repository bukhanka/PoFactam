import os
from app import app, db
from models import User, Article, SearchHistory, user_favorites

def init_db():
    with app.app_context():
        # Create the database directory if it doesn't exist
        db_dir = os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
        os.makedirs(db_dir, exist_ok=True)

        # Create all tables
        db.create_all()
        
        print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()