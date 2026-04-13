import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    if db_url.startswith("mysql://"):
        db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)
    SQLALCHEMY_DATABASE_URI = db_url
