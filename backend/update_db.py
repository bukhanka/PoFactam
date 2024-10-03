from app import app, db
from models import User, Article, SearchHistory, user_favorites

def update_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("Database schema updated successfully.")

if __name__ == "__main__":
    update_db()