"""
WorkFlowX - Configuration Settings

This module contains configuration settings for the application.
Following the principle of separation of concerns.
"""

import os


class Config:
    """Base configuration class with common settings."""
    
    # Security settings
    # Week 9 Concept: Security best practices - environment variable usage
    SECRET_KEY = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production-ca2-2024")
    
    # Database configuration (CA-2 Requirement: SQLite)
    # Week 7 Concept: Database configuration with SQLite
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'workflowx.db')}"
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
