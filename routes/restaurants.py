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
    user_id = get_jwt_identity()
    restaurant_id = data.get("restaurant_id")

    if Like.query.filter_by(user_id=user_id, restaurant_id=restaurant_id).first():
        return jsonify({"message": "Already liked"}), 400

    like = Like(user_id=user_id, restaurant_id=restaurant_id)
    db.session.add(like)
    db.session.commit()

    return jsonify({"message": "Restaurant liked successfully"}), 201
