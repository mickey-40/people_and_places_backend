# settings.py

import os
from dotenv import load_dotenv

load_dotenv()

print("settings.py loaded")
# print("JWT_SECRET_KEY:", os.getenv("JWT_SECRET_KEY"))

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
