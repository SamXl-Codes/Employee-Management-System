"""
Integration Tests for WorkFlowX System

Tests complete workflows and integration between components:
- User authentication flow
- Employee management workflow
- Leave request approval workflow  
- API endpoint integration
- Database transactions

Week 3 Concept: Integration testing
Week 8 Concept: Testing API endpoints
Week 9 Concept: Testing complete user workflows
"""

import unittest
import sys
import os
import json
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
import repository as repo


class TestAuthenticationFlow(unittest.TestCase):
    """Test complete authentication workflow."""
    
    def setUp(self):
        """Set up test client and database."""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
            repo.create_user('admin', 'admin123', 'admin')
    
    def tearDown(self):
        """Clean up test database."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_login_success(self):
        """Test successful login flow."""
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
    
    def test_login_failure(self):
        """Test failed login with wrong credentials."""
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid', response.data)
    
    def test_logout(self):
        """Test logout flow."""
        # Login first
        self.client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        # Then logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


class TestEmployeeManagementWorkflow(unittest.TestCase):
    """Test complete employee management workflow."""
    
    def setUp(self):
        """Set up test client and database."""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
            repo.create_user('admin', 'admin123', 'admin')
            repo.create_department('Engineering', 'Engineering Team')
            repo.create_role('Developer', 'Software Developer')
    
    def tearDown(self):
        """Clean up test database."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def login_as_admin(self):
        """Helper method to login as admin."""
        self.client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
    
    def test_view_employees_page(self):
        """Test viewing employees page requires login."""
        # Without login should redirect
        response = self.client.get('/employees')
        self.assertEqual(response.status_code, 302)
        
        # With login should work
        self.login_as_admin()
        response = self.client.get('/employees')
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_access(self):
        """Test dashboard access requires authentication."""
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        self.login_as_admin()
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)


class TestAPIEndpoints(unittest.TestCase):
    """
    Test REST API endpoints.
    
    Week 8 Concept: Testing REST APIs
    Week 8 Concept: JSON response validation
    """
    
    def setUp(self):
        """Set up test client and database."""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
            repo.create_user('admin', 'admin123', 'admin')
            _, _, dept = repo.create_department('IT', 'IT Department')
            _, _, role = repo.create_role('Developer', 'Developer Role')
            repo.create_employee('Test Employee', 'test@example.com', '555-1234',
                                dept.department_id, role.role_id, 75000, date.today())
    
    def tearDown(self):
        """Clean up test database."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def login_as_admin(self):
        """Helper method to login."""
        self.client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
    
    def test_api_employees_endpoint(self):
        """
        Test /api/employees REST endpoint.
        
        Week 8 Concept: REST API testing with JSON responses
        """
        self.login_as_admin()
        response = self.client.get('/api/employees')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        # Parse JSON response
        data = json.loads(response.data)
        
        # Verify structure
        self.assertIn('success', data)
        self.assertIn('count', data)
        self.assertIn('employees', data)
        
        # Verify data
        self.assertTrue(data['success'])
        self.assertGreater(data['count'], 0)
        self.assertIsInstance(data['employees'], list)
    
    def test_api_stats_endpoint(self):
        """Test /api/stats REST endpoint."""
        self.login_as_admin()
        response = self.client.get('/api/stats')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('success', data)
        self.assertIn('data', data)
        self.assertTrue(data['success'])
    
    def test_api_requires_authentication(self):
        """Test API endpoints require authentication."""
        # Without login should redirect
        response = self.client.get('/api/employees')
        self.assertEqual(response.status_code, 302)


class TestDataExport(unittest.TestCase):
    """Test data export functionality."""
    
    def setUp(self):
        """Set up test client."""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
            repo.create_user('admin', 'admin123', 'admin')
            _, _, dept = repo.create_department('Sales', 'Sales Team')
            _, _, role = repo.create_role('Manager', 'Sales Manager')
            repo.create_employee('Export Test', 'export@test.com', '555-9999',
                                dept.department_id, role.role_id, 80000, date.today())
    
    def tearDown(self):
        """Clean up test database."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def login_as_admin(self):
        """Helper to login."""
        self.client.post('/login', data={'username': 'admin', 'password': 'admin123'})
    
    def test_csv_export(self):
        """
        Test CSV export functionality.
        
        Week 6 Concept: CSV file generation and download
        """
        self.login_as_admin()
        response = self.client.get('/export/employees/csv')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'text/csv')
        self.assertIn('attachment', response.headers.get('Content-Disposition', ''))
    
    def test_json_export(self):
        """
        Test JSON export functionality.
        
        Week 6 Concept: JSON file generation
        """
        self.login_as_admin()
        response = self.client.get('/export/employees/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        # Verify valid JSON
        data = json.loads(response.data)
        self.assertIsInstance(data, list)


class TestCompleteUserJourney(unittest.TestCase):
    """
    Test complete user journey from login to task completion.
    
    Week 9 Concept: End-to-end integration testing
    """
    
    def setUp(self):
        """Set up complete test environment."""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
            # Create admin user
            repo.create_user('admin', 'admin123', 'admin')
            # Create department and role
            _, _, self.dept = repo.create_department('HR', 'HR Department')
            _, _, self.role = repo.create_role('HR Manager', 'HR Manager Role')
    
    def tearDown(self):
        """Clean up."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_admin_complete_workflow(self):
        """
        Test admin workflow: Login -> View Dashboard -> Manage Employees.
        
        Integration of multiple system components.
        """
        # Step 1: Login
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Access dashboard
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        
        # Step 3: View employees
        response = self.client.get('/employees')
        self.assertEqual(response.status_code, 200)
        
        # Step 4: Access departments
        response = self.client.get('/departments')
        self.assertEqual(response.status_code, 200)
        
        # Step 5: Access roles
        response = self.client.get('/roles')
        self.assertEqual(response.status_code, 200)
        
        # Step 6: Logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


def run_integration_tests():
    """Run all integration tests."""
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAuthenticationFlow))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEmployeeManagementWorkflow))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAPIEndpoints))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDataExport))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCompleteUserJourney))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)
