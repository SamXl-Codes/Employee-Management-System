"""
WorkFlowX - Route Handlers (Controllers)

This module contains all Flask route handlers following MVC pattern.
This is the Controller layer that handles HTTP requests and responses.

Demonstrates:
- Flask routing and request handling
- Session management for authentication
- Form data validation
- CSV and JSON exports (Week 6: File handling)
- REST API endpoint (Week 8: Networking)
"""

from flask import render_template, request, redirect, url_for, session, flash, jsonify, make_response
from app import app, db
from models import User, Department, Role, Employee, Attendance, LeaveRequest, AuditLog
import repository as repo
import utils
from datetime import datetime, date
from functools import wraps
import csv
import json
import io


# ==================== EMAIL NOTIFICATIONS ====================

def send_email_notification(recipient_email, subject, leave_type, status, start_date=None, end_date=None):
    """
    Send email notification for leave request decisions.
    
    Week 7 Concept: String formatting
    Week 9 Concept: Security - Audit and notification logging
    """
    try:
        # Mock email sending (in production, use Flask-Mail)
        email_body = f"""
Dear Employee,

Your leave request has been {status.lower()}.

Leave Type: {leave_type}
Start Date: {start_date}
End Date: {end_date}

Status: {status}

Thank you,
HR Management System
"""
        # Log the email event for compliance
        app.logger.info(f"Email sent to {recipient_email}: Leave {status} notification")
        return True
    except Exception as e:
        app.logger.error(f"Failed to send email: {str(e)}")
        return False


