from flask import Blueprint, jsonify

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
def get_user_profile():
    # Placeholder implementation
    return jsonify({"message": "User profile fetched successfully"}), 200