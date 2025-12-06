"""
WorkFlowX - Employee Management System
Flask Application Initialization

This module initializes the Flask application and database connection.
It follows the Application Factory pattern for better modularity.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix


class Base(DeclarativeBase):
    """Base class for all database models using SQLAlchemy's declarative base."""
    pass


# Initialize SQLAlchemy with custom base class
db = SQLAlchemy(model_class=Base)

# Create the Flask application instance
app = Flask(__name__)

# Set secret key for session management (required for Flask sessions)
# Week 9 Concept: Security - Session management with secure secret key
# Using environment variable for security - never hardcode secrets
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production-ca2-2024")

# Load configuration from config.py (handles both local and cloud)
from config import Config
app.config.from_object(Config)

# ProxyFix middleware needed for proper URL generation with HTTPS
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Preferred URL scheme for external URLs
app.config['PREFERRED_URL_SCHEME'] = 'http'

# Get base directory
basedir = os.path.abspath(os.path.dirname(__file__))

# File Upload Configuration
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'images', 'profiles')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the database with the Flask app
db.init_app(app)

# Create database tables within application context
with app.app_context():
    # Import models here to ensure tables are created
    # This prevents circular import issues
    import models  # noqa: F401
    
    # Create all tables defined in models
    db.create_all()
