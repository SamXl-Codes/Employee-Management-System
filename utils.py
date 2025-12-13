"""
WorkFlowX - Utility Functions

This module contains helper functions for validation, sanitization, and data processing.
Demonstrates:
- Regex pattern matching for validation
- String manipulation methods (.strip(), .lower(), etc.)
- Exception handling
- Function design with clear inputs/outputs
"""

import re
from datetime import datetime, date
from typing import Optional, Tuple


def validate_email(email: str) -> bool:
    """
    Validate email format using regular expressions.
    Pattern ensures valid structure with username, @ symbol, domain, and TLD.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email format is valid, False otherwise
        
    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid.email")
        False
    """
    if not email:
        return False
    
    # Regex pattern for email validation
    # Pattern breakdown:
    # ^[a-zA-Z0-9._%+-]+ : Start with alphanumeric or special chars
    # @ : Required @ symbol
    # [a-zA-Z0-9.-]+ : Domain name
    # \. : Required dot
    # [a-zA-Z]{2,}$ : Top-level domain (2+ letters)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    return bool(re.match(email_pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.
    
    Accepts formats like: 1234567890, 123-456-7890, (123) 456-7890, +1-123-456-7890
    
    Args:
        phone: Phone number to validate
        
    Returns:
        bool: True if phone format is valid, False otherwise
    """
    if not phone:
        return False
    
    # Regex pattern for phone validation
    # Accepts various common phone formats
    phone_pattern = r'^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}$'
    
    return bool(re.match(phone_pattern, phone))


def sanitize_string(input_str: str) -> str:
    """
    Sanitize string input to prevent XSS and other injection attacks.
    Removes dangerous HTML/script patterns and trims whitespace.
    
    Args:
        input_str: String to sanitize
        
    Returns:
        str: Sanitized string
    """
    if not input_str:
        return ""
    
    # Remove leading/trailing whitespace
    sanitized = input_str.strip()
    
    # Remove any potentially dangerous HTML/script tags (basic protection)
    # Jinja2 auto-escaping provides additional XSS protection
    dangerous_patterns = ['<script', '</script', 'javascript:', 'onerror=', 'onclick=']
    
    for pattern in dangerous_patterns:
        sanitized = sanitized.replace(pattern, '')
        sanitized = sanitized.replace(pattern.upper(), '')
    
    return sanitized


def validate_date_range(start_date: date, end_date: date) -> Tuple[bool, str]:
    """
    Validate that end_date is after start_date.
    
    Business rule for leave requests: end date must be >= start date
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
        
    Example:
        >>> from datetime import date
        >>> validate_date_range(date(2024, 1, 1), date(2024, 1, 5))
        (True, '')
        >>> validate_date_range(date(2024, 1, 5), date(2024, 1, 1))
        (False, 'End date must be after start date')
    """
    if not start_date or not end_date:
        return False, "Both start and end dates are required"
    
    if end_date < start_date:
        return False, "End date must be after start date"
    
    return True, ""


def validate_salary(salary_str: str) -> Tuple[bool, str, Optional[float]]:
    """
    Validate and convert salary input.
    Converts string to float and checks for reasonable ranges.
    
    Args:
        salary_str: Salary as string
        
    Returns:
        Tuple[bool, str, Optional[float]]: (is_valid, error_message, converted_value)
    """
    if not salary_str:
        return False, "Salary is required", None
    
    try:
        salary = float(salary_str)
        
        # Validation: salary must be positive
        if salary <= 0:
            return False, "Salary must be a positive number", None
        
        # Validation: reasonable salary range (for example)
        if salary > 10000000:  # $10 million cap
            return False, "Salary exceeds maximum allowed value", None
        
        return True, "", salary
        
    except ValueError:
        return False, "Salary must be a valid number", None
    except Exception as e:
        return False, f"Invalid salary: {str(e)}", None


def format_currency(amount: float) -> str:
    """
    Format number as currency.
    
    Args:
        amount: Numeric amount
        
    Returns:
        str: Formatted currency string
        
    Example:
        >>> format_currency(1234.56)
        '$1,234.56'
    """
    try:
        return f"${amount:,.2f}"
    except:
        return "$0.00"


def calculate_date_difference(start_date: date, end_date: date) -> int:
    """
    Calculate number of days between two dates (inclusive).
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        int: Number of days (includes both start and end dates)
    """
    if not start_date or not end_date:
        return 0
    
    delta = end_date - start_date
    return delta.days + 1  # +1 to include both start and end dates


def parse_date(date_str: str, date_format: str = '%Y-%m-%d') -> Optional[date]:
    """
    Parse date string to date object.
    Returns None if string format is invalid or cannot be parsed.
    
    Args:
        date_str: Date as string
        date_format: Expected date format (default: YYYY-MM-DD)
        
    Returns:
        Optional[date]: Parsed date or None if invalid
    """
    try:
        return datetime.strptime(date_str, date_format).date()
    except (ValueError, TypeError):
        return None


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username format.
    
    Rules:
    - 3-64 characters
    - Alphanumeric and underscores only
    - No spaces
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"
    
    # Remove whitespace
    username = username.strip()
    
    # Length check
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 64:
        return False, "Username must not exceed 64 characters"
    
    # Pattern check: alphanumeric and underscores only
    username_pattern = r'^[a-zA-Z0-9_]+$'
    if not re.match(username_pattern, username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, ""


def validate_required_fields(data: dict, required_fields: list) -> Tuple[bool, str]:
    """
    Check if all required fields are present and non-empty.
    Validates form data to ensure no required information is missing.
    
    Args:
        data: Dictionary of form data
        required_fields: List of required field names
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    missing_fields = []
    
    # Check each required field
    for field in required_fields:
        if field not in data or not data[field] or str(data[field]).strip() == '':
            missing_fields.append(field)
    
    # Build error message if any fields are missing
    if missing_fields:
        # Format field names nicely
        formatted_fields = ', '.join(missing_fields)
        return False, f"Missing required fields: {formatted_fields}"
    
    return True, ""


def get_current_date() -> date:
    """
    Get current date.
    
    Returns:
        date: Today's date
    """
    return date.today()


def get_current_datetime() -> datetime:
    """
    Get current datetime.
    
    Returns:
        datetime: Current datetime
    """
    return datetime.utcnow()
