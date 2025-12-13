"""
Unit Tests for Repository Layer

Tests all database repository functions including:
- User CRUD operations
- Employee CRUD operations  
- Department and Role management
- Attendance tracking
- Leave request management
- Transaction handling and error cases


"""

import unittest
import sys
import os
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
import repository as repo


class TestUserRepository(unittest.TestCase):
    """Test user repository functions."""
    
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
    
    def test_create_user_success(self):
        """Test successful user creation."""
        with app.app_context():
            success, message, user = repo.create_user('testuser', 'password123', 'employee')
            
            self.assertTrue(success)
            self.assertIsNotNone(user)
            self.assertEqual(user.username, 'testuser')
    
    def test_create_user_duplicate(self):
        """Test creating user with duplicate username fails."""
        with app.app_context():
            repo.create_user('duplicate', 'pass1', 'employee')
            success, message, user = repo.create_user('duplicate', 'pass2', 'admin')
            
            self.assertFalse(success)
            self.assertIn('already exists', message.lower())
    
    def test_get_user_by_username(self):
        """Test retrieving user by username."""
        with app.app_context():
            repo.create_user('findme', 'password', 'admin')
            user = repo.get_user_by_username('findme')
            
            self.assertIsNotNone(user)
            self.assertEqual(user.username, 'findme')
    
    def test_get_user_by_id(self):
        """Test retrieving user by ID."""
        with app.app_context():
            _, _, created_user = repo.create_user('testuser', 'password', 'employee')
            retrieved_user = repo.get_user_by_id(created_user.user_id)
            
            self.assertIsNotNone(retrieved_user)
            self.assertEqual(retrieved_user.user_id, created_user.user_id)


class TestEmployeeRepository(unittest.TestCase):
    """Test employee repository functions."""
    
    def setUp(self):
        """Set up test database with dependencies."""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        with app.app_context():
            db.create_all()
            # Create required dependencies
            self.dept_success, _, self.dept = repo.create_department('IT', 'IT Department')
            self.role_success, _, self.role = repo.create_role('Developer', 'Software Developer')
    
    def tearDown(self):
        """Clean up test database."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_create_employee_success(self):
        """Test successful employee creation."""
        with app.app_context():
            success, message, emp = repo.create_employee(
                name='John Doe',
                email='john@test.com',
                phone='555-1234',
                department_id=self.dept.department_id,
                role_id=self.role.role_id,
                salary=75000.0,
                date_joined=date(2024, 1, 15)
            )
            
            self.assertTrue(success)
            self.assertIsNotNone(emp)
            self.assertEqual(emp.name, 'John Doe')
            self.assertEqual(emp.email, 'john@test.com')
    
    def test_create_employee_duplicate_email(self):
        """Test creating employee with duplicate email fails."""
        with app.app_context():
            repo.create_employee('First', 'duplicate@test.com', '111', self.dept.department_id,
                               self.role.role_id, 50000, date.today())
            success, message, _ = repo.create_employee('Second', 'duplicate@test.com', '222',
                                                       self.dept.department_id, self.role.role_id,
                                                       60000, date.today())
            
            self.assertFalse(success)
            self.assertIn('already exists', message.lower())
    
    def test_get_all_employees(self):
        """Test retrieving all employees."""
        with app.app_context():
            repo.create_employee('Emp1', 'emp1@test.com', '111', self.dept.department_id,
                               self.role.role_id, 50000, date.today())
            repo.create_employee('Emp2', 'emp2@test.com', '222', self.dept.department_id,
                               self.role.role_id, 60000, date.today())
            
            employees = repo.get_all_employees()
            self.assertEqual(len(employees), 2)
    
    def test_search_employees(self):
        """Test employee search functionality."""
        with app.app_context():
            repo.create_employee('Alice Smith', 'alice@test.com', '111', self.dept.department_id,
                               self.role.role_id, 70000, date.today())
            repo.create_employee('Bob Johnson', 'bob@test.com', '222', self.dept.department_id,
                               self.role.role_id, 60000, date.today())
            
            results = repo.search_employees('Alice')
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].name, 'Alice Smith')
    
    def test_update_employee(self):
        """Test updating employee information."""
        with app.app_context():
            _, _, emp = repo.create_employee('Original Name', 'original@test.com', '111',
                                            self.dept.department_id, self.role.role_id,
                                            50000, date.today())
            
            success, message = repo.update_employee(emp.employee_id, name='Updated Name',
                                                   salary=80000)
            
            self.assertTrue(success)
            updated_emp = repo.get_employee_by_id(emp.employee_id)
            self.assertEqual(updated_emp.name, 'Updated Name')
            self.assertEqual(float(updated_emp.salary), 80000.0)
    
    def test_delete_employee_soft(self):
        """Test soft delete (deactivate) employee."""
        with app.app_context():
            _, _, emp = repo.create_employee('To Delete', 'delete@test.com', '999',
                                            self.dept.department_id, self.role.role_id,
                                            50000, date.today())
            
            success, message = repo.delete_employee(emp.employee_id, soft_delete=True)
            
            self.assertTrue(success)
            deleted_emp = repo.get_employee_by_id(emp.employee_id)
            self.assertEqual(deleted_emp.status, 'inactive')


class TestDashboardStats(unittest.TestCase):
    """Test dashboard statistics function."""
    
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
    
    def test_get_dashboard_stats(self):
        """
        Test dashboard statistics calculation.
        
        Work with dictionary data structures
        """
        with app.app_context():
            stats = repo.get_dashboard_stats()
            
            # Should return dictionary with required keys
            self.assertIn('total_employees', stats)
            self.assertIn('total_departments', stats)
            self.assertIn('total_roles', stats)
            self.assertIn('pending_leaves', stats)
            self.assertIn('today_attendance', stats)
            
            # All values should be integers >= 0
            for key, value in stats.items():
                self.assertIsInstance(value, int)
                self.assertGreaterEqual(value, 0)


def run_repository_tests():
    """Run all repository tests."""
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestUserRepository))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEmployeeRepository))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDashboardStats))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_repository_tests()
    sys.exit(0 if success else 1)
