from flask import Blueprint, request, jsonify
from models import Restaurant, Like, db
from flask_jwt_extended import jwt_required, get_jwt_identity

restaurants_bp = Blueprint("restaurants", __name__)

@restaurants_bp.route("/", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([
        {"id": r.id, "name": r.name, "description": r.description}
        for r in restaurants
    ])

@restaurants_bp.route("/like", methods=["POST"])
@jwt_required()
def like_restaurant():
    data = request.get_json()
    user_id = get_jwt_identity()  # Get the user ID from the token
    restaurant_id = data.get("restaurant_id")

    print(f"User ID from token: {user_id}")  # ✅ Debugging

    if not user_id:
        return jsonify({"message": "Invalid token"}), 401

    if Like.query.filter_by(user_id=user_id, restaurant_id=restaurant_id).first():
        return jsonify({"message": "Already liked"}), 400

    like = Like(user_id=user_id, restaurant_id=restaurant_id)
    db.session.add(like)
    db.session.commit()

    return jsonify({"message": "Restaurant liked successfully"}), 201
