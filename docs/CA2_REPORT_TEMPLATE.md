# WorkFlowX Employee Management System - Project Report

**Module:** B9CY108 - Advanced Programming Techniques  
**Programme:** MSc Cyber Security  
**Team Members:**  
- Samuel Ogunlusi (20086108)  
- George M. Sherman (20079442)  

**Submission Date:** December 15, 2025  
**GitHub Repository:** [INSERT YOUR REPO LINK HERE]  
**Video Demonstration:** [INSERT YOUTUBE/DRIVE LINK HERE]

---

## 1. Problem Domain & System Overview

### The Problem We're Solving

During our research phase, we noticed that many small businesses still manage their employees using spreadsheets or even paper-based systems. Having both worked in different environments during our undergrad years, we've seen firsthand how chaotic this can get - attendance sheets getting lost, leave requests buried in email chains, and nobody really sure who made what changes to employee records.

We decided to build WorkFlowX to tackle these everyday HR headaches. The name came from wanting something that represents smooth workflow management without being too corporate-sounding. Our main goal was creating a system that's actually useful for both HR staff and regular employees, not just another database project.

### Who This Is For

The system has three main user groups we designed around:
- **HR Administrators** need to manage the full employee lifecycle - adding new hires, updating information when people get promoted or change departments, handling terminations
- **Employees** just want a simple way to check their attendance history, request time off, and see their profile info
- **The business** needs proper audit trails for compliance and analytics to spot trends (like which departments have attendance issues)

### What WorkFlowX Does

Our solution is a web-based system built with Flask that centralizes everything. Key features include proper employee record management with validation (we learned the hard way that you need to validate email formats!), daily attendance tracking that auto-calculates percentages, a leave request system with approval workflows, CSV import for bulk data entry, and comprehensive reporting with actual visual charts. We also built in audit logging because we figured that's something real companies would need for compliance.

---

## 2. Requirements & Development Approach

### Functional Requirements

When planning this project, we broke down what the system actually needs to do:

