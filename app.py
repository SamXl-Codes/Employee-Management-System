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
# Manage user sessions
# Using environment variable for security - never hardcode secrets
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production-ca2-2024")

# ProxyFix middleware needed for proper URL generation with HTTPS
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Preferred URL scheme for external URLs
app.config['PREFERRED_URL_SCHEME'] = 'http'

# Configure database connection
# Use SQLite for testing, MS SQL Server for production
basedir = os.path.abspath(os.path.dirname(__file__))

# Check if running in test mode
if os.environ.get('TESTING') == '1' or app.config.get('TESTING'):
    # Use SQLite in-memory for testing
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///:memory:'
else:
    # MS SQL Server Settings - Allow configuration via environment variables
    # George can set his own SQL Server instance name
    MSSQL_SERVER = os.environ.get('MSSQL_SERVER', 'localhost\\SQLEXPRESS01')
    MSSQL_DATABASE = os.environ.get('MSSQL_DATABASE', 'workflowx')
    USE_WINDOWS_AUTH = os.environ.get('USE_WINDOWS_AUTH', '0') == '1'
    
    # Detect available ODBC driver
    try:
        import pyodbc
        drivers = [x for x in pyodbc.drivers() if 'SQL Server' in x]
        if any('17' in d for d in drivers):
            MSSQL_DRIVER = 'ODBC Driver 17 for SQL Server'
        elif any('18' in d for d in drivers):
            MSSQL_DRIVER = 'ODBC Driver 18 for SQL Server'
        else:
            MSSQL_DRIVER = 'SQL Server'
        
        auth_method = "Windows Authentication" if USE_WINDOWS_AUTH else "SQL Authentication"
        print(f"Using MS SQL Server: {MSSQL_SERVER} | Database: {MSSQL_DATABASE} | Auth: {auth_method}")
    except:
        MSSQL_DRIVER = 'ODBC Driver 17 for SQL Server'
    
    # Build MS SQL Server connection string
    from urllib.parse import quote_plus
    
    if USE_WINDOWS_AUTH:
        # Windows Authentication (Trusted Connection)
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            f'mssql+pyodbc://{MSSQL_SERVER}/{MSSQL_DATABASE}?'
            f'driver={MSSQL_DRIVER}&trusted_connection=yes&timeout=5'
        )
    else:
        # SQL Server Authentication (username/password)
        MSSQL_USERNAME = os.environ.get('MSSQL_USERNAME', 'workflowx_admin')
        MSSQL_PASSWORD = os.environ.get('MSSQL_PASSWORD', 'WorkFlowDB@2025')
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            f'mssql+pyodbc://{MSSQL_USERNAME}:{quote_plus(MSSQL_PASSWORD)}@{MSSQL_SERVER}/{MSSQL_DATABASE}?'
            f'driver={MSSQL_DRIVER}&timeout=5'
        )

# Database engine options
# Database configuration
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,  # Recycle connections after 5 minutes
    "pool_pre_ping": True,  # Verify connections before using them
}

# Disable modification tracking to save resources
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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
