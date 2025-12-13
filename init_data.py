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
    
    Handle errors gracefully
    Database configuration
    """
    try:
        print("🚀 Starting data initialization...")
        
        with app.app_context():
            # Clear existing data (for fresh start)
            print("📝 Clearing existing data...")
            db.drop_all()
            db.create_all()
            
            # Create Users
            print("👤 Creating users...")
            admin = User(username='admin', password='admin123', role='admin')
            
            db.session.add(admin)
            db.session.commit()
            print("✅ Created admin user")
            
            
            print("🏢 Creating departments...")
            departments = [
                Department('Technology & Infrastructure', 'IT operations, software development, cloud infrastructure, and technical services'),
                Department('Human Resources', 'Employee management and recruitment'),
                Department('Sales', 'Customer acquisition and revenue generation'),
                Department('Marketing', 'Brand management and promotion'),
                Department('Finance', 'Financial planning and accounting'),
            ]
            
            for dept in departments:
                db.session.add(dept)
            
            db.session.commit()
            print(f"✅ Created {len(departments)} departments")
            
            
            print("💼 Creating job roles...")
            roles = [
                # Technology & Infrastructure Roles
                Role('Software Engineer', 'Design and develop software applications'),
                Role('Senior Software Engineer', 'Lead technical projects and mentor junior engineers'),
                Role('DevOps Engineer', 'Manage infrastructure, CI/CD pipelines, and deployments'),
                Role('Database Administrator', 'Manage and optimize database systems and data integrity'),
                Role('Cloud Architect', 'Design and implement cloud infrastructure solutions'),
                Role('Cloud Engineer', 'Deploy and maintain cloud computing services'),
                Role('Network Engineer', 'Design, implement, and maintain network infrastructure'),
                Role('Security Engineer', 'Protect systems and data from cyber threats'),
                Role('System Administrator', 'Manage servers, systems, and IT infrastructure'),
                Role('IT Support Specialist', 'Provide technical support and troubleshooting'),
                Role('Data Engineer', 'Build and maintain data pipelines and analytics infrastructure'),
                Role('Systems Analyst', 'Analyze and optimize business systems and processes'),
                Role('Project Manager', 'Lead and coordinate technology projects and teams'),
                Role('Chief Information Officer', 'Oversee all technology strategy and operations'),
                
                # Other Department Roles
                Role('Product Manager', 'Define product strategy and roadmap'),
                Role('HR Manager', 'Oversee recruitment and employee relations'),
                Role('Sales Executive', 'Drive sales and customer relationships'),
                Role('Marketing Specialist', 'Execute marketing campaigns'),
                Role('Financial Analyst', 'Analyze financial data and trends'),
            ]
            
            for role in roles:
                db.session.add(role)
            
            db.session.commit()
            print(f"✅ Created {len(roles)} job roles")
            
            # Create Employees
            # Company founded: December 2020 (5 years ago)
            # Department IDs: 1=Tech & Infrastructure, 2=HR, 3=Sales, 4=Marketing, 5=Finance
            # Role IDs: 1=Soft Eng, 2=Sr Soft Eng, 3=DevOps, 4=DBA, 5=Cloud Arch, 6=Cloud Eng, 7=Network Eng, 8=Security Eng, 9=SysAdmin, 10=IT Support, 11=Data Eng, 12=Systems Analyst, 13=PM, 14=CIO, 15=Prod Mgr, 16=HR Mgr, 17=Sales Exec, 18=Marketing Spec, 19=Financial Analyst
            print("👥 Creating employees...")
            employees_data = [
                # Founding team members (Dec 2020 - Early 2021) - Leadership
                ('John Smith', 'john.smith@workflowx.com', '555-0101', 1, 14, 150000, date(2020, 12, 1), 'john-smith.jpg'),  # CIO - Founder
                ('Emily Davis', 'emily.davis@workflowx.com', '555-0104', 2, 16, 85000, date(2020, 12, 15), 'emily-davis.jpg'),  # HR Manager - Founder
                ('Robert Taylor', 'robert.taylor@workflowx.com', '555-0107', 5, 19, 78000, date(2021, 1, 10), 'robert-taylor.jpg'),  # Financial Analyst
                ('Albert Dera', 'albert.dera@workflowx.com', '555-0201', 1, 5, 130000, date(2021, 1, 20), 'new useer man albert-dera-ILip77SbmOE-unsplash.jpg'),  # Cloud Architect
                ('Vicky Hladynets', 'vicky.hladynets@workflowx.com', '555-0202', 1, 13, 110000, date(2021, 2, 1), 'new use woman vicky-hladynets-C8Ta0gwPbQg-unsplash.jpg'),  # Project Manager
                
                # First year hires (2021) - Tech Team
                ('Michael Chen', 'michael.chen@workflowx.com', '555-0103', 1, 3, 92000, date(2021, 3, 15), 'michael-chen.jpg'),  # DevOps Engineer
                ('Aiony Haust', 'aiony.haust@workflowx.com', '555-0203', 1, 4, 95000, date(2021, 4, 10), 'new user woman aiony-haust-3TLl_97HNJo-unsplash.jpg'),  # Database Administrator
                ('Ali Morshedlou', 'ali.morshedlou@workflowx.com', '555-0204', 1, 8, 98000, date(2021, 5, 5), 'new user man ali-morshedlou-WMD64tMfc4k-unsplash.jpg'),  # Security Engineer
                ('Christopher Campbell', 'christopher.campbell@workflowx.com', '555-0205', 1, 7, 88000, date(2021, 6, 1), 'new user woman christopher-campbell-rDEOVtE7vOs-unsplash.jpg'),  # Network Engineer
                ('Jennifer Garcia', 'jennifer.garcia@workflowx.com', '555-0110', 4, 18, 69000, date(2021, 6, 20), 'jennifer-garcia.jpg'),  # Marketing Specialist
                ('Darshan Patel', 'darshan.patel@workflowx.com', '555-0206', 1, 2, 105000, date(2021, 7, 15), 'new user man darshan-patel-QJEVpydulGs-unsplash.jpg'),  # Senior Software Engineer
                ('Joel Frank', 'joel.frank@workflowx.com', '555-0207', 1, 11, 90000, date(2021, 8, 10), 'new user woman joel-frank-T82OhMjnB-c-unsplash.jpg'),  # Data Engineer
                ('David Martinez', 'david.martinez@workflowx.com', '555-0105', 3, 17, 72000, date(2021, 9, 5), 'david-martinez.jpg'),  # Sales Executive
                ('Fotos Kakaroto', 'fotos.kakaroto@workflowx.com', '555-0208', 1, 9, 82000, date(2021, 10, 1), 'new user man fotos-8ISNp7BpXdM-unsplash.jpg'),  # System Administrator
                ('Luca Nicoletti', 'luca.nicoletti@workflowx.com', '555-0209', 1, 6, 86000, date(2021, 11, 15), 'new user woman luca-nicoletti-EqLXRA41jrA-unsplash.jpg'),  # Cloud Engineer
                
                # Second year hires (2022) - Growing Team
                ('Sarah Johnson', 'sarah.johnson@workflowx.com', '555-0102', 1, 1, 75000, date(2022, 2, 10), 'sarah-johnson.jpg'),  # Software Engineer
                ('Itay Verchik', 'itay.verchik@workflowx.com', '555-0210', 1, 1, 76000, date(2022, 3, 20), 'new user man itay-verchik-YmQ8TrsieE4-unsplash.jpg'),  # Software Engineer
                ('Michael Dam', 'michael.dam@workflowx.com', '555-0211', 1, 12, 80000, date(2022, 4, 15), 'new user woman michael-dam-mEZ3PoFGs_k-unsplash.jpg'),  # Systems Analyst
                ('Jadon Johnson', 'jadon.johnson@workflowx.com', '555-0212', 1, 10, 65000, date(2022, 5, 1), 'new user man jadon-johnson-58nrhtlvhwM-unsplash.jpg'),  # IT Support Specialist
                ('Tran Nhu Tuan', 'tran.nhutuan@workflowx.com', '555-0213', 3, 17, 70000, date(2022, 6, 10), 'new user woman tran-nhu-tuan-Ydnhp9z0FOU-unsplash.jpg'),  # Sales Executive
                ('Jessica Wilson', 'jessica.wilson@workflowx.com', '555-0106', 4, 18, 68000, date(2022, 7, 15), 'jessica-wilson.jpg'),  # Marketing Specialist
                ('Jonas Kakaroto', 'jonas.kakaroto@workflowx.com', '555-0214', 1, 1, 74000, date(2022, 8, 20), 'new user man jonas-kakaroto-KIPqvvTOC1s-unsplash.jpg'),  # Software Engineer
                ('Amanda Brown', 'amanda.brown@workflowx.com', '555-0108', 1, 1, 73000, date(2022, 9, 5), 'amanda-brown.jpg'),  # Software Engineer
                ('Jurica Koletic', 'jurica.koletic@workflowx.com', '555-0216', 1, 15, 95000, date(2022, 10, 15), 'new user man jurica-koletic-7YVZYZeITc8-unsplash.jpg'),  # Product Manager
                ('Agnes Ogbe', 'agnes.ogbe@workflowx.com', '555-0108', 1, 2, 105000, date(2022, 11, 1), 'agnes-ogbe.jpeg'),  # Senior Software Engineer
                
                # Recent hires (2023-2024) - Latest Additions
                ('Ransford Quaye', 'ransford.quaye@workflowx.com', '555-0217', 5, 19, 76000, date(2023, 4, 1), 'new user man ransford-quaye-DzAFv1iVMGg-unsplash.jpg'),  # Financial Analyst
                ('Redd Francisco', 'redd.francisco@workflowx.com', '555-0218', 1, 3, 91000, date(2023, 6, 15), 'new user man redd-francisco-v6771a4avV4-unsplash.jpg'),  # DevOps Engineer
                ('Samuel Ogunlusi', 'samuel.ogunlusi@workflowx.com', '555-0108', 1, 2, 105000, date(2023, 8, 10), 'samuel-ogunlusi.png'),  # Senior Software Engineer
                ('Ryan Hoffman', 'ryan.hoffman@workflowx.com', '555-0220', 1, 10, 64000, date(2023, 10, 1), 'new user man ryan-hoffman-v7Jja2ChN6s-unsplash.jpg'),  # IT Support Specialist
                ('Christopher Lee', 'chris.lee@workflowx.com', '555-0109', 3, 17, 68000, date(2024, 1, 15), 'christopher-lee.jpg'),  # Sales Executive
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
                # Assign profile image if provided
                if len(emp_data) > 7:
                    emp.profile_image = emp_data[7]
                employees.append(emp)
                db.session.add(emp)
            
            db.session.commit()
            print(f"✅ Created {len(employees)} employees")
            
            
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
            
            
            print("📅 Creating realistic attendance records based on hire dates...")
            import random
            random.seed(42)  # For reproducible "random" data
            attendance_count = 0
            
            today = date.today()
            
            # Create attendance for each employee from their hire date to today
            for emp in employees:
                # Start from hire date
                current_date = emp.date_joined
                
                # Generate attendance only for weekdays (Monday-Friday)
                while current_date <= today:
                    # Skip weekends (Saturday=5, Sunday=6)
                    if current_date.weekday() < 5:
                        # Realistic attendance patterns:
                        # - 88% Present, 7% Absent, 5% Late
                        # - Employees with longer tenure have slightly better attendance
                        days_employed = (today - emp.date_joined).days
                        
                        if days_employed > 730:  # 2+ years
                            status_choice = random.choices(
                                ['Present', 'Absent', 'Late'],
                                weights=[90, 5, 5],
                                k=1
                            )[0]
                        elif days_employed > 365:  # 1-2 years
                            status_choice = random.choices(
                                ['Present', 'Absent', 'Late'],
                                weights=[88, 7, 5],
                                k=1
                            )[0]
                        else:  # Less than 1 year
                            status_choice = random.choices(
                                ['Present', 'Absent', 'Late'],
                                weights=[85, 10, 5],
                                k=1
                            )[0]
                        
                        attendance = Attendance(
                            employee_id=emp.employee_id,
                            date=current_date,
                            status=status_choice
                        )
                        db.session.add(attendance)
                        attendance_count += 1
                        
                        # Commit in batches to avoid memory issues
                        if attendance_count % 500 == 0:
                            db.session.commit()
                            print(f"   ... {attendance_count} records created")
                    
                    current_date += timedelta(days=1)
            
            db.session.commit()
            print(f"✅ Created {attendance_count} realistic attendance records (workdays only)")
            
            
            print("🏖️ Creating realistic leave requests based on employee tenure...")
            leave_requests = []
            leave_count = 0
            
            leave_reasons = {
                'Annual': ['Family vacation', 'Holiday trip', 'Personal travel', 'Wedding anniversary', 'Extended break'],
                'Sick': ['Medical appointment', 'Illness', 'Doctor visit', 'Medical procedure', 'Recovery'],
                'Personal': ['Personal matters', 'Family commitment', 'Moving house', 'Personal emergency', 'Family event']
            }
            
            # Generate realistic leave history for each employee
            for emp in employees:
                days_employed = (today - emp.date_joined).days
                years_employed = days_employed / 365.25
                
                # Employees take approximately 15-20 days leave per year
                # Plus some sick leave and personal days
                expected_annual_leaves = int(years_employed * random.randint(2, 4))  # 2-4 annual leaves per year
                expected_sick_leaves = int(years_employed * random.randint(1, 3))    # 1-3 sick leaves per year
                expected_personal_leaves = int(years_employed * random.randint(0, 2)) # 0-2 personal leaves per year
                
                # Generate past ANNUAL leaves (all approved)
                for _ in range(expected_annual_leaves):
                    # Random date in their employment period (excluding last 30 days)
                    days_range = max(60, days_employed - 30)
                    days_ago = random.randint(30, days_range)
                    leave_start = today - timedelta(days=days_ago)
                    leave_duration = random.randint(3, 10)  # 3-10 days
                    leave_end = leave_start + timedelta(days=leave_duration - 1)
                    
                    leave = LeaveRequest(
                        employee_id=emp.employee_id,
                        start_date=leave_start,
                        end_date=leave_end,
                        leave_type='Annual',
                        reason=random.choice(leave_reasons['Annual'])
                    )
                    leave.approve()  # Past leaves are approved
                    leave_requests.append(leave)
                    leave_count += 1
                
                # Generate past SICK leaves (all approved)
                for _ in range(expected_sick_leaves):
                    days_range = max(60, days_employed - 30)
                    days_ago = random.randint(30, days_range)
                    leave_start = today - timedelta(days=days_ago)
                    leave_duration = random.randint(1, 5)  # 1-5 days for sick leave
                    leave_end = leave_start + timedelta(days=leave_duration - 1)
                    
                    leave = LeaveRequest(
                        employee_id=emp.employee_id,
                        start_date=leave_start,
                        end_date=leave_end,
                        leave_type='Sick',
                        reason=random.choice(leave_reasons['Sick'])
                    )
                    leave.approve()
                    leave_requests.append(leave)
                    leave_count += 1
                
                # Generate past PERSONAL leaves (all approved)
                for _ in range(expected_personal_leaves):
                    days_range = max(60, days_employed - 30)
                    days_ago = random.randint(30, days_range)
                    leave_start = today - timedelta(days=days_ago)
                    leave_duration = random.randint(1, 3)  # 1-3 days for personal leave
                    leave_end = leave_start + timedelta(days=leave_duration - 1)
                    
                    leave = LeaveRequest(
                        employee_id=emp.employee_id,
                        start_date=leave_start,
                        end_date=leave_end,
                        leave_type='Personal',
                        reason=random.choice(leave_reasons['Personal'])
                    )
                    leave.approve()
                    leave_requests.append(leave)
                    leave_count += 1
                
                # Generate a few PENDING future leaves (20% chance per employee)
                if random.random() < 0.3 and years_employed > 0.5:  # Only for employees with 6+ months
                    leave_start = today + timedelta(days=random.randint(7, 60))
                    leave_duration = random.randint(3, 7)
                    leave_end = leave_start + timedelta(days=leave_duration - 1)
                    
                    leave = LeaveRequest(
                        employee_id=emp.employee_id,
                        start_date=leave_start,
                        end_date=leave_end,
                        leave_type=random.choice(['Annual', 'Personal']),
                        reason=random.choice(leave_reasons['Annual'] + leave_reasons['Personal'])
                    )
                    # Leave as pending
                    leave_requests.append(leave)
                    leave_count += 1
            
            # Add all leave requests to database
            for leave in leave_requests:
                db.session.add(leave)
            
            db.session.commit()
            print(f"✅ Created {leave_count} realistic leave requests (approved historical + some pending)")
            
            print("\n" + "=" * 70)
            print("🎉 Database initialization completed successfully!")
            print("=" * 70)
            print("\n📋 Summary:")
            print(f"   Users: {employee_users_created + 1} (1 admin + {employee_users_created} employees)")
            print(f"   Departments: {len(departments)}")
            print(f"   Job Roles: {len(roles)}")
            print(f"   Employees: {len(employees)}")
            print(f"   Attendance Records: {attendance_count}")
            print(f"   Leave Requests: {leave_count}")
            print("\n📊 Data Authenticity:")
            print("   ✓ Company founded: December 2020 (5 years ago)")
            print("   ✓ Employee hire dates span from Dec 2020 to Jan 2024")
            print("   ✓ Attendance records generated from each employee's hire date")
            print("   ✓ Weekdays only (Monday-Friday) - no weekend records")
            print("   ✓ Leave requests realistic per employee tenure")
            print("   ✓ Historical data reflects years of employment accurately")
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