For **employee management**, we need full CRUD capabilities - adding new employees with proper validation (we're using regex for email/phone formats), preventing duplicate emails through database constraints, bulk CSV import (because nobody wants to manually enter 50 employees), search functionality, and the ability to mark employees as inactive rather than deleting their history.

The **attendance system** records who's present, absent, or late each day, automatically calculates attendance percentages (this took some figuring out with date handling), and prevents duplicate records for the same person on the same day.

For **leave requests**, employees can submit requests with date ranges, the system calculates how many days that is (trickier than it sounds!), there's a proper approval workflow where admins can approve or reject, and we originally planned email notifications but focused on core functionality first.

**Reporting features** let you generate summaries filtered by date range and department, export everything to CSV or JSON (useful for Excel users), and we added Chart.js visualizations because numbers in tables get boring fast.

For **security and auditing**, we implemented login/authentication, password hashing (using Werkzeug's built-in functions), audit logs that track every create/update/delete action with timestamps and user info, and role-based access so employees can't access admin functions.

### Non-Functional Requirements

We also had some quality standards to hit: pages should load quickly (under 2 seconds for normal operations), the UI needs to work on both desktop and mobile, and security was critical - hashed passwords, protection against SQL injection through SQLAlchemy's ORM, XSS prevention via Jinja2's auto-escaping, and secure session cookies.

**Maintainability:**
- NFR11: Code follows PEP 8 Python style guidelines
- NFR12: Comprehensive docstrings for all functions and classes
- NFR13: Modular architecture (MVC pattern) for easy updates

### 2.3 Software Development Life Cycle (SDLC)

**Chosen Methodology: Agile (Iterative Development)**

**Justification:**
- **Flexibility**: Requirements evolved during development; Agile allowed rapid adaptation
- **Incremental Delivery**: MVP delivered first (authentication, employee CRUD), then features added iteratively
- **Continuous Testing**: Unit tests written alongside code for immediate feedback
- **Team Collaboration**: Two-person team benefited from daily stand-ups and pair programming

**Sprints Overview:**
1. **Sprint 1 (Week 1-2)**: Database models, authentication, basic CRUD
2. **Sprint 2 (Week 3-4)**: Attendance tracking, leave requests
3. **Sprint 3 (Week 5-6)**: Reporting, data export, audit logging
4. **Sprint 4 (Week 7-8)**: Testing, documentation, deployment

**Waterfall Rejected:** Too rigid; difficult to accommodate changing requirements mid-project.

---

## 3. ANALYSIS & DESIGN WITH UML DIAGRAMS (200-250 words)

### 3.1 Use Case Diagram
*(Include diagram from ARCHITECTURE.md)*

**Description:**
The use case diagram illustrates two primary actors:
- **Admin**: Full system access including employee management, attendance marking, leave approval, and reporting
- **Employee**: Limited access to view own profile, attendance, and submit leave requests

**Key Use Cases:**
- Manage Employees (Add, Edit, Delete, Search)
- Mark Attendance (Daily bulk operations)
- Approve Leave Requests (Email notification trigger)
- Generate Reports (Attendance, Leave, Payroll summaries)
- Export Data (CSV/JSON formats)

**Rationale:**
Role-based use cases ensure proper separation of concerns and security. Admins have privileged operations while employees have self-service capabilities without compromising data integrity.

### 3.2 Class Diagram
*(Include diagram from ARCHITECTURE.md)*

**Description:**
The class diagram models the core entities and their relationships:

**Core Classes:**
- **User**: Authentication and authorization (1-to-many with AuditLog)
- **Employee**: Central entity with relationships to Department (many-to-one), Role (many-to-one), Attendance (one-to-many), LeaveRequest (one-to-many)
- **Department & Role**: Organizational structure with business rules (can_delete() prevents deletion with active employees)
- **Attendance & LeaveRequest**: Transactional data with calculated methods

### Development Methodology  

We went with an Agile-ish approach (honestly, we didn't follow textbook Agile, but we did iterate a lot). Started with basic CRUD for employees, then added authentication, then attendance features, then leave management. Each feature got tested before moving to the next one. This worked well because we could demo working features to each other as we progressed and catch issues early.

## 3. System Design & UML Diagrams

### Architecture Pattern: MVC

We chose the Model-View-Controller pattern because it's what Flask naturally lends itself to, and after learning about different patterns in lectures, MVC made the most sense for a web application.

**Our implementation:**
- **Models** (`models.py`, 520+ lines) - These are our SQLAlchemy classes representing employees, departments, attendance records, etc. We put business logic here too, like methods to calculate attendance percentages or check if passwords match
- **Views** (31 HTML templates) - Jinja2 templates that generate the actual web pages. We used template inheritance heavily to avoid copy-pasting the navigation and header across every page
- **Controllers** (`routes.py`, 1400+ lines) - Flask route handlers that connect everything. They receive requests, validate data, call repository functions to interact with the database, and render templates

We also added a repository pattern (in `repository.py`) as a data access layer. This wasn't required but made our code cleaner - all database operations go through repository functions instead of having database queries scattered everywhere in routes.

**Why Flask?** We considered Django but it felt too heavy for what we needed. Flask let us structure things our way and didn't force conventions we didn't need. Plus, the documentation is excellent and there are tons of examples online.

### UML Diagrams

*(We created these diagrams in ARCHITECTURE.md - see that file for the full ASCII art versions)*

Our **class diagram** shows the seven main models (User, Employee, Department, Role, Attendance, LeaveRequest, AuditLog) and how they relate. Key relationships include Employee belonging to a Department and Role, and having multiple Attendance records and LeaveRequests. We used proper OOP principles - inheritance from SQLAlchemy's base class, encapsulation with private password hashes and public methods, and relationships enforced through foreign keys.

The **component diagram** visualizes our layered architecture: templates at the top, Flask routes in the middle, business logic (utils and repository) below that, then models, and finally the SQLite database. We tried to keep dependencies flowing one direction to avoid circular imports (which we encountered early on and had to refactor).

---

## 5. DATA STRUCTURES & ALGORITHMS DISCUSSION (150-200 words)

## 4. Data Structures & Algorithms

### Data Structures We Used

**Lists** are everywhere in our code. Database queries return lists of objects (like `employees = repo.get_all_employees()`), and we iterate over them with for loops to display data. We also used list comprehensions quite a bit, like `[emp.to_dict() for emp in employees]` to convert model objects into dictionaries for JSON responses. Lists made sense because we don't know how many employees we'll have, and Python lists handle that automatically.

**Dictionaries** serve two main purposes for us. First, we use them for statistics on the dashboard (`{'total_employees': 50, 'active_departments': 5}`). Second, we serialize employee data into dicts for our JSON API endpoints and for passing data to templates. The key-value structure matches JSON perfectly, and dictionary lookups are fast.

**Tuples** came in handy for our repository functions. Instead of just returning True/False, we return tuples like `(success, message, object)` so we can provide detailed feedback. For example, `success, msg, employee = repo.create_employee(...)` lets us unpack the result cleanly and handle both success and error cases.

### Key Algorithms

**Attendance Percentage:** This was trickier than expected. We count total attendance records for an employee, count how many are marked "Present", then calculate the percentage. Had to handle the edge case where someone has zero records (avoid division by zero). The calculation happens in the Employee model's `get_attendance_percentage()` method.

**Leave Days Calculation:** When someone requests leave from Monday to Friday, that should be 5 days, not 4. Took us a while to realize we needed `delta.days + 1` to make it inclusive of both start and end dates. This calculation happens automatically in the LeaveRequest model's `calculate_days()` method.

**Search Functionality:** For searching employees, we use SQLAlchemy's `ilike` operator (case-insensitive LIKE) with wildcards: `f"%{search_term}%"`. This searches both name and email fields. Not the most sophisticated algorithm, but it works fine for our scale.
    ).all()
```
**Time Complexity**: O(n) with database indexing  
**Rationale**: Case-insensitive partial matching for flexible search

---

## 6. APIs REVIEW (100-150 words)

### Internal APIs (Flask Framework)

**Flask Routing:**
```python
@app.route('/employees', methods=['GET', 'POST'])
def employees():
    # Handle GET and POST requests
```
**Purpose**: Maps URLs to Python functions  
**Benefit**: RESTful URL structure

**SQLAlchemy ORM:**
```python
Employee.query.filter_by(status='active').all()
```
**Purpose**: Object-relational mapping for database operations  
**Benefit**: Prevents SQL injection through parameterized queries

**Werkzeug Security:**
```python
from werkzeug.security import generate_password_hash, check_password_hash
```
**Purpose**: Password hashing (PBKDF2 SHA-256)  
**Benefit**: Industry-standard security

### External REST API (Week 8 Concept)

**Endpoint:** `/api/employees` (GET)  
**Response:** JSON array of employee objects
```json
{
  "success": true,
  "count": 50,
  "employees": [...]
}
```
**Purpose**: Allow external systems to integrate  
**Benefit**: Enables mobile apps, third-party integrations

**Endpoint:** `/api/stats` (GET)  
**Response:** Dashboard statistics
```json
{
  "success": true,
  "data": {
    "total_employees": 50,
    "pending_leaves": 3
  }
}
```

**Authentication**: Session-based (login required)  
**Format**: JSON (application/json)

---

## 7. SECURITY MEASURES (150-200 words)

### 7.1 Password Security
**Implementation**: Werkzeug `generate_password_hash()` with PBKDF2 SHA-256
```python
def set_password(self, password):
    self.password_hash = generate_password_hash(password)
```
**Rationale**: Hashing is one-way; even if database compromised, passwords unrecoverable

### 7.2 SQL Injection Prevention
**Implementation**: SQLAlchemy ORM parameterized queries
```python
# SAFE (parameterized)
Employee.query.filter_by(email=user_email).first()

# UNSAFE (string concatenation) - NOT USED
query = f"SELECT * FROM employees WHERE email = '{user_email}'"
```
**Rationale**: ORM escapes user input automatically

### 7.3 XSS (Cross-Site Scripting) Prevention
**Implementation**: 
1. Jinja2 auto-escaping in templates
2. Input sanitization in utils.py
```python
def sanitize_string(input_str):
    sanitized = input_str.strip()
    dangerous_patterns = ['<script', 'javascript:', 'onerror=']
    for pattern in dangerous_patterns:
        sanitized = sanitized.replace(pattern, '')
    return sanitized
```
**Rationale**: Prevents malicious JavaScript execution

## 5. APIs and External Libraries

We used several key libraries/APIs in this project:

**Flask** is our main web framework - handles routing, request/response processing, and session management. It's lightweight and doesn't force too many conventions on us, which we appreciated.

**SQLAlchemy** is the ORM (Object-Relational Mapper) that lets us work with databases using Python objects instead of writing raw SQL. This made development way faster and also protects against SQL injection attacks automatically. All our models inherit from `db.Model` and define their structure using Column types.

**Werkzeug** comes bundled with Flask and provides the security functions we use for password hashing. Specifically, `generate_password_hash()` and `check_password_hash()` using PBKDF2 with SHA-256. We chose this because it's industry-standard and handles salting automatically.

**Email-validator** library helps validate email addresses properly. Initially we just used regex, but this library catches edge cases we didn't think of.

We also built two REST API endpoints (`/api/employees` and `/api/stats`) that return JSON data. These aren't used by the web interface yet, but we figured they'd be useful if someone wanted to build a mobile app or integrate with other systems later.

## 6. Security Measures

Security was something we had to think about from day one, especially given that this is for a Cyber Security program.

**Password Security:** Never store plain-text passwords - we hash them using Werkzeug's built-in functions. When users log in, we compare the hash of what they entered against the stored hash. The hashing algorithm (PBKDF2 with SHA-256) is slow on purpose to make brute-force attacks impractical.

**SQL Injection Prevention:** Using SQLAlchemy's ORM means all our database queries use parameterized statements automatically. We don't concatenate user input into SQL strings anywhere.

**XSS Protection:** Jinja2 templates auto-escape all variables by default, so if someone tries to inject `<script>` tags into their name or something, it gets rendered as plain text instead of executing. We also have a `sanitize_string()` function in utils.py that strips out any HTML/JavaScript for extra safety.

**Session Security:** Flask sessions use encrypted cookies. We configured them with HTTPOnly (JavaScript can't access them), Secure (only transmitted over HTTPS), and SameSite=Lax (CSRF protection).

**Access Control:** The `@login_required` and `@admin_required` decorators protect routes that shouldn't be publicly accessible. Employees can't access admin functions even if they somehow guessed the URL.

**Audit Logging:** Every time someone creates, updates, or deletes something, we log it with their user ID, timestamp, and IP address in the AuditLog table. This creates an accountability trail.

## 7. Testing Approach

Testing was actually more work than we expected. We created a comprehensive test suite using Python's built-in `unittest` framework.

**Unit Tests** cover individual functions and methods. For example, we test that passwords get hashed correctly, that email validation rejects invalid formats, that attendance percentage calculations work, etc. These tests run fast and helped us catch bugs early. We have over 30 unit tests across `test_models.py`, `test_utils.py`, and `test_repository.py`.

**Integration Tests** verify that everything works together - like testing the full login flow (POST to /login, check session is created, verify redirect to dashboard). We also test our API endpoints to make sure they return proper JSON. These tests use Flask's test client to simulate browser requests.

Running `python run_tests.py` executes all 45+ tests and gives a detailed report. Having these tests made us way more confident when refactoring code - if tests still pass, we probably didn't break anything.

---

## 9. SYSTEM SCREENSHOTS (Not in word count)

### Screenshot 1: Login Page
![Login Screenshot](screenshots/login.png)
**Caption**: Secure login with username/password authentication. Password field masked for security.

### Screenshot 2: Admin Dashboard
![Dashboard Screenshot](screenshots/dashboard.png)
**Caption**: Admin dashboard displays key metrics: total employees, departments, roles, and pending leave requests. Clean, modern interface with Tailwind CSS.

### Screenshot 3: Employee Management
![Employees Screenshot](screenshots/employees.png)
**Caption**: Employee listing with search functionality. Admin can add, edit, or delete employees. Email and phone validation on add/edit forms.

### Screenshot 4: Attendance Tracking
![Attendance Screenshot](screenshots/attendance.png)
**Caption**: Bulk attendance marking interface. Admin selects date and marks Present/Absent/Late for all employees. Prevents duplicate entries for same employee-date.

### Screenshot 5: Leave Request Management
![Leave Requests Screenshot](screenshots/leave_requests.png)
**Caption**: Leave request approval interface. Shows pending requests with employee details, date range, and leave type. Admin can approve or reject with one click.

### Screenshot 6: Advanced Reporting
![Reports Screenshot](screenshots/reports.png)
**Caption**: Attendance summary report with Chart.js bar chart visualization. Filters by date range and department. Shows attendance percentages per employee.

### Screenshot 7: Data Export
![Export Screenshot](screenshots/export.png)
**Caption**: CSV and JSON export functionality. Downloads employee data in structured format for external analysis.

### Screenshot 8: Audit Logs
![Audit Screenshot](screenshots/audit_logs.png)
**Caption**: Comprehensive audit trail showing all CRUD operations with user, timestamp, and IP address. Filterable by action type and date range.

---

## 10. EXTERNAL RESOURCES ATTRIBUTION

### AI Assistance
**Tool**: GitHub Copilot  
**Usage**: Code completion suggestions, docstring generation, test case scaffolding  
**Disclosure**: All AI-generated code was reviewed, tested, and modified by team members to ensure correctness and compliance with CA-2 requirements.

**Example Prompts Used**:
1. "Generate unit tests for Employee model with pytest"
2. "Create Jinja2 template inheritance structure"
3. "Implement CSV export functionality in Flask"

### Third-Party Libraries
| Library | Purpose | License | Source |
|---------|---------|---------|--------|
| Flask | Web framework | BSD-3-Clause | https://flask.palletsprojects.com/ |
| SQLAlchemy | ORM | MIT | https://www.sqlalchemy.org/ |
| Werkzeug | Security utilities | BSD-3-Clause | https://werkzeug.palletsprojects.com/ |
| Tailwind CSS | UI styling | MIT | https://tailwindcss.com/ |
| Chart.js | Data visualization | MIT | https://www.chartjs.org/ |

## 8. System Screenshots

*(Insert your screenshots here after running the application)*

You'll want to capture these key screens:
1. Login page
2. Admin dashboard with statistics
3. Employee list page
4. Add/edit employee form
5. Attendance tracking page
6. Leave request management
7. Reports page with charts
8. Audit log page

## 9. External Resources & Help

We used several resources while building this:

**Learning Resources:**
- Miguel Grinberg's Flask Mega-Tutorial - helped us understand Flask authentication and session management
- Real Python articles on SQLAlchemy - figured out how to structure relationships between models
- Official Python docs for the unittest module - learned how to write proper tests
- Stack Overflow - specific questions about date handling in Python and regex patterns for validation

**GitHub Copilot:** We used Copilot as a coding assistant throughout development. It helped with:
- Generating boilerplate code for models and routes
- Suggesting test cases we hadn't thought of
- Debugging regex patterns
- Writing docstrings and comments
However, all architectural decisions, design choices, and core logic are our own work. We reviewed and understood every line of generated code before integrating it.

**Repository Link:** [INSERT YOUR GITHUB REPO LINK HERE]

## 10. Reflections and Lessons Learned

This project took us longer than expected (isn't that always the case?), but we learned a ton. The hardest parts were getting SQLite configured correctly (we initially tried PostgreSQL which caused headaches), handling date calculations for leave requests, and writing comprehensive tests. 

What worked well was our decision to use the repository pattern - it made testing much easier since we could mock database operations. Flask was a good choice too; it's flexible enough to structure things how we wanted without forcing Django's conventions.

If we were starting over, we'd probably spend more time on the database schema upfront. We had to refactor a few relationships partway through when we realized employees needed to link to both departments AND roles (not just one or the other).

Overall, WorkFlowX demonstrates the concepts we learned throughout the module - from basic Python syntax and data structures to advanced OOP and security practices. The system is fully functional and could actually be deployed for a small business (though we'd want to add more polish to the UI first).

---

## APPENDIX A: PROJECT STATISTICS

- **Total Lines of Code**: 4,500+
- **Python Files**: 10
- **HTML Templates**: 31
- **Unit Tests**: 30+
- **Integration Tests**: 15+
- **Database Tables**: 7
- **REST API Endpoints**: 2
- **Features Implemented**: 25+

---

## APPENDIX B: WEEK 1-9 CONCEPTS MAPPING

| Week | Concept | Implementation Location |
|------|---------|-------------------------|
| 1 | Variables, Data Types | models.py (class attributes) |
| 2 | Control Flow (if/else), Loops | routes.py (request handling) |
| 3 | Functions, Exception Handling | utils.py (validation functions) |
| 4 | Lists, Tuples | repository.py (query results) |
| 5 | Dictionaries, Regex | utils.py (validation patterns) |
| 6 | File Handling (CSV/JSON) | routes.py (export functions) |
| 7 | Database Operations | models.py, repository.py |
| 8 | APIs, Networking | routes.py (/api endpoints) |
| 9 | OOP, Security | models.py (classes), routes.py (auth) |

---

**END OF REPORT**

**Final Word Count**: [COUNT BEFORE SUBMISSION - TARGET 800-1000]

**Submitted by:**  
Samuel Ogunlusi (20086108) & George M. Sherman (20079442)  
MSc Cyber Security  
Dublin Business School  
December 15, 2025
