from flask import Flask
from flask import jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from models import db
from settings import Config
from routes.auth import auth_bp
from routes.restaurants import restaurants_bp
from routes.users import users_bp


app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
CORS(app)
app.config["JWT_ALGORITHM"] = "HS256"  # Ensure this matches login JWT
jwt = JWTManager(app)
db.init_app(app)

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

if __name__ == "__main__":
    app.run(debug=True)
