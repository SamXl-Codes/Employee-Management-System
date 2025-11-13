# WorkFlowX Employee Management System

A Flask web application for managing employees, attendance, and leave requests. Built for CA-2 (Advanced Programming Techniques) project.

**Team:** Samuel Ogunlusi (20086108) & George M. Sherman (20079442)

## Quick Start

**Need to run this fast?** Check `docs/QUICK_START.md` for the 5-minute setup.

### What You Need
- Python 3.11 or higher
- That's it! (SQLite comes with Python)

### Setup

```powershell
# 1. Install packages
pip install -r requirements.txt

# 2. Create database with sample data
python init_data.py

# 3. Run the app
python main.py

# 4. Open browser
http://localhost:5000
```

Login with: **admin** / **admin123**

### Running Tests

```powershell
# All tests
python run_tests.py

# Specific tests
python run_tests.py models
python run_tests.py utils
python run_tests.py integration
```

All 45+ tests should pass.

## What It Does

- **Employee Management** - Add/edit/delete employee records with validation
- **Attendance Tracking** - Daily attendance with automatic percentage calculation
- **Leave Requests** - Submit and approve/reject leave requests
- **Reports** - Generate summaries, export to CSV/JSON
- **Audit Logs** - Track who did what and when
- **REST API** - JSON endpoints for employees and statistics
5. **Data Export**: Export employee data to CSV and JSON formats
6. **Bulk Import**: CSV file upload with row-by-row validation and error reporting
7. **Authentication**: Secure login with password hashing and session management
8. **Authorization**: Role-based access control (Admin vs Employee)
9. **Audit Logging**: Track all CRUD operations with user, timestamp, and IP address
10. **REST API**: JSON endpoints for external system integration

### Non-Functional Requirements (NFR)
- **Performance**: Page load < 2 seconds, support 50+ concurrent users
- **Security**: Password hashing (PBKDF2), SQL injection prevention (ORM), XSS protection
- **Usability**: Responsive UI, clear error messages, intuitive navigation
- **Maintainability**: MVC architecture, comprehensive docstrings, PEP 8 compliance
- **Testability**: 45+ unit/integration tests with 85%+ code coverage

### Software Development Life Cycle (SDLC)
**Methodology**: Agile (Iterative Development)  
**Justification**: Flexible requirements, incremental delivery, continuous testing, team collaboration

## 📁 Project Structure

```
workflowx/
├── app.py                 # Flask app initialization & SQLite config (CA-2 requirement)
├── main.py               # Entry point
├── models.py             # SQLAlchemy ORM models (520+ lines, Week 9: OOP)
├── routes.py             # Route handlers & business logic (1400+ lines, MVC Controller)
├── repository.py         # Data access layer (Week 7: Database operations)
├── utils.py              # Validation & utility functions (Week 5: Regex)
├── config.py             # Configuration settings (SQLite)
├── init_data.py          # Sample data initialization
├── requirements.txt      # Python dependencies (NO PostgreSQL)
├── run_tests.py          # Test suite runner
├── README.md             # Project documentation
├── ARCHITECTURE.md       # UML diagrams and design documentation
├── CA2_REPORT_TEMPLATE.md  # Report template (800-1000 words)
├── SUBMISSION_CHECKLIST.md  # Final submission checklist
├── replit.md             # Comprehensive project documentation
│
├── templates/            # Jinja2 HTML templates (31 templates)
│   ├── base.html                    # Base layout template
│   ├── login.html                   # Authentication
│   ├── dashboard.html               # Admin dashboard
│   ├── employees.html               # Employee list & CRUD
│   ├── departments.html             # Department management
│   ├── roles.html                   # Role management
│   ├── attendance.html              # Attendance tracking
│   ├── leave_requests.html          # Leave management
│   ├── reports.html                 # Advanced reporting with Chart.js
│   ├── import_employees.html        # Bulk CSV import
│   ├── audit_logs.html              # Audit trail viewer
│   ├── employee_dashboard.html      # Employee self-service portal
│   ├── employee_profile.html        # Employee profile view
│   ├── employee_leave_history.html  # Leave history viewer
│   ├── employee_attendance.html     # Attendance records viewer
│   └── ... (error pages, modals)
│
├── static/               # Static assets
│   └── css/style.css     # Custom styles
│
└── requirements.txt      # Python dependencies (for reference)
```

## ✨ Features Implemented

### 1. **Employee Management** ✅
- CRUD operations (Create, Read, Update, Delete)
- Employee listing with filtering
- Batch operations on employee records
- Email & phone validation

### 2. **Bulk Employee Import** ✅
- CSV file upload with validation
- Row-by-row error reporting
- Downloadable CSV template
- Batch creation with transaction rollback on errors

### 3. **Department & Role Management** ✅
- Create/edit/delete departments
- Role hierarchy management
- Employee assignment to departments/roles

### 4. **Attendance Tracking** ✅
- Daily attendance recording (Present/Absent/Late)
- Attendance history viewing
- Statistics and reporting

### 5. **Leave Request Management** ✅
- Employee leave request submission
- Admin approval/rejection workflow
- Leave type categorization (Sick, Vacation, Personal)
- Automatic day calculation

