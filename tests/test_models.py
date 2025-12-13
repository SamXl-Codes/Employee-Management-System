"""
Unit Tests for Database Models

Tests all model classes including:
- User model and authentication
- Employee model and business logic
- Department and Role models
- Attendance and LeaveRequest models
- AuditLog model


"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import User, Department, Role, Employee, Attendance, LeaveRequest, AuditLog
from datetime import date, datetime, timedelta


class TestUserModel(unittest.TestCase):
    """
    Test User model functionality.
    
    Test with unittest framework
    Test security features
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test database before all tests."""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        cls.app = app
        cls.client = app.test_client()
    
    def setUp(self):
        """Create test database tables before each test."""
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up test database after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_user_creation(self):
        """
        Test creating a new user.
        
        Test with unittest framework
        Test object methods
        """
        with app.app_context():
            user = User(username='testuser', password='testpass123', role='employee')
            db.session.add(user)
            db.session.commit()
            
            # Verify user was created
            self.assertIsNotNone(user.user_id)
            self.assertEqual(user.username, 'testuser')
            self.assertEqual(user.role, 'employee')
    
    def test_password_hashing(self):
        """
        Test password hashing functionality.
        
        Use secure password hashing
        """
        with app.app_context():
            user = User(username='testuser', password='mypassword', role='admin')
            db.session.add(user)
            db.session.commit()
            
            # Password should be hashed, not plain text
            self.assertNotEqual(user.password_hash, 'mypassword')
            # Should contain hash prefix
            self.assertTrue(user.password_hash.startswith('scrypt:'))
    
    def test_password_verification(self):
        """
        Test password checking works correctly.
        
        Boolean logic and assertions
        Authentication testing
        """
        with app.app_context():
            user = User(username='testuser', password='correctpassword', role='employee')
            db.session.add(user)
            db.session.commit()
            
            # Correct password should pass
            self.assertTrue(user.check_password('correctpassword'))
            # Wrong password should fail
            self.assertFalse(user.check_password('wrongpassword'))
    
    def test_user_to_dict(self):
        """
        Test User to_dict() method for JSON serialization.
        
        Work with dictionary data structures
        Serialize data for API responses
        """
        with app.app_context():
            user = User(username='testuser', password='password', role='admin')
            db.session.add(user)
            db.session.commit()
            
            user_dict = user.to_dict()
            
            # Check required fields
            self.assertIn('user_id', user_dict)
            self.assertIn('username', user_dict)
            self.assertIn('role', user_dict)
            # Password should NOT be in dict (security)
            self.assertNotIn('password_hash', user_dict)


class TestDepartmentModel(unittest.TestCase):
    """Test Department model functionality."""
    
    def setUp(self):
        """Create test database before each test."""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_department_creation(self):
        """Test creating a department."""
        with app.app_context():
            dept = Department(name='Engineering', description='Software Development')
            db.session.add(dept)
            db.session.commit()
            
            self.assertIsNotNone(dept.department_id)
            self.assertEqual(dept.name, 'Engineering')
            self.assertEqual(dept.description, 'Software Development')
    
    def test_department_employee_count(self):
        """
        Test get_employee_count() method.
        
        Test object methods
        """
        with app.app_context():
            # Create department and role
            dept = Department(name='HR', description='Human Resources')
            role = Role(title='HR Manager', description='Manages HR')
            db.session.add(dept)
            db.session.add(role)
            db.session.commit()
            
            # Initially no employees
            self.assertEqual(dept.get_employee_count(), 0)
            
            # Add employee
            emp = Employee(
                name='John Doe',
                email='john@test.com',
                phone='1234567890',
                department_id=dept.department_id,
                role_id=role.role_id,
                salary=50000,
                date_joined=date.today()
            )
            db.session.add(emp)
            db.session.commit()
            
            # Should have 1 employee
            self.assertEqual(dept.get_employee_count(), 1)
    
    def test_department_can_delete(self):
        """
        Test can_delete() business logic.
        
        Boolean logic and assertions
        Validate business rules
        """
        with app.app_context():
            dept = Department(name='Marketing', description='Marketing Team')
            db.session.add(dept)
            db.session.commit()
            
            # Department with no employees can be deleted
            self.assertTrue(dept.can_delete())


class TestEmployeeModel(unittest.TestCase):
    """Test Employee model functionality."""
    
    def setUp(self):
        """Set up test database."""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up test database."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_employee_creation(self):
        """Test creating an employee with all required fields."""
        with app.app_context():
            # Create dependencies
            dept = Department(name='IT', description='IT Department')
            role = Role(title='Developer', description='Software Developer')
            db.session.add(dept)
            db.session.add(role)
            db.session.commit()
            
            # Create employee
            emp = Employee(
                name='Jane Smith',
                email='jane@test.com',
                phone='555-1234',
                department_id=dept.department_id,
                role_id=role.role_id,
                salary=75000,
                date_joined=date(2024, 1, 15)
            )
            db.session.add(emp)
            db.session.commit()
            
            self.assertIsNotNone(emp.employee_id)
            self.assertEqual(emp.name, 'Jane Smith')
            self.assertEqual(emp.email, 'jane@test.com')
            self.assertEqual(emp.status, 'active')  # Default value
    
    def test_employee_attendance_percentage(self):
        """
        Test get_attendance_percentage() calculation.
        
        Calculate values
        Data processing
        """
        with app.app_context():
            # Create employee
            dept = Department(name='Sales', description='Sales Department')
            role = Role(title='Sales Rep', description='Sales Representative')
            db.session.add(dept)
            db.session.add(role)
            db.session.commit()
            
            emp = Employee(
                name='Bob Johnson',
                email='bob@test.com',
                phone='555-5678',
                department_id=dept.department_id,
                role_id=role.role_id,
                salary=60000,
                date_joined=date.today()
            )
            db.session.add(emp)
            db.session.commit()
            
            # No attendance records - should be 0%
            self.assertEqual(emp.get_attendance_percentage(), 0.0)
            
            # Add attendance records
            for i in range(10):
                attendance = Attendance(
                    employee_id=emp.employee_id,
                    date=date.today() - timedelta(days=i),
                    status='Present' if i < 8 else 'Absent'
                )
                db.session.add(attendance)
            db.session.commit()
            
            # 8 present out of 10 = 80%
            self.assertEqual(emp.get_attendance_percentage(), 80.0)
    
    def test_employee_total_leave_days(self):
        """
        Test get_total_leave_days() calculation.
        
        Calculate values
        """
        with app.app_context():
            # Create employee
            dept = Department(name='Finance', description='Finance Department')
            role = Role(title='Accountant', description='Financial Accountant')
            db.session.add(dept)
            db.session.add(role)
            db.session.commit()
            
            emp = Employee(
                name='Alice Williams',
                email='alice@test.com',
                phone='555-9999',
                department_id=dept.department_id,
                role_id=role.role_id,
                salary=70000,
                date_joined=date.today()
            )
            db.session.add(emp)
            db.session.commit()
            
            # No leave requests - should be 0
            self.assertEqual(emp.get_total_leave_days(), 0)
            
            # Add approved leave request (3 days: Jan 1-3)
            leave = LeaveRequest(
                employee_id=emp.employee_id,
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 3),
                leave_type='Annual',
                reason='Vacation'
            )
            leave.status = 'Approved'
            db.session.add(leave)
            db.session.commit()
            
            # Should be 3 days (inclusive)
            self.assertEqual(emp.get_total_leave_days(), 3)
    
    def test_employee_activation_methods(self):
        """
        Test activate() and deactivate() methods.
        
        Test object methods
        """
        with app.app_context():
            dept = Department(name='Operations', description='Operations Team')
            role = Role(title='Operator', description='System Operator')
            db.session.add(dept)
            db.session.add(role)
            db.session.commit()
            
            emp = Employee(
                name='Charlie Brown',
                email='charlie@test.com',
                phone='555-0000',
                department_id=dept.department_id,
                role_id=role.role_id,
                salary=55000,
                date_joined=date.today()
            )
            db.session.add(emp)
            db.session.commit()
            
            # Initially active
            self.assertTrue(emp.is_active())
            
            # Deactivate
            emp.deactivate()
            self.assertFalse(emp.is_active())
            self.assertEqual(emp.status, 'inactive')
            
            # Reactivate
            emp.activate()
            self.assertTrue(emp.is_active())
            self.assertEqual(emp.status, 'active')


class TestLeaveRequestModel(unittest.TestCase):
    """Test LeaveRequest model functionality."""
    
    def setUp(self):
        """Set up test database."""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up test database."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_leave_request_creation(self):
        """Test creating a leave request."""
        with app.app_context():
            # Create employee
            dept = Department(name='Support', description='Customer Support')
            role = Role(title='Support Agent', description='Customer Support')
            db.session.add(dept)
            db.session.add(role)
            db.session.commit()
            
            emp = Employee(
                name='David Lee',
                email='david@test.com',
                phone='555-1111',
                department_id=dept.department_id,
                role_id=role.role_id,
                salary=50000,
                date_joined=date.today()
            )
            db.session.add(emp)
            db.session.commit()
            
            # Create leave request
            leave = LeaveRequest(
                employee_id=emp.employee_id,
                start_date=date(2024, 3, 1),
                end_date=date(2024, 3, 5),
                leave_type='Sick',
                reason='Medical appointment'
            )
            db.session.add(leave)
            db.session.commit()
            
            self.assertIsNotNone(leave.leave_id)
            self.assertEqual(leave.status, 'Pending')  # Default status
            self.assertTrue(leave.is_pending())
    
    def test_leave_calculate_days(self):
        """
        Test calculate_days() method.
        
        Calculate values
        """
        with app.app_context():
            dept = Department(name='Design', description='Design Team')
            role = Role(title='Designer', description='UX Designer')
            db.session.add(dept)
            db.session.add(role)
            db.session.commit()
            
            emp = Employee(
                name='Emma Wilson',
                email='emma@test.com',
                phone='555-2222',
                department_id=dept.department_id,
                role_id=role.role_id,
                salary=65000,
                date_joined=date.today()
            )
            db.session.add(emp)
            db.session.commit()
            
            # 5-day leave request
            leave = LeaveRequest(
                employee_id=emp.employee_id,
                start_date=date(2024, 6, 10),
                end_date=date(2024, 6, 14),
                leave_type='Annual',
                reason='Summer vacation'
            )
            db.session.add(leave)
            db.session.commit()
            
            # 10, 11, 12, 13, 14 = 5 days
            self.assertEqual(leave.calculate_days(), 5)
    
    def test_leave_approve_reject(self):
        """
        Test approve() and reject() methods.
        
        Test object methods
        """
        with app.app_context():
            dept = Department(name='Legal', description='Legal Department')
            role = Role(title='Lawyer', description='Legal Counsel')
            db.session.add(dept)
            db.session.add(role)
            db.session.commit()
            
            emp = Employee(
                name='Frank Miller',
                email='frank@test.com',
                phone='555-3333',
                department_id=dept.department_id,
                role_id=role.role_id,
                salary=90000,
                date_joined=date.today()
            )
            db.session.add(emp)
            db.session.commit()
            
            leave = LeaveRequest(
                employee_id=emp.employee_id,
                start_date=date(2024, 7, 1),
                end_date=date(2024, 7, 2),
                leave_type='Personal',
                reason='Personal matter'
            )
            db.session.add(leave)
            db.session.commit()
            
            # Initially pending
            self.assertTrue(leave.is_pending())
            
            # Approve
            leave.approve()
            db.session.commit()
            self.assertEqual(leave.status, 'Approved')
            self.assertFalse(leave.is_pending())
            self.assertIsNotNone(leave.reviewed_at)
            
            # Create another for rejection test
            leave2 = LeaveRequest(
                employee_id=emp.employee_id,
                start_date=date(2024, 8, 1),
                end_date=date(2024, 8, 2),
                leave_type='Annual',
                reason='Vacation'
            )
            db.session.add(leave2)
            db.session.commit()
            
            # Reject
            leave2.reject()
            db.session.commit()
            self.assertEqual(leave2.status, 'Rejected')
            self.assertIsNotNone(leave2.reviewed_at)


def run_model_tests():
    """
    Run all model tests.
    
    Test with unittest framework
    """
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestUserModel))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDepartmentModel))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEmployeeModel))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLeaveRequestModel))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == '__main__':
    # Run tests when executed directly
    success = run_model_tests()
    sys.exit(0 if success else 1)