def log_audit(action, entity_type, entity_id=None, description=None):
    """
    Log an audit event for tracking critical operations.
    
    Week 8 Concept: Functions for code reuse
    Week 9 Concept: Security and compliance through logging
    """
    try:
        log = AuditLog(
            user_id=session.get('user_id'),
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Error logging audit: {str(e)}")
        db.session.rollback()


# ==================== AUTHENTICATION DECORATORS ====================

def login_required(f):
    """
    Decorator to require login for protected routes.
    
    Week 3 Concept: Functions and decorators
    Week 9 Concept: Secure coding - authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin role for protected routes.
    
    Week 2 Concept: Control flow with if/else
    Week 9 Concept: Authorization
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login'))
        
        user = repo.get_user_by_id(session['user_id'])
        if not user or user.role != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    """Redirect to login or dashboard based on authentication."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    
    Week 2 Concept: if/elif/else for request method handling
    Week 9 Concept: Secure coding - password hashing
    """
    # If already logged in, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validate required fields (Week 5: validation)
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('login.html')
        
        # Retrieve user from database
        user = repo.get_user_by_username(username)
        
        # Verify credentials (Week 2: if/else logic)
        if user and user.check_password(password):
            # Set session variables (Week 9: session management)
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['role'] = user.role
            
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    username = session.get('username', 'User')
    
    # Clear session (Week 9: secure session management)
    session.clear()
    
    flash(f'Goodbye, {username}!', 'info')
    return redirect(url_for('login'))


# ==================== DASHBOARD ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """
    Display dashboard with statistics and recent activity.
    
    Week 5 Concept: Dictionaries to pass data to templates
    """
    # Get dashboard statistics
    stats = repo.get_dashboard_stats()
    
    # Get pending leave requests (for admin view)
    pending_leaves = []
    if session.get('role') == 'admin':
        pending_leaves = repo.get_all_leave_requests(status='Pending')[:5]  # Latest 5
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         pending_leaves=pending_leaves,
                         current_user=session.get('username'),
                         user_role=session.get('role'))


# ==================== EMPLOYEE ROUTES ====================

@app.route('/employees')
@login_required
def employees():
    """
    Display all employees with search capability.
    
    Week 2 Concept: for loops to iterate over results
    Week 5 Concept: Lists to store and display data
    """
    search_term = request.args.get('search', '').strip()
    
    # Search or get all employees (Week 2: if/else)
    if search_term:
        employee_list = repo.search_employees(search_term)
    else:
        employee_list = repo.get_all_employees(include_inactive=False)
    
    return render_template('employees.html', 
                         employees=employee_list,
                         search_term=search_term,
                         user_role=session.get('role'))


@app.route('/employees/add', methods=['GET', 'POST'])
@admin_required
def add_employee():
    """
    Add new employee with validation.
    
    Week 3 Concept: Exception handling
    Week 5 Concept: String methods and regex validation
    Week 9 Concept: Input validation for security
    """
    if request.method == 'POST':
        # Get form data (Week 5: dictionary operations)
        name = utils.sanitize_string(request.form.get('name', ''))
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        department_id = request.form.get('department_id')
        role_id = request.form.get('role_id')
        salary_str = request.form.get('salary', '')
        date_joined_str = request.form.get('date_joined', '')
        
        # Validate required fields
        is_valid, error_msg = utils.validate_required_fields(
            request.form,
            ['name', 'email', 'department_id', 'role_id', 'salary', 'date_joined']
        )
        
        if not is_valid:
            flash(error_msg, 'danger')
            return redirect(url_for('add_employee'))
        
        # Validate email format (Week 5: regex)
        if not utils.validate_email(email):
            flash('Invalid email format', 'danger')
            return redirect(url_for('add_employee'))
        
        # Validate phone (if provided)
        if phone and not utils.validate_phone(phone):
            flash('Invalid phone number format', 'danger')
            return redirect(url_for('add_employee'))
        
        # Validate and convert salary (Week 3: exception handling)
        is_valid, error_msg, salary = utils.validate_salary(salary_str)
        if not is_valid:
            flash(error_msg, 'danger')
            return redirect(url_for('add_employee'))
        
        # Parse date
        date_joined = utils.parse_date(date_joined_str)
        if not date_joined:
            flash('Invalid date format', 'danger')
            return redirect(url_for('add_employee'))
        
        # Create employee (Week 7: database operations)
        success, message, employee = repo.create_employee(
            name=name,
            email=email,
            phone=phone,
            department_id=int(department_id),
            role_id=int(role_id),
            salary=salary,
            date_joined=date_joined
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('employees'))
        else:
            flash(message, 'danger')
    
    # Get departments and roles for form dropdowns
    departments = repo.get_all_departments()
    roles = repo.get_all_roles()
    
    return render_template('add_employee.html', 
                         departments=departments, 
                         roles=roles)


@app.route('/employees/edit/<int:employee_id>', methods=['GET', 'POST'])
@admin_required
def edit_employee(employee_id):
    """Edit employee details."""
    employee = repo.get_employee_by_id(employee_id)
    
    if not employee:
        flash('Employee not found', 'danger')
        return redirect(url_for('employees'))
    
    if request.method == 'POST':
        # Get and validate form data (similar to add_employee)
        name = utils.sanitize_string(request.form.get('name', ''))
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        department_id = request.form.get('department_id')
        role_id = request.form.get('role_id')
        salary_str = request.form.get('salary', '')
        date_joined_str = request.form.get('date_joined', '')
        status = request.form.get('status', 'active')
        
        # Validate
        if not utils.validate_email(email):
            flash('Invalid email format', 'danger')
            return redirect(url_for('edit_employee', employee_id=employee_id))
        
        if phone and not utils.validate_phone(phone):
            flash('Invalid phone number format', 'danger')
            return redirect(url_for('edit_employee', employee_id=employee_id))
        
        is_valid, error_msg, salary = utils.validate_salary(salary_str)
        if not is_valid:
            flash(error_msg, 'danger')
            return redirect(url_for('edit_employee', employee_id=employee_id))
        
        date_joined = utils.parse_date(date_joined_str)
        if not date_joined:
            flash('Invalid date format', 'danger')
            return redirect(url_for('edit_employee', employee_id=employee_id))
        
        # Update employee
        success, message = repo.update_employee(
            employee_id,
            name=name,
            email=email,
            phone=phone,
            department_id=int(department_id),
            role_id=int(role_id),
            salary=salary,
            date_joined=date_joined,
            status=status
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('employees'))
        else:
            flash(message, 'danger')
    
    departments = repo.get_all_departments()
    roles = repo.get_all_roles()
    
    return render_template('edit_employee.html', 
                         employee=employee,
                         departments=departments,
                         roles=roles)


@app.route('/employees/delete/<int:employee_id>', methods=['POST'])
@admin_required
def delete_employee(employee_id):
    """
    Delete (deactivate) employee.
    
    Default: soft delete (mark as inactive)
    """
    soft_delete = request.form.get('soft_delete', 'true') == 'true'
    
    success, message = repo.delete_employee(employee_id, soft_delete=soft_delete)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('employees'))


# ==================== DEPARTMENT ROUTES ====================

@app.route('/departments')
@login_required
def departments():
    """Display all departments."""
    department_list = repo.get_all_departments()
    return render_template('departments.html', 
                         departments=department_list,
                         user_role=session.get('role'))


@app.route('/departments/add', methods=['POST'])
@admin_required
def add_department():
    """Add new department."""
    name = utils.sanitize_string(request.form.get('name', ''))
    description = utils.sanitize_string(request.form.get('description', ''))
    
    if not name:
        flash('Department name is required', 'danger')
        return redirect(url_for('departments'))
    
    success, message, _ = repo.create_department(name, description)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('departments'))


@app.route('/departments/edit/<int:department_id>', methods=['POST'])
@admin_required
def edit_department(department_id):
    """Edit department details."""
    name = utils.sanitize_string(request.form.get('name', ''))
    description = utils.sanitize_string(request.form.get('description', ''))
    
    if not name:
        flash('Department name is required', 'danger')
        return redirect(url_for('departments'))
    
    success, message = repo.update_department(department_id, name, description)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('departments'))


@app.route('/departments/delete/<int:department_id>', methods=['POST'])
@admin_required
def delete_department(department_id):
    """Delete department (only if no employees)."""
    success, message = repo.delete_department(department_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('departments'))


# ==================== ROLE ROUTES ====================

@app.route('/roles')
@login_required
def roles():
    """Display all roles."""
    role_list = repo.get_all_roles()
    return render_template('roles.html', 
                         roles=role_list,
                         user_role=session.get('role'))


@app.route('/roles/add', methods=['POST'])
@admin_required
def add_role():
    """Add new role."""
    title = utils.sanitize_string(request.form.get('title', ''))
    description = utils.sanitize_string(request.form.get('description', ''))
    
    if not title:
        flash('Role title is required', 'danger')
        return redirect(url_for('roles'))
    
    success, message, _ = repo.create_role(title, description)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('roles'))


@app.route('/roles/edit/<int:role_id>', methods=['POST'])
@admin_required
def edit_role(role_id):
    """Edit role details."""
    title = utils.sanitize_string(request.form.get('title', ''))
    description = utils.sanitize_string(request.form.get('description', ''))
    
    if not title:
        flash('Role title is required', 'danger')
        return redirect(url_for('roles'))
    
    success, message = repo.update_role(role_id, title, description)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('roles'))


@app.route('/roles/delete/<int:role_id>', methods=['POST'])
@admin_required
def delete_role(role_id):
    """Delete role (only if no employees)."""
    success, message = repo.delete_role(role_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('roles'))


# ==================== ATTENDANCE ROUTES ====================

@app.route('/attendance')
@login_required
def attendance():
    """
    Display attendance marking interface.
    
    Week 2 Concept: for loops to iterate over employees
    """
    # Get date from query params or use today
    date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    attendance_date = utils.parse_date(date_str)
    
    if not attendance_date:
        attendance_date = date.today()
    
    # Get all active employees
    employee_list = repo.get_all_employees()
    
    # Get existing attendance for this date
    attendance_records = repo.get_attendance_by_date(attendance_date)
    attendance_map = {record.employee_id: record for record in attendance_records}
    
    return render_template('attendance.html',
                         employees=employee_list,
                         attendance_map=attendance_map,
                         selected_date=attendance_date,
                         user_role=session.get('role'))


@app.route('/attendance/mark', methods=['POST'])
@admin_required
def mark_attendance():
    """
    Mark attendance for employees.
    
    Week 2 Concept: for loops to process form data
    Week 5 Concept: Dictionary and list operations
    """
    date_str = request.form.get('date')
    attendance_date = utils.parse_date(date_str)
    
    if not attendance_date:
        flash('Invalid date', 'danger')
        return redirect(url_for('attendance'))
    
    # Process attendance for each employee
    # Form data: employee_{id}_status = 'Present'/'Absent'/'Late'
    for key, value in request.form.items():
        if key.startswith('employee_') and key.endswith('_status'):
            employee_id = int(key.split('_')[1])
            status = value
            notes = request.form.get(f'employee_{employee_id}_notes', '')
            
            # Mark attendance
            repo.mark_attendance(employee_id, attendance_date, status, notes)
    
    flash('Attendance marked successfully', 'success')
    return redirect(url_for('attendance', date=date_str))


# ==================== LEAVE REQUEST ROUTES ====================

@app.route('/leave-requests')
@login_required
def leave_requests():
    """Display leave requests."""
    status_filter = request.args.get('status', None)
    
    # Admin sees all, employee sees only their own
    if session.get('role') == 'admin':
        leave_list = repo.get_all_leave_requests(status=status_filter)
    else:
        # Employee view - would need additional repo function
        leave_list = []
    
    return render_template('leave_requests.html',
                         leaves=leave_list,
                         status_filter=status_filter,
                         user_role=session.get('role'))


@app.route('/leave-requests/add', methods=['GET', 'POST'])
@login_required
def add_leave_request():
    """Submit new leave request."""
    if request.method == 'POST':
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        leave_type = request.form.get('leave_type')
        reason = utils.sanitize_string(request.form.get('reason', ''))
        
        # Parse dates
        start_date = utils.parse_date(start_date_str)
        end_date = utils.parse_date(end_date_str)
        
        if not start_date or not end_date:
            flash('Invalid date format', 'danger')
            return redirect(url_for('add_leave_request'))
        
        # Validate date range (Week 3: custom validation function)
        is_valid, error_msg = utils.validate_date_range(start_date, end_date)
        if not is_valid:
            flash(error_msg, 'danger')
            return redirect(url_for('add_leave_request'))
        
        # For demo, use first employee (in real app, would use logged-in employee)
        employee_id = 1  # This should be session['employee_id'] in production
        
        success, message, _ = repo.create_leave_request(
            employee_id, start_date, end_date, leave_type, reason
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('leave_requests'))
        else:
            flash(message, 'danger')
    
    return render_template('add_leave_request.html')


@app.route('/leave-requests/update/<int:leave_id>', methods=['POST'])
@admin_required
def update_leave_request(leave_id):
    """Approve or reject leave request."""
    action = request.form.get('action')
    
    if action == 'approve':
        success, message = repo.update_leave_status(leave_id, 'Approved')
    elif action == 'reject':
        success, message = repo.update_leave_status(leave_id, 'Rejected')
    else:
        flash('Invalid action', 'danger')
        return redirect(url_for('leave_requests'))
    
    if success:
        # Get leave request details for email notification
        leave = LeaveRequest.query.get(leave_id)
        if leave and leave.employee:
            send_email_notification(
                leave.employee.email,
                f'Leave Request {action.title()}',
                leave.leave_type,
                action.title(),
                leave.start_date.strftime('%Y-%m-%d') if leave.start_date else None,
                leave.end_date.strftime('%Y-%m-%d') if leave.end_date else None
            )
        
        log_audit('UPDATE', 'LeaveRequest', leave_id, f'Status changed to {action}')
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('leave_requests'))


# ==================== REPORTS & EXPORTS ====================

@app.route('/reports')
@login_required
def reports():
    """
    Display advanced reports page with filters.
    
    Week 5 Concept: Dictionary for complex data structures
    Week 2 Concept: if/else for conditional rendering
    """
    # Get filter parameters
    report_type = request.args.get('type', 'overview')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    department_id = request.args.get('department_id', '')
    
    # Parse dates
    start_date = utils.parse_date(start_date_str) if start_date_str else None
    end_date = utils.parse_date(end_date_str) if end_date_str else None
    
    # Initialize report data
    report_data = None
    
    if report_type == 'attendance_summary':
        # Attendance summary report
        report_data = generate_attendance_summary_report(start_date, end_date, department_id)
    elif report_type == 'leave_summary':
        # Leave summary report
        report_data = generate_leave_summary_report(start_date, end_date, department_id)
    elif report_type == 'payroll_summary':
        # Payroll summary report
        report_data = generate_payroll_summary_report(department_id)
    
    # Get departments for filter dropdown
    departments = repo.get_all_departments()
    
    # Generate chart data for visualizations
    chart_data = generate_chart_data(report_type, report_data)
    
    return render_template('reports.html', 
                         user_role=session.get('role'),
                         report_type=report_type,
                         report_data=report_data,
                         chart_data=chart_data,
                         departments=departments,
                         start_date=start_date,
                         end_date=end_date,
                         selected_department=department_id)


def generate_attendance_summary_report(start_date=None, end_date=None, department_id=None):
    """
    Generate attendance summary report with filters.
    
    Returns: dict with employee attendance data
    """
    # Get employees (filtered by department if provided)
    if department_id:
        employees = Employee.query.filter_by(department_id=int(department_id), status='active').all()
    else:
        employees = repo.get_all_employees()
    
    report = []
    
    for emp in employees:
        # Get attendance records
        query = Attendance.query.filter_by(employee_id=emp.employee_id)
        
        # Apply date filters
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        if end_date:
            query = query.filter(Attendance.date <= end_date)
        
        attendance_records = query.all()
        
        # Calculate statistics
        total_days = len(attendance_records)
        present_days = len([a for a in attendance_records if a.status == 'Present'])
        absent_days = len([a for a in attendance_records if a.status == 'Absent'])
        late_days = len([a for a in attendance_records if a.status == 'Late'])
        
        attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
        
        report.append({
            'employee': emp,
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'attendance_percentage': round(attendance_percentage, 2)
        })
    
    return report


def generate_leave_summary_report(start_date=None, end_date=None, department_id=None):
    """Generate leave summary report with filters."""
    # Get employees (filtered by department if provided)
    if department_id:
        employees = Employee.query.filter_by(department_id=int(department_id), status='active').all()
    else:
        employees = repo.get_all_employees()
    
    report = []
    
    for emp in employees:
        # Get leave requests
        query = LeaveRequest.query.filter_by(employee_id=emp.employee_id)
        
        # Apply date filters
        if start_date:
            query = query.filter(LeaveRequest.start_date >= start_date)
        if end_date:
            query = query.filter(LeaveRequest.end_date <= end_date)
        
        leave_requests = query.all()
        
        # Calculate statistics
        total_requests = len(leave_requests)
        approved_requests = len([l for l in leave_requests if l.status == 'Approved'])
        pending_requests = len([l for l in leave_requests if l.status == 'Pending'])
        rejected_requests = len([l for l in leave_requests if l.status == 'Rejected'])
        
        # Calculate total leave days (approved only)
        total_leave_days = sum([l.calculate_days() for l in leave_requests if l.status == 'Approved'])
        
        report.append({
            'employee': emp,
            'total_requests': total_requests,
            'approved_requests': approved_requests,
            'pending_requests': pending_requests,
            'rejected_requests': rejected_requests,
            'total_leave_days': total_leave_days
        })
    
    return report


def generate_payroll_summary_report(department_id=None):
    """Generate payroll summary report."""
    # Get employees (filtered by department if provided)
    if department_id:
        employees = Employee.query.filter_by(department_id=int(department_id), status='active').all()
    else:
        employees = repo.get_all_employees()
    
    report = []
    total_payroll = 0
    
    for emp in employees:
        if emp.salary:
            monthly_salary = float(emp.salary) / 12
            total_payroll += float(emp.salary)
            
            report.append({
                'employee': emp,
                'annual_salary': float(emp.salary),
                'monthly_salary': round(monthly_salary, 2)
            })
    
    return {
        'employees': report,
        'total_annual_payroll': total_payroll,
        'total_monthly_payroll': round(total_payroll / 12, 2)
    }


def generate_chart_data(report_type, report_data):
    """
    Generate chart data for visualizations.
    
    Week 5 Concept: List comprehension and dictionary construction for data transformation
    Week 3 Concept: Function modularity for chart data generation
    """
    if not report_data:
        return None
    
    import json
    
    if report_type == 'attendance_summary':
        # Attendance percentage chart
        labels = [row['employee'].name for row in report_data]
        percentages = [row['attendance_percentage'] for row in report_data]
        
        return {
            'attendance_chart': json.dumps({
                'type': 'bar',
                'labels': labels,
                'data': percentages,
                'colors': ['#3b82f6' if p >= 90 else '#f59e0b' if p >= 75 else '#ef4444' for p in percentages]
            })
        }
    
    elif report_type == 'leave_summary':
        # Leave status distribution chart
        total_approved = sum(row['approved_requests'] for row in report_data)
        total_pending = sum(row['pending_requests'] for row in report_data)
        total_rejected = sum(row['rejected_requests'] for row in report_data)
        
        return {
            'leave_chart': json.dumps({
                'type': 'doughnut',
                'labels': ['Approved', 'Pending', 'Rejected'],
                'data': [total_approved, total_pending, total_rejected],
                'colors': ['#10b981', '#f59e0b', '#ef4444']
            })
        }
    
    elif report_type == 'payroll_summary':
        # Salary distribution by department
        dept_salaries = {}
        for emp_data in report_data['employees']:
            dept = emp_data['employee'].department.name if emp_data['employee'].department else 'Unassigned'
            if dept not in dept_salaries:
                dept_salaries[dept] = 0
            dept_salaries[dept] += emp_data['annual_salary']
        
        return {
            'payroll_chart': json.dumps({
                'type': 'pie',
                'labels': list(dept_salaries.keys()),
                'data': list(dept_salaries.values()),
                'colors': ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
            })
        }
    
    return None


@app.route('/export/employees/csv')
@admin_required
def export_employees_csv():
    """
    Export employees to CSV file.
    
    Week 6 Concept: CSV file handling with csv.writer
    Week 6 Concept: Using 'with' context manager (although in-memory here)
    """
    # Get all employees
    employees = repo.get_all_employees(include_inactive=True)
    
    # Create CSV in memory (Week 6: File handling)
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header row
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Department', 'Role', 'Salary', 'Date Joined', 'Status'])
    
    # Write data rows (Week 2: for loop iteration)
    for emp in employees:
        writer.writerow([
            emp.employee_id,
            emp.name,
            emp.email,
            emp.phone or '',
            emp.department.name if emp.department else '',
            emp.role.title if emp.role else '',
            emp.salary or 0,
            emp.date_joined.strftime('%Y-%m-%d') if emp.date_joined else '',
            emp.status
        ])
    
    # Create response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=employees_{date.today()}.csv'
    
    return response


@app.route('/export/employees/json')
@admin_required
def export_employees_json():
    """
    Export employees to JSON file.
    
    Week 6 Concept: JSON file handling
    Week 5 Concept: Dictionary operations with to_dict()
    """
    # Get all employees
    employees = repo.get_all_employees(include_inactive=True)
    
    # Convert to dictionary list (Week 5: list comprehension, dictionaries)
    employee_data = [emp.to_dict() for emp in employees]
    
    # Create JSON response
    response = make_response(json.dumps(employee_data, indent=2))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = f'attachment; filename=employees_{date.today()}.json'
    
    return response


@app.route('/export/leave-summary/csv')
@admin_required
def export_leave_summary_csv():
    """Export leave summary report to CSV."""
    employees = repo.get_all_employees()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Employee ID', 'Name', 'Total Leave Days', 'Pending Requests', 'Approved Requests'])
    
    for emp in employees:
        pending = emp.leave_requests.filter_by(status='Pending').count()
        approved = emp.leave_requests.filter_by(status='Approved').count()
        
        writer.writerow([
            emp.employee_id,
            emp.name,
            emp.get_total_leave_days(),
            pending,
            approved
        ])
    
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=leave_summary_{date.today()}.csv'
    
    return response


# ==================== REST API ENDPOINT ====================

@app.route('/api/employees', methods=['GET'])
@login_required
def api_employees():
    """
    REST API endpoint to get employees as JSON.
    
    Week 8 Concept: Networking/REST API
    Returns JSON response instead of HTML
    """
    employees = repo.get_all_employees()
    
    # Convert to dictionary list (Week 5: list comprehension)
    employee_data = [emp.to_dict() for emp in employees]
    
    # Return JSON response (Week 8: REST API)
    return jsonify({
        'success': True,
        'count': len(employee_data),
        'employees': employee_data
    })


@app.route('/api/stats', methods=['GET'])
@login_required
def api_stats():
    """REST API endpoint for dashboard statistics."""
    stats = repo.get_dashboard_stats()
    
    return jsonify({
        'success': True,
        'data': stats
    })


# ==================== BULK IMPORT ====================

@app.route('/employees/import', methods=['GET', 'POST'])
@admin_required
def import_employees():
    """
    Bulk import employees from CSV file.
    
    Week 6 Concept: File handling with CSV parsing
    Week 3 Concept: Exception handling during import
    Week 5 Concept: Lists and dictionaries for batch processing
    """
    import_results = None
    
    if request.method == 'POST':
        # Check if file was uploaded
        if 'csv_file' not in request.files:
            flash('No file uploaded', 'danger')
            return redirect(url_for('import_employees'))
        
        file = request.files['csv_file']
        
        # Check if filename is empty
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('import_employees'))
        
        # Check file extension
        if not file.filename.endswith('.csv'):
            flash('File must be a CSV file', 'danger')
            return redirect(url_for('import_employees'))
        
        try:
            # Read CSV file (Week 6: File handling)
            import csv as csv_module
            from io import StringIO
            
            # Read file content
            file_content = file.read().decode('utf-8')
            csv_reader = csv_module.DictReader(StringIO(file_content))
            
            success_count = 0
            error_count = 0
            errors = []
            
            # Get all departments and roles for lookup
            departments = {dept.name.lower(): dept.department_id for dept in repo.get_all_departments()}
            roles = {role.title.lower(): role.role_id for role in repo.get_all_roles()}
            
            # Process each row (Week 2: for loop iteration)
            row_number = 1
            for row in csv_reader:
                row_number += 1
                
                try:
                    # Extract and validate data
                    name = utils.sanitize_string(row.get('name', ''))
                    email = row.get('email', '').strip().lower()
                    phone = row.get('phone', '').strip()
                    department_name = row.get('department', '').strip()
                    role_title = row.get('role', '').strip()
                    salary_str = row.get('salary', '')
                    date_joined_str = row.get('date_joined', '')
                    
                    # Validate required fields
                    if not name or not email or not department_name or not role_title or not salary_str or not date_joined_str:
                        errors.append({
                            'row': row_number,
                            'message': 'Missing required fields'
                        })
                        error_count += 1
                        continue
                    
                    # Validate email
                    if not utils.validate_email(email):
                        errors.append({
                            'row': row_number,
                            'message': f'Invalid email format: {email}'
                        })
                        error_count += 1
                        continue
                    
                    # Validate phone if provided
                    if phone and not utils.validate_phone(phone):
                        errors.append({
                            'row': row_number,
                            'message': f'Invalid phone format: {phone}'
                        })
                        error_count += 1
                        continue
                    
                    # Lookup department
                    department_id = departments.get(department_name.lower())
                    if not department_id:
                        errors.append({
                            'row': row_number,
                            'message': f'Department not found: {department_name}'
                        })
                        error_count += 1
                        continue
                    
                    # Lookup role
                    role_id = roles.get(role_title.lower())
                    if not role_id:
                        errors.append({
                            'row': row_number,
                            'message': f'Role not found: {role_title}'
                        })
                        error_count += 1
                        continue
                    
                    # Validate salary
                    is_valid, error_msg, salary = utils.validate_salary(salary_str)
                    if not is_valid:
                        errors.append({
                            'row': row_number,
                            'message': error_msg
                        })
                        error_count += 1
                        continue
                    
                    # Parse date
                    date_joined = utils.parse_date(date_joined_str)
                    if not date_joined:
                        errors.append({
                            'row': row_number,
                            'message': f'Invalid date format: {date_joined_str} (use YYYY-MM-DD)'
                        })
                        error_count += 1
                        continue
                    
                    # Create employee (Week 7: Database operations)
                    success, message, employee = repo.create_employee(
                        name=name,
                        email=email,
                        phone=phone,
                        department_id=department_id,
                        role_id=role_id,
                        salary=salary,
                        date_joined=date_joined
                    )
                    
                    if success:
                        success_count += 1
                    else:
                        errors.append({
                            'row': row_number,
                            'message': message
                        })
                        error_count += 1
                    
                except Exception as e:
                    errors.append({
                        'row': row_number,
                        'message': f'Error processing row: {str(e)}'
                    })
                    error_count += 1
            
            # Prepare results
            import_results = {
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors[:20]  # Limit to first 20 errors for display
            }
            
            if success_count > 0:
                flash(f'Successfully imported {success_count} employees!', 'success')
            
            if error_count > 0:
                flash(f'{error_count} errors encountered during import', 'warning')
        
        except Exception as e:
            flash(f'Error reading CSV file: {str(e)}', 'danger')
            return redirect(url_for('import_employees'))
    
    return render_template('import_employees.html', import_results=import_results)


@app.route('/employees/import/template')
@admin_required
def download_import_template():
    """
    Download CSV template for employee import.
    
    Week 6 Concept: CSV file generation
    """
    import csv as csv_module
    
    output = io.StringIO()
    writer = csv_module.writer(output)
    
    # Write header
    writer.writerow(['name', 'email', 'phone', 'department', 'role', 'salary', 'date_joined'])
    
    # Write example row
    writer.writerow([
        'John Doe',
        'john.doe@company.com',
        '555-1234',
        'Engineering',
        'Software Engineer',
        '75000',
        '2024-01-15'
    ])
    
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=employee_import_template.csv'
    
    return response


# ==================== AUDIT LOG VIEWER ====================

@app.route('/admin/audit-logs')
@admin_required
def audit_logs():
    """
    Admin page to view and filter audit logs.
    
    Week 5 Concept: Dictionary filtering and comprehensions
    Week 8 Concept: Database querying with filters
    """
    # Get filter parameters
    action_filter = request.args.get('action', '')
    entity_filter = request.args.get('entity_type', '')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    
    # Build query
    query = AuditLog.query
    
    if action_filter:
        query = query.filter_by(action=action_filter)
    if entity_filter:
        query = query.filter_by(entity_type=entity_filter)
    
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            query = query.filter(AuditLog.timestamp >= start_date)
        except:
            pass
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            query = query.filter(AuditLog.timestamp <= end_date)
        except:
            pass
    
    # Get logs ordered by most recent first, limit to 500
    logs = query.order_by(AuditLog.timestamp.desc()).limit(500).all()
    
    return render_template('audit_logs.html',
                         audit_logs=logs,
                         action_filter=action_filter,
                         entity_filter=entity_filter,
                         start_date=start_date_str,
                         end_date=end_date_str)


# ==================== ERROR HANDLERS ====================

# ==================== EMPLOYEE SELF-SERVICE PORTAL ====================

@app.route('/employee/dashboard')
@login_required
def employee_dashboard():
    """Employee personal dashboard with stats."""
    user = repo.get_user_by_id(session['user_id'])
    emp = Employee.query.filter_by(email=user.username + '@company.com').first()
    
    if not emp:
        emp = Employee.query.first()
    
    # Calculate attendance rate (last 30 days)
    from datetime import timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_attendance = Attendance.query.filter(
        Attendance.employee_id == emp.employee_id,
        Attendance.date >= thirty_days_ago
    ).all()
    
    present_count = len([a for a in recent_attendance if a.status == 'Present'])
    attendance_rate = round((present_count / len(recent_attendance) * 100), 1) if recent_attendance else 0
    
    # Get leave statistics
    pending_leaves = LeaveRequest.query.filter_by(
        employee_id=emp.employee_id,
        status='Pending'
    ).count()
    
    approved_leaves = LeaveRequest.query.filter_by(
        employee_id=emp.employee_id,
        status='Approved'
    ).count()
    
    recent_leaves = LeaveRequest.query.filter_by(
        employee_id=emp.employee_id
    ).order_by(LeaveRequest.submitted_at.desc()).all()
    
    return render_template('employee_dashboard.html',
                         current_user=emp,
                         attendance_rate=attendance_rate,
                         pending_leaves=pending_leaves,
                         approved_leaves=approved_leaves,
                         recent_leaves=recent_leaves)


@app.route('/employee/profile')
@login_required
def my_profile():
    """View employee's own profile."""
    user = repo.get_user_by_id(session['user_id'])
    emp = Employee.query.filter_by(email=user.username + '@company.com').first()
    
    if not emp:
        emp = Employee.query.first()
    
    return render_template('employee_profile.html', current_user=emp)


@app.route('/employee/leave-history')
@login_required
def my_leave_history():
    """View employee's leave request history."""
    user = repo.get_user_by_id(session['user_id'])
    emp = Employee.query.filter_by(email=user.username + '@company.com').first()
    
    if not emp:
        emp = Employee.query.first()
    
    leave_requests = LeaveRequest.query.filter_by(
        employee_id=emp.employee_id
    ).order_by(LeaveRequest.submitted_at.desc()).all()
    
    return render_template('employee_leave_history.html', leave_requests=leave_requests)


@app.route('/employee/attendance')
@login_required
def my_attendance():
    """View employee's attendance records."""
    user = repo.get_user_by_id(session['user_id'])
    emp = Employee.query.filter_by(email=user.username + '@company.com').first()
    
    if not emp:
        emp = Employee.query.first()
    
    attendance_records = Attendance.query.filter_by(
        employee_id=emp.employee_id
    ).order_by(Attendance.date.desc()).all()
    
    total_days = len(attendance_records)
    present_days = len([a for a in attendance_records if a.status == 'Present'])
    absent_days = len([a for a in attendance_records if a.status == 'Absent'])
    late_days = len([a for a in attendance_records if a.status == 'Late'])
    
    return render_template('employee_attendance.html',
                         attendance_records=attendance_records,
                         total_days=total_days,
                         present_days=present_days,
                         absent_days=absent_days,
                         late_days=late_days)


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    db.session.rollback()
    return render_template('500.html'), 500
