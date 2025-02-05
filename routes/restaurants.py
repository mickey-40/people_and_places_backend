from flask import Blueprint, request, jsonify
from models import Restaurant, Like, db
from flask_jwt_extended import jwt_required, get_jwt_identity

restaurants_bp = Blueprint("restaurants", __name__)
# Gets all restaurants
@restaurants_bp.route("/", methods=["GET"])
def get_restaurants():
    page = request.args.get("page", 1, type=int)
    per_page = 10  # Adjust based on frontend needs
    restaurants = Restaurant.query.paginate(page=page, per_page=per_page)

    return jsonify([
        {"id": r.id, "name": r.name, "description": r.description}
        for r in restaurants.items
    ])

# Allows users to like a restaurant
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
# Allow Users to unlike a restaurant
@restaurants_bp.route("/unlike", methods=["DELETE"])
@jwt_required()
def unlike_restaurant():
    data = request.get_json()
    user_id = get_jwt_identity()
    restaurant_id = data.get("restaurant_id")

    like = Like.query.filter_by(user_id=user_id, restaurant_id=restaurant_id).first()
    if not like:
        return jsonify({"message": "Like not found"}), 404

    db.session.delete(like)
    db.session.commit()

    return jsonify({"message": "Like removed"}), 200
# Allows Users to see liked restaurants
@restaurants_bp.route("/liked", methods=["GET"])
@jwt_required()
def get_liked_restaurants():
    user_id = get_jwt_identity()
    liked_restaurants = Like.query.filter_by(user_id=user_id).all()

    return jsonify([
        {"restaurant_id": like.restaurant_id}
        for like in liked_restaurants
    ])
