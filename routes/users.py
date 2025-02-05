from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Like, Restaurant

users_bp = Blueprint("users", __name__)

@users_bp.route("/me", methods=["GET"])
@jwt_required()
def get_user_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    # Get all restaurants the user has liked
    liked_restaurants = (
        Restaurant.query.join(Like).filter(Like.user_id == user_id).all()
    )

    return jsonify({
        "id": user.id,
        "username": user.username,
        "liked_restaurants": [
            {"id": r.id, "name": r.name} for r in liked_restaurants
        ]
    })
