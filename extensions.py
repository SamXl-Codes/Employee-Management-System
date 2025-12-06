"""
Flask extensions initialization.
This module prevents circular imports by centralizing extension creation.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models using SQLAlchemy's declarative base."""
    pass


# Create database extension instance with custom base class
db = SQLAlchemy(model_class=Base)
