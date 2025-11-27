"""
WorkFlowX - Database Initialization Script

This script populates the database with sample data for testing and demonstration.
Run this once to set up initial data.

Demonstrates:
- Database operations with transactions
- Exception handling
- Data population patterns
"""

from app import app, db
from models import User, Department, Role, Employee, Attendance, LeaveRequest
from datetime import date, timedelta
import sys


def create_sample_data():
    """
    Create sample data for the application.
    
    Week 3 Concept: Exception handling with try/except
    Week 7 Concept: Database transactions
    """
    try:
        print("🚀 Starting data initialization...")
        
        with app.app_context():
            # Clear existing data (for fresh start)
            print("📝 Clearing existing data...")
            db.drop_all()
            db.create_all()
            
            # Create Users (Week 4-5: OOP - creating instances)
            print("👤 Creating users...")
            admin = User(username='admin', password='admin123', role='admin')
            
            db.session.add(admin)
            db.session.commit()
            print("✅ Created admin user")
            
            # Create Departments (Week 2: Lists to store multiple items)
            print("🏢 Creating departments...")
            departments = [
                Department('Engineering', 'Software development and technical operations'),
                Department('Human Resources', 'Employee management and recruitment'),
                Department('Sales', 'Customer acquisition and revenue generation'),
                Department('Marketing', 'Brand management and promotion'),
                Department('Finance', 'Financial planning and accounting'),
            ]
            
            for dept in departments:
                db.session.add(dept)
            
            db.session.commit()
            print(f"✅ Created {len(departments)} departments")
            
            # Create Roles (Week 2: for loops for iteration)
            print("💼 Creating job roles...")
            roles = [
                Role('Software Engineer', 'Design and develop software applications'),
                Role('Senior Software Engineer', 'Lead technical projects and mentor junior engineers'),
                Role('Product Manager', 'Define product strategy and roadmap'),
                Role('HR Manager', 'Oversee recruitment and employee relations'),
                Role('Sales Executive', 'Drive sales and customer relationships'),
                Role('Marketing Specialist', 'Execute marketing campaigns'),
                Role('Financial Analyst', 'Analyze financial data and trends'),
                Role('DevOps Engineer', 'Manage infrastructure and deployments'),
            ]
            
            for role in roles:
                db.session.add(role)
            
            db.session.commit()
            print(f"✅ Created {len(roles)} job roles")
            
            # Create Employees (Week 4-5: OOP with complex objects)
            print("👥 Creating employees...")
            employees_data = [
                ('John Smith', 'john.smith@workflowx.com', '555-0101', 1, 2, 95000, date(2022, 1, 15)),
                ('Sarah Johnson', 'sarah.johnson@workflowx.com', '555-0102', 1, 1, 75000, date(2022, 3, 20)),
                ('Michael Chen', 'michael.chen@workflowx.com', '555-0103', 1, 8, 85000, date(2021, 6, 10)),
                ('Emily Davis', 'emily.davis@workflowx.com', '555-0104', 2, 4, 70000, date(2022, 2, 1)),
                ('David Martinez', 'david.martinez@workflowx.com', '555-0105', 3, 5, 65000, date(2022, 5, 15)),
                ('Jessica Wilson', 'jessica.wilson@workflowx.com', '555-0106', 4, 6, 68000, date(2022, 4, 10)),
                ('Robert Taylor', 'robert.taylor@workflowx.com', '555-0107', 5, 7, 72000, date(2021, 9, 5)),
                ('Amanda Brown', 'amanda.brown@workflowx.com', '555-0108', 1, 1, 73000, date(2023, 1, 12)),
                ('Christopher Lee', 'chris.lee@workflowx.com', '555-0109', 3, 5, 67000, date(2023, 2, 20)),
                ('Jennifer Garcia', 'jennifer.garcia@workflowx.com', '555-0110', 4, 6, 69000, date(2022, 8, 15)),
            ]
            
            employees = []
            for emp_data in employees_data:
                emp = Employee(
                    name=emp_data[0],
                    email=emp_data[1],
                    phone=emp_data[2],
                    department_id=emp_data[3],
                    role_id=emp_data[4],
                    salary=emp_data[5],
                    date_joined=emp_data[6]
                )
                employees.append(emp)
                db.session.add(emp)
            
            db.session.commit()
            print(f"✅ Created {len(employees)} employees")
            
            # Create user accounts for all employees (Week 2: for loops)
            print("🔐 Creating user accounts for employees...")
            default_password = 'WorkFlow@2025'  # Default password for all employees
            employee_users_created = 0
            
            for emp in employees:
                # Create user account with employee's email as username
                emp_user = User(
                    username=emp.email,
                    password=default_password,
                    role='employee'
                )
                db.session.add(emp_user)
                employee_users_created += 1
            
            db.session.commit()
            print(f"✅ Created {employee_users_created} employee user accounts (default password: {default_password})")
            
            # Create Attendance Records (Week 2: Loops and date calculations)
            print("📅 Creating attendance records...")
            attendance_count = 0
            
            # Create attendance for the last 5 days
            for i in range(5):
                attendance_date = date.today() - timedelta(days=i)
                
                # Mark attendance for each employee (Week 2: nested loops)
                for emp in employees:
                    # Simulate realistic attendance (Week 2: if/else)
                    import random
                    status_choice = random.choices(
                        ['Present', 'Absent', 'Late'],
                        weights=[85, 10, 5],  # 85% present, 10% absent, 5% late
                        k=1
                    )[0]
                    
                    attendance = Attendance(
                        employee_id=emp.employee_id,
                        date=attendance_date,
                        status=status_choice
                    )
                    db.session.add(attendance)
                    attendance_count += 1
            
            db.session.commit()
            print(f"✅ Created {attendance_count} attendance records")
            
            # Create Leave Requests (Week 5: Different data structures)
            print("🏖️ Creating leave requests...")
            leave_requests = [
                LeaveRequest(
                    employee_id=1,
                    start_date=date.today() + timedelta(days=10),
                    end_date=date.today() + timedelta(days=14),
                    leave_type='Annual',
                    reason='Family vacation'
                ),
                LeaveRequest(
                    employee_id=2,
                    start_date=date.today() + timedelta(days=5),
                    end_date=date.today() + timedelta(days=6),
                    leave_type='Sick',
                    reason='Medical appointment'
                ),
                LeaveRequest(
                    employee_id=3,
                    start_date=date.today() - timedelta(days=5),
                    end_date=date.today() - timedelta(days=3),
                    leave_type='Personal',
                    reason='Personal matters'
                ),
            ]
            
            # Approve the past leave request
            leave_requests[2].approve()
            
            for leave in leave_requests:
                db.session.add(leave)
            
            db.session.commit()
            print(f"✅ Created {len(leave_requests)} leave requests")
            
            print("\n" + "=" * 60)
            print("🎉 Database initialization completed successfully!")
            print("=" * 60)
            print("\n📋 Summary:")
            print(f"   Users: {employee_users_created + 1} (1 admin + {employee_users_created} employees)")
            print(f"   Departments: {len(departments)}")
            print(f"   Job Roles: {len(roles)}")
            print(f"   Employees: {len(employees)}")
            print(f"   Attendance Records: {attendance_count}")
            print(f"   Leave Requests: {len(leave_requests)}")
            print("\n🔐 Login Credentials:")
            print("\n   ADMIN:")
            print("     Username: admin")
            print("     Password: admin123")
            print("\n   ALL EMPLOYEES:")
            print(f"     Username: [their email address]")
            print(f"     Password: {default_password} (default for all)")
            print("\n   Example Employee Logins:")
            print("     - john.smith@workflowx.com / WorkFlow@2025")
            print("     - sarah.johnson@workflowx.com / WorkFlow@2025")
            print("     - michael.chen@workflowx.com / WorkFlow@2025")
            print("\n⚠️  IMPORTANT: Employees should change their password after first login.")
            print("   Contact IT Support for password reset assistance.")
            print("\n✨ You can now start the application and login!")
            
    except Exception as e:
        print(f"\n❌ Error during initialization: {str(e)}")
        db.session.rollback()
        sys.exit(1)


if __name__ == "__main__":
    create_sample_data()
