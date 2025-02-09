from flask import Blueprint, request, jsonify
from models import User, db, TokenBlocklist  # ✅ Corrected import
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt,create_access_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))  # ✅ Store user ID, not username
    return jsonify({"token": access_token}), 200

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    try:
        jti = get_jwt()["jti"]  # ✅ Get the JWT unique identifier
        token = TokenBlocklist(jti=jti)  # ✅ Create a new TokenBlocklist entry
        db.session.add(token)
        db.session.commit()
        return jsonify({"message": "Successfully logged out"}), 200
    except Exception as e:
        db.session.rollback()  # ✅ Rollback in case of error
        return jsonify({"error": str(e)}), 500  # ✅ Send error message in response

