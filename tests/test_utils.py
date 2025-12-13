"""
Unit Tests for Utility Functions

Tests all validation and helper functions in utils.py including:
- Email validation (regex)
- Phone validation (regex)
- String sanitization
- Date validation and parsing
- Salary validation
- Required field validation


"""

import unittest
import sys
import os
from datetime import date, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import utils


class TestEmailValidation(unittest.TestCase):
    """
    Test email validation function.
    Ensures regex patterns correctly identify valid and invalid email formats.
    """
    
    def test_valid_emails(self):
        """Test various valid email formats."""
        valid_emails = [
            'user@example.com',
            'john.doe@company.co.uk',
            'admin123@test-domain.com',
            'sales@mycompany.org',
            'info+newsletter@website.io'
        ]
        
        # Test each valid email format
        for email in valid_emails:
            with self.subTest(email=email):
                self.assertTrue(utils.validate_email(email), 
                               f"Email '{email}' should be valid")
    
    def test_invalid_emails(self):
        """Test invalid email formats that should fail."""
        invalid_emails = [
            'notanemail',
            'missing@domain',
            '@nodomain.com',
            'noatsign.com',
            'spaces in@email.com',
            'double@@domain.com',
            '',
            None
        ]
        
        for email in invalid_emails:
            with self.subTest(email=email):
                self.assertFalse(utils.validate_email(email) if email else False,
                                f"Email '{email}' should be invalid")
    
    def test_email_case_sensitivity(self):
        """Test email validation is case-insensitive."""
        self.assertTrue(utils.validate_email('USER@EXAMPLE.COM'))
        self.assertTrue(utils.validate_email('User@Example.Com'))


class TestPhoneValidation(unittest.TestCase):
    """
    Test phone number validation.
    Verifies various international phone number formats are accepted.
    """
    
    def test_valid_phone_formats(self):
        """Test various valid phone number formats."""
        valid_phones = [
            '1234567890',
            '123-456-7890',
            '(123) 456-7890',
            '+1-123-456-7890',
            '+44 20 1234 5678',
            '555.123.4567'
        ]
        
        for phone in valid_phones:
            with self.subTest(phone=phone):
                self.assertTrue(utils.validate_phone(phone),
                               f"Phone '{phone}' should be valid")
    
    def test_invalid_phone_formats(self):
        """Test invalid phone formats."""
        invalid_phones = [
            'abc',
            '123',
            '12-34',
            'notaphone',
            '',
            None
        ]
        
        for phone in invalid_phones:
            with self.subTest(phone=phone):
                result = utils.validate_phone(phone) if phone else False
                self.assertFalse(result, f"Phone '{phone}' should be invalid")


class TestStringSanitization(unittest.TestCase):
    """
    Test string sanitization for XSS prevention.
    Ensures dangerous HTML and script tags are properly removed from user input.
    """
    
    def test_sanitize_removes_dangerous_tags(self):
        """Test that dangerous HTML/script tags are removed."""
        dangerous_inputs = [
            '<script>alert("XSS")</script>Hello',
            'Normal text<script>bad()</script>',
            'JAVASCRIPT:void(0)',
            'onclick=alert(1)',
            '<SCRIPT>malicious</SCRIPT>'
        ]
        
        for dangerous in dangerous_inputs:
            with self.subTest(input=dangerous):
                sanitized = utils.sanitize_string(dangerous)
                # Verify dangerous patterns are removed
                self.assertNotIn('<script', sanitized.lower())
                self.assertNotIn('javascript:', sanitized.lower())
                self.assertNotIn('onclick=', sanitized.lower())
    
    def test_sanitize_strips_whitespace(self):
        """Test that leading/trailing whitespace is removed."""
        test_cases = [
            ('  hello  ', 'hello'),
            ('\n\ttest\n', 'test'),
            ('   spaced   ', 'spaced')
        ]
        
        for input_str, expected in test_cases:
            with self.subTest(input=input_str):
                result = utils.sanitize_string(input_str)
                self.assertEqual(result, expected)
    
    def test_sanitize_empty_strings(self):
        """Test handling of empty/None strings."""
        self.assertEqual(utils.sanitize_string(''), '')
        self.assertEqual(utils.sanitize_string(None), '')


