"""
WorkFlowX - Configuration Settings

This module contains configuration settings for the application.
Following the principle of separation of concerns.

RAILWAY DEPLOYMENT VERSION - Updated Dec 6, 2025
"""

import os

# Force Railway cache invalidation marker: v1.0.3


class Config:
    """Base configuration class with common settings."""
    
    # Security settings
    # Week 9 Concept: Security best practices - environment variable usage
    SECRET_KEY = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production-ca2-2024")
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images', 'profiles')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Database configuration - Support both MS SQL Server (local) and SQLite (Railway)
    # Week 7 Concept: Database configuration with flexible database support
    
    # Check if running on Railway - Railway automatically sets RAILWAY_STATIC_URL
    # Also check for common deployment environment variables as fallback
    IS_RAILWAY = (
        os.environ.get('RAILWAY_STATIC_URL') is not None or
        os.environ.get('RAILWAY_ENVIRONMENT') is not None or
        os.environ.get('RAILWAY_SERVICE_NAME') is not None or
        os.environ.get('PORT') is not None  # Railway sets PORT
    )
    
    # Debug logging
    print(f"[CONFIG DEBUG] IS_RAILWAY: {IS_RAILWAY}")
    print(f"[CONFIG DEBUG] PORT: {os.environ.get('PORT')}")
    print(f"[CONFIG DEBUG] RAILWAY_STATIC_URL: {os.environ.get('RAILWAY_STATIC_URL')}")
    
    if IS_RAILWAY:
        # Railway deployment - Use SQLite (simple, no separate database needed)
        # Store database in persistent storage
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workflowx.db')
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
        }
    else:
        # Local development - Use MS SQL Server
        # Import pyodbc only for local development (not available on Railway)
        import pyodbc
        
        MSSQL_SERVER = 'localhost\\SQLEXPRESS01'
        MSSQL_DATABASE = 'workflowx'
        MSSQL_USERNAME = 'workflowx_admin'
        MSSQL_PASSWORD = 'WorkFlowDB@2025'
        
        # Try ODBC Driver 17 first, fallback to Driver 18
        try:
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
