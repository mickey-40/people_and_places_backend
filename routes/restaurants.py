from flask import Blueprint, request, jsonify
from models import Restaurant, Like, Review, User, db
from flask_jwt_extended import jwt_required, get_jwt_identity

restaurants_bp = Blueprint("restaurants", __name__)

# Allows admin to add a restaurant
@restaurants_bp.route("/add", methods=["POST"])
@jwt_required()  # Protect endpoint (optional)
def add_restaurant():
    user_id = get_jwt_identity()  # Get the authenticated user (optional)
    data = request.get_json()

    name = data.get("name")
    description = data.get("description")

    if not name or not description:
        return jsonify({"message": "Name and description are required"}), 400

    new_restaurant = Restaurant(name=name, description=description)
    db.session.add(new_restaurant)
    db.session.commit()

    return jsonify({"message": "Restaurant added successfully", "restaurant_id": new_restaurant.id}), 201


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

# Create the Review 
@restaurants_bp.route("/review", methods=["POST"])
@jwt_required()
def add_review():
    data = request.get_json()
    user_id = get_jwt_identity()
    restaurant_id = data.get("restaurant_id")
    rating = data.get("rating")
    comment = data.get("comment")

    # Check if the user already reviewed this restaurant
    existing_review = Review.query.filter_by(user_id=user_id, restaurant_id=restaurant_id).first()
    if existing_review:
        return jsonify({"message": "You have already reviewed this restaurant. Edit your review instead."}), 400

    # Validate input
    if not (1 <= rating <= 5):
        return jsonify({"message": "Rating must be between 1 and 5"}), 400

    new_review = Review(user_id=user_id, restaurant_id=restaurant_id, rating=rating, comment=comment)
    db.session.add(new_review)
    db.session.commit()

    return jsonify({"message": "Review added!"}), 201


# allow users to view all reviews for a specific restaurant
@restaurants_bp.route("/<int:restaurant_id>/reviews", methods=["GET"])
def get_restaurant_reviews(restaurant_id):
    reviews = Review.query.filter_by(restaurant_id=restaurant_id).join(User).all()

    if not reviews:
        return jsonify({"message": "No reviews found for this restaurant"}), 404

    return jsonify([
        {
            "id": review.id,
            "user": {"id": review.user.id, "username": review.user.username},
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at.strftime("%Y-%m-%d %H:%M:%S")  # ✅ Format timestamp
        } for review in reviews
    ]), 200
# Allows user to update review
@restaurants_bp.route("/review", methods=["PUT"])
@jwt_required()
def update_review():
    data = request.get_json()
    user_id = get_jwt_identity()
    restaurant_id = data.get("restaurant_id")
    new_rating = data.get("rating")
    new_comment = data.get("comment")

    # Find the review by the logged-in user for the given restaurant
    review = Review.query.filter_by(user_id=user_id, restaurant_id=restaurant_id).first()

    if not review:
        return jsonify({"message": "Review not found"}), 404

    # Update the rating and comment
    if new_rating:
        if not (1 <= new_rating <= 5):
            return jsonify({"message": "Rating must be between 1 and 5"}), 400
        review.rating = new_rating

    if new_comment:
        review.comment = new_comment

    db.session.commit()

    return jsonify({"message": "Review updated successfully"}), 200
# Allows user to delete review
@restaurants_bp.route("/review", methods=["DELETE"])
@jwt_required()
def delete_review():
    data = request.get_json()
    user_id = get_jwt_identity()
    restaurant_id = data.get("restaurant_id")

    # Find the review by the logged-in user for the given restaurant
    review = Review.query.filter_by(user_id=user_id, restaurant_id=restaurant_id).first()

    if not review:
        return jsonify({"message": "Review not found"}), 404

    # Delete the review
    db.session.delete(review)
    db.session.commit()

    return jsonify({"message": "Review deleted successfully"}), 200