class TestDateValidation(unittest.TestCase):
    """
    Test date validation and parsing functions.
    Validates date ranges for leave requests and other time-based operations.
    """
    
    def test_validate_date_range_valid(self):
        """Test valid date ranges."""
        start = date(2024, 1, 1)
        end = date(2024, 1, 10)
        
        is_valid, error_msg = utils.validate_date_range(start, end)
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, '')
    
    def test_validate_date_range_same_day(self):
        """Test date range with same start and end date."""
        same_date = date(2024, 5, 15)
        
        is_valid, error_msg = utils.validate_date_range(same_date, same_date)
        self.assertTrue(is_valid)
    
    def test_validate_date_range_invalid(self):
        """Test invalid date ranges (end before start)."""
        start = date(2024, 1, 10)
        end = date(2024, 1, 1)
        
        is_valid, error_msg = utils.validate_date_range(start, end)
        self.assertFalse(is_valid)
        self.assertIn('End date must be after start date', error_msg)
    
    def test_validate_date_range_missing_dates(self):
        """Test handling of None dates."""
        is_valid, error_msg = utils.validate_date_range(None, date.today())
        self.assertFalse(is_valid)
        
        is_valid, error_msg = utils.validate_date_range(date.today(), None)
        self.assertFalse(is_valid)
    
    def test_parse_date_valid_formats(self):
        """
        Test parsing valid date strings.
        
        Parse and convert data
        """
        test_cases = [
            ('2024-01-15', date(2024, 1, 15)),
            ('2024-12-31', date(2024, 12, 31)),
            ('2025-06-01', date(2025, 6, 1))
        ]
        
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                result = utils.parse_date(date_str)
                self.assertEqual(result, expected)
    
    def test_parse_date_invalid_formats(self):
        """Test parsing invalid date strings."""
        invalid_dates = [
            'not-a-date',
            '01/15/2024',  # Wrong format
            '2024-13-01',  # Invalid month
            '2024-01-32',  # Invalid day
            '',
            None
        ]
        
        for date_str in invalid_dates:
            with self.subTest(date_str=date_str):
                result = utils.parse_date(date_str)
                self.assertIsNone(result)
    
    def test_calculate_date_difference(self):
        """
        Test date difference calculation.
        Calculates inclusive days between two dates for leave requests.
        """
        start = date(2024, 1, 1)
        end = date(2024, 1, 5)
        
        # Should be 5 days inclusive (1, 2, 3, 4, 5)
        days = utils.calculate_date_difference(start, end)
        self.assertEqual(days, 5)
        
        # Same day should be 1
        same_day = date(2024, 3, 15)
        days = utils.calculate_date_difference(same_day, same_day)
        self.assertEqual(days, 1)


class TestSalaryValidation(unittest.TestCase):
    """
    Test salary validation and conversion.
    Ensures salary inputs are valid numbers within reasonable ranges.
    """
    
    def test_validate_salary_valid(self):
        """Test valid salary inputs."""
        test_cases = [
            ('50000', 50000.0),
            ('75000.50', 75000.50),
            ('100000', 100000.0),
            ('45000.99', 45000.99)
        ]
        
        for salary_str, expected in test_cases:
            with self.subTest(salary=salary_str):
                is_valid, error_msg, value = utils.validate_salary(salary_str)
                self.assertTrue(is_valid, f"Salary '{salary_str}' should be valid")
                self.assertEqual(error_msg, '')
                self.assertEqual(value, expected)
    
    def test_validate_salary_negative(self):
        """Test negative salary is rejected."""
        is_valid, error_msg, value = utils.validate_salary('-5000')
        self.assertFalse(is_valid)
        self.assertIn('positive', error_msg.lower())
        self.assertIsNone(value)
    
    def test_validate_salary_zero(self):
        """Test zero salary is rejected."""
        is_valid, error_msg, value = utils.validate_salary('0')
        self.assertFalse(is_valid)
        self.assertIn('positive', error_msg.lower())
    
    def test_validate_salary_too_large(self):
        """Test unreasonably large salary is rejected."""
        is_valid, error_msg, value = utils.validate_salary('99999999999')
        self.assertFalse(is_valid)
        self.assertIn('exceeds', error_msg.lower())
    
    def test_validate_salary_invalid_format(self):
        """Test non-numeric inputs are rejected."""
        invalid_inputs = [
            'abc',
            'fifty thousand',
            '$50000',
            '50,000',
            '',
            None
        ]
        
        for salary_str in invalid_inputs:
            with self.subTest(salary=salary_str):
                is_valid, error_msg, value = utils.validate_salary(salary_str) if salary_str else utils.validate_salary('')
                self.assertFalse(is_valid)
                self.assertIsNone(value)


