from flask import Flask
from flask_migrate import Migrate  # ✅ Import Flask-Migrate
from flask import jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from models import User, db, TokenBlocklist
from settings import Config  # ✅ Corrected import
from routes.auth import auth_bp
from routes.restaurants import restaurants_bp
from routes.users import users_bp


app = Flask(__name__)
app.config.from_object(Config)
app.config["CORS_HEADERS"] = "Content-Type"

# Initialize extensions
# ✅ Allow specific origins, methods, and headers
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
app.config["JWT_ALGORITHM"] = "HS256"  # Ensure this matches login JWT
jwt = JWTManager(app)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)  # ✅ Register Flask-Migrate

print("CORS is enabled:", app.config["CORS_HEADERS"])
@app.route("/restaurants", methods=["OPTIONS"])
def handle_options():
    return "", 204


# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(restaurants_bp, url_prefix="/restaurants")
app.register_blueprint(users_bp, url_prefix="/users")

# Initialize database tables when the first request comes in
@app.before_request
def initialize_database():
    if not hasattr(app, 'db_initialized'):
        with app.app_context():
            db.create_all()
        app.db_initialized = True

@app.route("/token")
def generate_token():
    token = create_access_token(identity="testuser")
    return jsonify(access_token=token)

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar() is not None


if __name__ == "__main__":
    app.run(debug=True)
