import os
from datetime import timedelta

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///f1_fantasy.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Jolpi Ergast API proxy configuration
    JOLPI_ERGAST_API_BASE_URL = os.environ.get(
        'JOLPI_ERGAST_API_BASE_URL',
        'https://api.jolpi.ca/ergast/f1',
    )