class TestUsernameValidation(unittest.TestCase):
    """
    Test username validation.
    
    Validate using regex patterns
    """
    
    def test_valid_usernames(self):
        """Test valid username formats."""
        valid_usernames = [
            'user123',
            'john_doe',
            'admin',
            'test_user_123',
            'Employee1'
        ]
        
        for username in valid_usernames:
            with self.subTest(username=username):
                is_valid, error_msg = utils.validate_username(username)
                self.assertTrue(is_valid, f"Username '{username}' should be valid")
                self.assertEqual(error_msg, '')
    
    def test_username_too_short(self):
        """Test username shorter than 3 characters."""
        is_valid, error_msg = utils.validate_username('ab')
        self.assertFalse(is_valid)
        self.assertIn('at least 3', error_msg)
    
    def test_username_too_long(self):
        """Test username longer than 64 characters."""
        long_username = 'a' * 65
        is_valid, error_msg = utils.validate_username(long_username)
        self.assertFalse(is_valid)
        self.assertIn('exceed 64', error_msg)
    
    def test_username_invalid_characters(self):
        """Test usernames with special characters."""
        invalid_usernames = [
            'user@domain',
            'john.doe',
            'test user',
            'admin!',
            'user#123'
        ]
        
        for username in invalid_usernames:
            with self.subTest(username=username):
                is_valid, error_msg = utils.validate_username(username)
                self.assertFalse(is_valid)
                self.assertIn('letters, numbers, and underscores', error_msg)


class TestRequiredFields(unittest.TestCase):
    """
    Test required field validation.
    
    Work with dictionary data structures
    Control flow and validation
    """
    
    def test_all_fields_present(self):
        """Test when all required fields are provided."""
        data = {
            'name': 'John Doe',
            'email': 'john@test.com',
            'phone': '555-1234'
        }
        required = ['name', 'email', 'phone']
        
        is_valid, error_msg = utils.validate_required_fields(data, required)
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, '')
    
    def test_missing_field(self):
        """Test when a required field is missing."""
        data = {
            'name': 'John Doe',
            'phone': '555-1234'
        }
        required = ['name', 'email', 'phone']
        
        is_valid, error_msg = utils.validate_required_fields(data, required)
        self.assertFalse(is_valid)
        self.assertIn('email', error_msg)
    
    def test_empty_field(self):
        """Test when a field is present but empty."""
        data = {
            'name': 'John Doe',
            'email': '',  # Empty string
            'phone': '555-1234'
        }
        required = ['name', 'email', 'phone']
        
        is_valid, error_msg = utils.validate_required_fields(data, required)
        self.assertFalse(is_valid)
        self.assertIn('email', error_msg)
    
    def test_whitespace_only_field(self):
        """Test when a field contains only whitespace."""
        data = {
            'name': '   ',  # Whitespace only
            'email': 'john@test.com',
            'phone': '555-1234'
        }
        required = ['name', 'email', 'phone']
        
        is_valid, error_msg = utils.validate_required_fields(data, required)
        self.assertFalse(is_valid)
        self.assertIn('name', error_msg)


class TestCurrencyFormatting(unittest.TestCase):
    """
    Test currency formatting function.
    
    String formatting
    """
    
    def test_format_currency_valid(self):
        """Test formatting valid amounts."""
        test_cases = [
            (1234.56, '$1,234.56'),
            (0.99, '$0.99'),
            (1000000, '$1,000,000.00'),
            (50, '$50.00')
        ]
        
        for amount, expected in test_cases:
            with self.subTest(amount=amount):
                result = utils.format_currency(amount)
                self.assertEqual(result, expected)
    
    def test_format_currency_invalid(self):
        """Test handling of invalid inputs."""
        result = utils.format_currency('invalid')
        self.assertEqual(result, '$0.00')


def run_utils_tests():
    """
    Run all utility function tests.
    
    Test with unittest framework
    """
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEmailValidation))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPhoneValidation))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestStringSanitization))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDateValidation))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSalaryValidation))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestUsernameValidation))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRequiredFields))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCurrencyFormatting))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_utils_tests()
    sys.exit(0 if success else 1)