### 6. **Advanced Reporting & Analytics** ✅
- **Attendance Summary**: Employee attendance statistics with percentage calculations
- **Leave Summary**: Leave request analytics by status
- **Payroll Summary**: Salary analysis by department
- Date range filtering
- Department filtering
- **Chart.js Integration**: 
  - Bar charts for attendance trends
  - Doughnut charts for leave distribution
  - Pie charts for payroll breakdown

### 7. **Email Notifications** ✅
- Automated email on leave approval/rejection
- Employee notification system
- Email logging for compliance

### 8. **Employee Self-Service Portal** ✅
- Personal dashboard with attendance rate
- Profile viewing
- Leave request history
- Attendance records tracking

### 9. **Comprehensive Audit Logging** ✅
- Track all CRUD operations (CREATE, UPDATE, DELETE)
- Action-specific logging (APPROVE, REJECT)
- User, timestamp, IP address tracking
- Admin audit trail viewer with filtering

### 10. **Data Export** ✅
- Employee data export (CSV/JSON)
- Leave summary export
- Customizable report generation

## 🔐 Security Features

- **Password Hashing**: Werkzeug PBKDF2 algorithm
- **Session Management**: Secure cookie-based authentication
- **Input Validation**: Regex validation for email, phone, dates
- **SQL Injection Prevention**: SQLAlchemy parameterized queries
- **Authorization**: Role-based access control (Admin/Employee)
- **Audit Trail**: Complete operation logging for compliance

## 🏗️ Architecture

### MVC Pattern
- **Models** (`models.py`): Database entities with OOP principles
- **Views** (`templates/`): Jinja2 templates for UI rendering
- **Controllers** (`routes.py`): Request handlers and business logic

### Repository Pattern
- **Repository** (`repository.py`): Data access abstraction layer
- Encapsulates all database operations
- Easier testing and potential database migration

### Layered Architecture
1. **Route Handler**: HTTP request entry point
2. **Validation**: Input sanitization & validation
3. **Repository**: Database operations
4. **Model**: Data representation & relationships
5. **Template**: HTML rendering

## 🗄️ Database Schema

### Tables
- `users`: User accounts and authentication
- `employees`: Employee records with details
- `departments`: Organizational units
- `roles`: Job titles and positions
- `attendance`: Daily attendance records
- `leave_requests`: Leave application records
- `audit_logs`: Complete operation audit trail

### Relationships
```
Employee → Department (many-to-one)
Employee → Role (many-to-one)
Employee → Attendance (one-to-many)
Employee → LeaveRequest (one-to-many)
User → AuditLog (one-to-many)
```

## 📊 Technologies Used

### Backend
- **Flask 3.0.0**: Python web framework (Week 8: Networking)
- **SQLAlchemy 2.0.23**: ORM for database operations (Week 7: Database)
- **SQLite**: Lightweight relational database (**CA-2 Requirement**)
- **Werkzeug 3.0.1**: Security utilities for password hashing (Week 9: Security)

### Frontend
- **Jinja2**: Template engine
- **Tailwind CSS**: Utility-first CSS framework
- **Chart.js**: Data visualization library
- **Google Fonts**: Inter & Roboto Mono typefaces

### Deployment
- **Gunicorn**: WSGI HTTP server
- **Replit**: Development and hosting platform

## 🎓 Academic Concepts Demonstrated

The code demonstrates Python concepts from Week 1-9:

- **Week 1**: Variables, data types, operators
- **Week 2**: Control flow (if/else), loops
- **Week 3**: Functions, decorators, custom validation
- **Week 4**: Lists, list comprehensions, tuples
- **Week 5**: Dictionaries, nested structures, data transformation
- **Week 6**: File handling (CSV, JSON), data export
- **Week 7**: String formatting, manipulation
- **Week 8**: Functions for code reuse, API design
- **Week 9**: OOP (classes, inheritance), security, authentication, logging

## 📝 Key Code Examples

### OOP Model Definition (Week 9)
```python
class Employee(db.Model):
    """Employee model with OOP encapsulation."""
    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def get_full_info(self):
        return f"{self.name} ({self.email})"
```

### List Comprehension & Dictionary (Week 4-5)
```python
attendance_data = [{
    'employee': emp.name,
    'attendance_rate': round((present_days / total_days * 100), 1)
} for emp in employees]
```

### Function Decorator (Week 3, 9)
```python
def admin_required(f):
    """Authorization decorator for admin-only routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = repo.get_user_by_id(session['user_id'])
        if not user or user.role != 'admin':
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function
```

## 🧪 Testing

Test scripts included:
- `test_mvp.py`: MVP feature testing
- `test_bulk_import.py`: Bulk import validation
- `test_import.csv`: Sample import data

Run tests:
```bash
python test_mvp.py
python test_bulk_import.py
```

## 📖 Documentation

- `replit.md`: Comprehensive project documentation
- `design_guidelines.md`: UI/UX design specifications
- Inline code comments explaining key concepts

## 🚀 Deployment

### Local Development
```bash
python main.py
```

### Production (Gunicorn)
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
```

### Docker (Optional)
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
```

## 📞 Support

For questions about the code structure or features, refer to:
- `replit.md` for architecture documentation
- Inline code comments for specific implementations
- `design_guidelines.md` for UI decisions

## 📄 License

Academic Project - CA-2 Advanced Programming Techniques

---

**Built with Flask, SQLAlchemy, PostgreSQL, and Tailwind CSS**

**Demonstrates comprehensive Python programming from fundamentals to enterprise patterns**
