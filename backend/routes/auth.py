from flask import Blueprint, request, jsonify
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "Username already exists"}), 400

    new_user = User(username=username, password=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        # For now, just return a success message
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401