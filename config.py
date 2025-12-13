"""
WorkFlowX - Configuration Settings

This module contains configuration settings for the application.
Following the principle of separation of concerns.
"""

import os


class Config:
    """Base configuration class with common settings."""
    
    # Security settings
    # Use environment variables for sensitive configuration to keep secrets out of source code
    SECRET_KEY = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production-ca2-2024")
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images', 'profiles')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Database configuration for MS SQL Server
    # Connection settings for local development database
    
    # MS SQL Server Settings
    MSSQL_SERVER = 'localhost\\SQLEXPRESS01'
    MSSQL_DATABASE = 'workflowx'
    MSSQL_USERNAME = 'workflowx_admin'
    MSSQL_PASSWORD = 'WorkFlowDB@2025'
    
    # Try ODBC Driver 17 first, fallback to Driver 18
    try:
        import pyodbc
        drivers = [x for x in pyodbc.drivers() if 'SQL Server' in x]
        if any('17' in d for d in drivers):
            MSSQL_DRIVER = 'ODBC Driver 17 for SQL Server'
        elif any('18' in d for d in drivers):
            MSSQL_DRIVER = 'ODBC Driver 18 for SQL Server'
        else:
            MSSQL_DRIVER = 'SQL Server'
    except:
        MSSQL_DRIVER = 'ODBC Driver 17 for SQL Server'
    
    # Build MS SQL Server connection string
    # Using Windows Authentication (more reliable for local development)
    SQLALCHEMY_DATABASE_URI = (
        f'mssql+pyodbc://{MSSQL_SERVER}/{MSSQL_DATABASE}?'
        f'driver={MSSQL_DRIVER}&trusted_connection=yes'
    )
    
    # Alternative: SQL Server Authentication (if needed)
    # SQLALCHEMY_DATABASE_URI = (
    #     f'mssql+pyodbc://{MSSQL_USERNAME}:{MSSQL_PASSWORD}@'
    #     f'{MSSQL_SERVER}/{MSSQL_DATABASE}?'
    #     f'driver={MSSQL_DRIVER}&TrustServerCertificate=yes'
    # )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Application settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    
    # Session configuration
    SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to cookies
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    
    # Pagination settings
    ITEMS_PER_PAGE = 10


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False


# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
