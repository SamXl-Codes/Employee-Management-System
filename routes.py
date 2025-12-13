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
from models import User, Department, Role, Employee, Attendance, LeaveRequest, AuditLog, Message
import repository as repo
import utils
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from functools import wraps
import csv
import json
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from werkzeug.utils import secure_filename
import os
import qrcode
import io
import base64
import secrets
import socket

# Global storage for QR tokens (in production, use Redis or database)
qr_tokens = {}

@app.context_processor
def inject_unread_messages():
    """
    Context processor to inject unread message count into all templates.
    Makes unread_messages_count available globally for badge notifications.
    """
    unread_count = 0
    if 'user_id' in session and session.get('role') == 'employee':
        try:
            from sqlalchemy import text
            user_id = session['user_id']
            
            # Use raw SQL to avoid column mapping issues
            query = text("""
                SELECT COUNT(*) 
                FROM messages 
                WHERE (recipient_id = :user_id OR is_broadcast = 1) 
                AND is_read = 0
            """)
            result = db.session.execute(query, {'user_id': user_id})
            unread_count = result.scalar()
        except Exception as e:
            app.logger.error(f"Error counting unread messages: {str(e)}")
            unread_count = 0
    return dict(unread_messages_count=unread_count)

def get_local_ip():
    """Automatically detect the local network IP address."""
    try:
        # Create a socket connection to determine the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to an external address (doesn't actually send data)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"  # Fallback to localhost if detection fails


def get_base_url():
    """Get the base URL for the application, handling both local and deployed environments."""
    # Check if we're in a deployed environment (Railway, Render, etc.)
    # These environments don't have pyodbc, so we use that as a marker
    try:
        import pyodbc
        # Local development - use local IP with port 8080
        return f"http://{get_local_ip()}:8080"
    except ImportError:
        # Deployed environment - use the request's host
        # Railway and other platforms handle HTTPS and domains
        from flask import request
        if request:
            # Use the request host which will be the Railway domain
            scheme = request.scheme  # http or https
            host = request.host  # includes port if non-standard
            return f"{scheme}://{host}"
        # Fallback (shouldn't happen in normal operation)
        return "http://localhost:8080"

def get_or_create_qr_token(date_str):
    """Get existing QR token for date or create new one. Auto-cleans old tokens."""
    # Clean up expired tokens (older than today)
    today = date.today().isoformat()
    expired_dates = [d for d in list(qr_tokens.keys()) if d < today]
    for expired_date in expired_dates:
        del qr_tokens[expired_date]
        print(f"[QR TOKEN] Auto-cleaned expired token for {expired_date}")
    
    # Return existing token or create new one
    if date_str not in qr_tokens:
        qr_tokens[date_str] = secrets.token_urlsafe(16)
        print(f"[QR TOKEN] Auto-generated new token for {date_str}")
    else:
        print(f"[QR TOKEN] Reusing existing token for {date_str}")
    
    return qr_tokens[date_str]


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


# ==================== FILE UPLOAD HELPERS ====================

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def save_profile_image(file, employee_name):
    """
    Save uploaded profile image with secure filename.
    Returns the filename if successful, None otherwise.
    """
    if file and allowed_file(file.filename):
        # Create secure filename based on employee name
        filename = secure_filename(f"{employee_name.lower().replace(' ', '-')}.{file.filename.rsplit('.', 1)[1].lower()}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(filepath)
            return filename
        except Exception as e:
            app.logger.error(f"Error saving profile image: {str(e)}")
            return None
    return None


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
    """Show landing page or redirect to dashboard if logged in."""
    # If user is logged in, go to dashboard
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return redirect(url_for('dashboard'))
        else:
            session.clear()
    
    # Show landing page
    return render_template('landing.html')


@app.route('/set_loading_shown')
def set_loading_shown():
    """Mark loading screen as shown."""
    session['loading_shown'] = True
    return '', 204


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    
    Week 2 Concept: if/elif/else for request method handling
    Week 9 Concept: Secure coding - password hashing
    """
    print("LOGIN ROUTE CALLED")  # DEBUG
    
    # Save pending check-in data before clearing session
    pending_token = session.get('pending_checkin_token')
    pending_date = session.get('pending_checkin_date')
    
    # Clear any existing session data before processing login
    if request.method == 'POST':
        session.clear()
        # Restore pending check-in data
        if pending_token and pending_date:
            session['pending_checkin_token'] = pending_token
            session['pending_checkin_date'] = pending_date
    
    # If already logged in (GET request), redirect to dashboard
    if 'user_id' in session and request.method == 'GET':
        # Check if there's a pending check-in
        if pending_token and pending_date:
            return redirect(url_for('employee_qr_checkin', token=pending_token, date=pending_date))
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
            
            # Check if user was trying to check in via QR code
            if 'pending_checkin_token' in session and 'pending_checkin_date' in session:
                token = session['pending_checkin_token']
                checkin_date = session['pending_checkin_date']
                # Redirect back to check-in page
                return redirect(url_for('employee_qr_checkin', token=token, date=checkin_date))
            
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    username = session.get('username', 'User')
    
    # Clear session completely (Week 9: secure session management)
    session.clear()
    
    # Create response with cache control headers to prevent back button issues
    response = make_response(redirect(url_for('login')))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    flash(f'Goodbye, {username}!', 'info')
    return response


# ==================== DASHBOARD ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """
    Display dashboard with statistics and recent activity.
    Redirect employees to their personalized dashboard.
    
    Week 5 Concept: Dictionaries to pass data to templates
    Week 2 Concept: if/else for role-based routing
    """
    # Redirect employees to their personalized dashboard
    if session.get('role') == 'employee':
        return redirect(url_for('employee_dashboard'))
    
    # Admin dashboard - Get dashboard statistics
    stats = repo.get_dashboard_stats()
    
    # Get pending leave requests (for admin view)
    pending_leaves = repo.get_all_leave_requests(status='Pending')[:5]  # Latest 5
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         pending_leaves=pending_leaves,
                         current_user=session.get('username'),
                         user_role=session.get('role'))


# ==================== EMPLOYEE ROUTES ====================

@app.route('/employees')
@login_required
@admin_required
def employees():
    """
    Display all employees with search capability.
    ADMIN ONLY - Employees cannot view other employees' data.
    
    Week 2 Concept: for loops to iterate over results
    Week 5 Concept: Lists to store and display data
    """
    search_term = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'active')  # 'active', 'inactive', or 'all'
    
    # Search or get all employees (Week 2: if/else)
    if search_term:
        employee_list = repo.search_employees(search_term)
        # Apply status filter to search results
        if status_filter == 'active':
            employee_list = [emp for emp in employee_list if emp.status.lower() == 'active']
        elif status_filter == 'inactive':
            employee_list = [emp for emp in employee_list if emp.status.lower() == 'inactive']
    else:
        if status_filter == 'inactive':
            employee_list = Employee.query.filter_by(status='inactive').order_by(Employee.name).all()
        elif status_filter == 'all':
            employee_list = repo.get_all_employees(include_inactive=True)
        else:
            employee_list = repo.get_all_employees(include_inactive=False)
    
    return render_template('employees.html', 
                         employees=employee_list,
                         search_term=search_term,
                         status_filter=status_filter,
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
        
        # Handle profile image upload
        profile_image = 'default-avatar.svg'  # Default
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '':
                saved_filename = save_profile_image(file, name)
                if saved_filename:
                    profile_image = saved_filename
                else:
                    flash('Warning: Profile image could not be uploaded. Using default.', 'warning')
        
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
        
        # Update profile image if employee was created
        if success and employee:
            employee.profile_image = profile_image
            db.session.commit()
        
        if success and employee:
            # Automatically create user account for the new employee
            try:
                default_password = 'WorkFlow@2025'
                existing_user = User.query.filter_by(username=email).first()
                
                if not existing_user:
                    new_user = User(
                        username=email,
                        password=default_password,
                        role='employee'
                    )
                    db.session.add(new_user)
                    db.session.commit()
                    flash(f'{message} ✅ Login account created! Username: {email}, Default Password: {default_password}', 'success')
                    print(f"✅ Created User account for: {email} with default password: {default_password}")  # Debug log
                else:
                    flash(f'{message} (Login account already exists)', 'success')
                    print(f"⚠️ User account already exists for: {email}")  # Debug log
            except Exception as e:
                print(f"❌ Error creating user account: {str(e)}")  # Debug log
                db.session.rollback()
                flash(f'{message} ⚠️ Warning: Could not create login account. Contact IT Support.', 'warning')
            
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


@app.route('/employees/reactivate/<int:employee_id>', methods=['POST'])
@admin_required
def reactivate_employee(employee_id):
    """Reactivate a deactivated employee."""
    success, message = repo.reactivate_employee(employee_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('employees'))


# ==================== DEPARTMENT ROUTES ====================

@app.route('/departments')
@login_required
def departments():
    """Display all departments and roles."""
    department_list = repo.get_all_departments()
    role_list = repo.get_all_roles()
    return render_template('departments.html', 
                         departments=department_list,
                         roles=role_list,
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
    """Redirect to departments page (roles are now integrated there)."""
    return redirect(url_for('departments'))


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
    Display attendance marking interface with search and filter.
    
    Week 2 Concept: for loops to iterate over employees
    """
    # Get date from query params or use today
    date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    attendance_date = utils.parse_date(date_str)
    
    if not attendance_date:
        attendance_date = date.today()
    
    # Get search query
    search_query = request.args.get('search', '').strip()
    
    # Get all active employees
    employee_list = repo.get_all_employees()
    
    # Filter employees by search query if provided
    if search_query:
        # Try to parse employee ID (supports "WFX-0001", "0001", or "1")
        employee_id_num = None
        if search_query.upper().startswith('WFX-'):
            try:
                employee_id_num = int(search_query.upper().replace('WFX-', ''))
            except ValueError:
                pass
        else:
            try:
                employee_id_num = int(search_query)
            except ValueError:
                pass
        
        employee_list = [emp for emp in employee_list 
                        if search_query.lower() in emp.name.lower() or 
                           search_query.lower() in emp.email.lower() or
                           (employee_id_num is not None and emp.employee_id == employee_id_num)]
    
    # Get existing attendance for this date
    attendance_records = repo.get_attendance_by_date(attendance_date)
    attendance_map = {record.employee_id: record for record in attendance_records}
    
    # Sort employees: those with attendance today (newest check-in first) appear at top
    def sort_key(emp):
        if emp.employee_id in attendance_map:
            record = attendance_map[emp.employee_id]
            # If checked in today, sort by check_in_time (newest first = negative timestamp)
            if record.check_in_time:
                return (0, -record.check_in_time.timestamp())
            # If marked but not checked in, put after checked-in employees
            return (1, emp.name.lower())
        # Employees without attendance go last, sorted by name
        return (2, emp.name.lower())
    
    employee_list.sort(key=sort_key)
    
    return render_template('attendance.html',
                         employees=employee_list,
                         attendance_map=attendance_map,
                         selected_date=attendance_date,
                         search_query=search_query,
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
        
        # Get the logged-in user's employee record
        user = repo.get_user_by_id(session['user_id'])
        emp = Employee.query.filter_by(email=user.username).first()
        
        if not emp:
            flash('Employee profile not found. Please contact HR.', 'danger')
            return redirect(url_for('employee_dashboard'))
        
        employee_id = emp.employee_id
        
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
    """Approve or reject leave request with optional HR notes."""
    action = request.form.get('action')
    hr_notes = request.form.get('hr_notes', '').strip()
    
    if action == 'approve':
        success, message = repo.update_leave_status(leave_id, 'Approved', hr_notes=hr_notes)
    elif action == 'reject':
        success, message = repo.update_leave_status(leave_id, 'Rejected', hr_notes=hr_notes)
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


@app.route('/leave-requests/view/<int:leave_id>')
@admin_required
def view_leave_request(leave_id):
    """View detailed leave request with HR notes and history."""
    leave = LeaveRequest.query.get_or_404(leave_id)
    user = repo.get_user_by_id(session['user_id'])
    
    log_audit('VIEW', 'LeaveRequest', leave_id, 'Viewed leave request details')
    return render_template('leave_request_detail.html', user=user, leave=leave)


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


@app.route('/admin/settings')
@login_required
def admin_settings():
    """Admin settings page - REAL administrative control center with actual power."""
    if session.get('role') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    user = repo.get_user_by_id(session['user_id'])
    
    # Get real-time statistics for admin dashboard
    stats = {
        'total_employees': Employee.query.filter_by(status='active').count(),
        'active_today': Attendance.query.filter_by(date=date.today()).count(),
        'pending_leaves': LeaveRequest.query.filter_by(status='Pending').count(),
        'total_departments': Department.query.count()
    }
    
    return render_template('admin_settings_v6.html', user=user, stats=stats)


@app.route('/admin/run-migration', methods=['POST'])
@admin_required
def run_migration():
    """Run database migration to add draft and delete columns."""
    from sqlalchemy import inspect, text
    
    try:
        # Check current columns
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('messages')]
        has_draft = 'is_draft' in columns
        has_deleted = 'deleted_at' in columns
        
        if has_draft and has_deleted:
            flash('Migration already completed! Draft and delete features are enabled.', 'info')
            return redirect(url_for('admin_messages'))
        
        # Run migration
        app.logger.info("Starting database migration for draft and delete columns...")
        
        if not has_draft:
            app.logger.info("Adding is_draft column...")
            # SQLite uses INTEGER for boolean
            db.session.execute(text("ALTER TABLE messages ADD COLUMN is_draft INTEGER DEFAULT 0"))
            app.logger.info("✓ Added is_draft column")
        
        if not has_deleted:
            app.logger.info("Adding deleted_at column...")
            db.session.execute(text("ALTER TABLE messages ADD COLUMN deleted_at TEXT"))
            app.logger.info("✓ Added deleted_at column")
        
        db.session.commit()
        
        log_audit('UPDATE', 'Database', None, 'Migration completed: Added draft and delete columns')
        flash('✅ Migration completed successfully! Draft and delete features are now enabled.', 'success')
        app.logger.info("Migration completed successfully!")
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Migration failed: {str(e)}")
        flash(f'❌ Migration failed: {str(e)}', 'danger')
    
    return redirect(url_for('admin_messages'))


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


@app.route('/export/employees/pdf')
@admin_required
def export_employees_pdf():
    """Export employees to PDF with formatted table."""
    employees = repo.get_all_employees(include_inactive=True)
    
    # Create PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    
    # Container for PDF elements
    elements = []
    
    # Add title
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=30,
        alignment=1  # Center
    )
    title = Paragraph(f"Employee Report - {date.today().strftime('%B %d, %Y')}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2 * inch))
    
    # Prepare table data
    data = [['ID', 'Name', 'Email', 'Department', 'Role', 'Salary', 'Status']]
    
    for emp in employees:
        data.append([
            str(emp.employee_id),
            emp.name,
            emp.email,
            emp.department.name if emp.department else 'N/A',
            emp.role.title if emp.role else 'N/A',
            f"${emp.salary:,.2f}" if emp.salary else '$0.00',
            emp.status
        ])
    
    # Create table
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#374151')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    
    elements.append(table)
    
    # Add footer
    elements.append(Spacer(1, 0.3 * inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1
    )
    footer = Paragraph("© 2025 WorkFlowX. All rights reserved.", footer_style)
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF from buffer
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=employees_{date.today()}.pdf'
    
    return response


@app.route('/export/attendance-summary/pdf')
@admin_required
def export_attendance_summary_pdf():
    """Export attendance summary report to PDF."""
    # Get filtered data
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    department_id = request.args.get('department_id')
    
    start_date = utils.parse_date(start_date_str) if start_date_str else None
    end_date = utils.parse_date(end_date_str) if end_date_str else None
    
    employees = repo.get_all_employees()
    if department_id:
        employees = [e for e in employees if e.department_id == int(department_id)]
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    
    # Title
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=20, 
                                 textColor=colors.HexColor('#1f2937'), spaceAfter=20, alignment=1)
    title = Paragraph(f"Attendance Summary Report - {date.today().strftime('%B %d, %Y')}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2 * inch))
    
    # Table data
    data = [['Employee', 'Department', 'Total Days', 'Present', 'Absent', 'Late', 'Attendance %']]
    
    for emp in employees:
        attendance_records = emp.attendance_records
        if start_date and end_date:
            attendance_records = [a for a in attendance_records if start_date <= a.date <= end_date]
        
        total_days = len(attendance_records)
        present = len([a for a in attendance_records if a.status == 'Present'])
        absent = len([a for a in attendance_records if a.status == 'Absent'])
        late = len([a for a in attendance_records if a.status == 'Late'])
        percentage = (present / total_days * 100) if total_days > 0 else 0
        
        data.append([
            emp.name,
            emp.department.name if emp.department else 'N/A',
            str(total_days),
            str(present),
            str(absent),
            str(late),
            f"{percentage:.1f}%"
        ])
    
    # Create table
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#374151')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))
    footer = Paragraph("© 2025 WorkFlowX. All rights reserved.", 
                      ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1))
    elements.append(footer)
    
    doc.build(elements)
    buffer.seek(0)
    
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=attendance_summary_{date.today()}.pdf'
    
    return response


@app.route('/export/leave-summary/pdf')
@admin_required
def export_leave_summary_pdf():
    """Export leave summary report to PDF."""
    # Get filtered data
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    department_id = request.args.get('department_id')
    
    start_date = utils.parse_date(start_date_str) if start_date_str else None
    end_date = utils.parse_date(end_date_str) if end_date_str else None
    
    employees = repo.get_all_employees()
    if department_id:
        employees = [e for e in employees if e.department_id == int(department_id)]
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    
    # Title
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=20, 
                                 textColor=colors.HexColor('#1f2937'), spaceAfter=20, alignment=1)
    title = Paragraph(f"Leave Summary Report - {date.today().strftime('%B %d, %Y')}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2 * inch))
    
    # Table data
    data = [['Employee', 'Department', 'Total Requests', 'Approved', 'Pending', 'Rejected', 'Total Days']]
    
    for emp in employees:
        leave_requests = emp.leave_requests.all()
        if start_date and end_date:
            leave_requests = [lr for lr in leave_requests if start_date <= lr.start_date <= end_date]
        
        total_requests = len(leave_requests)
        approved = len([lr for lr in leave_requests if lr.status == 'Approved'])
        pending = len([lr for lr in leave_requests if lr.status == 'Pending'])
        rejected = len([lr for lr in leave_requests if lr.status == 'Rejected'])
        total_days = sum([lr.calculate_days() for lr in leave_requests])
        
        data.append([
            emp.name,
            emp.department.name if emp.department else 'N/A',
            str(total_requests),
            str(approved),
            str(pending),
            str(rejected),
            str(total_days)
        ])
    
    # Create table
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#374151')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))
    footer = Paragraph("© 2025 WorkFlowX. All rights reserved.", 
                      ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1))
    elements.append(footer)
    
    doc.build(elements)
    buffer.seek(0)
    
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=leave_summary_{date.today()}.pdf'
    
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
    """
    Employee personal dashboard with personalized stats.
    Shows only information relevant to the logged-in employee.
    """
    try:
        user = repo.get_user_by_id(session['user_id'])
        
        # Try to find employee by email matching username
        emp = Employee.query.filter_by(email=user.username).first()
        
        # If not found, try with @company.com or @workflowx.com
        if not emp:
            emp = Employee.query.filter(
                (Employee.email == user.username + '@company.com') |
                (Employee.email == user.username + '@workflowx.com') |
                (Employee.email.like(f'%{user.username}%'))
            ).first()
        
        # If still not found, show error message
        if not emp:
            flash('Your employee profile is not linked to this account. Please contact HR.', 'danger')
            return redirect(url_for('logout'))
        
        # Calculate attendance rate (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        today = datetime.utcnow().date()
        
        recent_attendance = Attendance.query.filter(
            Attendance.employee_id == emp.employee_id,
            Attendance.date >= thirty_days_ago
        ).all()
        
        present_count = len([a for a in recent_attendance if a.status == 'Present'])
        late_count = len([a for a in recent_attendance if a.status == 'Late'])
        absent_count = len([a for a in recent_attendance if a.status == 'Absent'])
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
        
        rejected_leaves = LeaveRequest.query.filter_by(
            employee_id=emp.employee_id,
            status='Rejected'
        ).count()
        
        # Get recent leave requests (last 5)
        recent_leaves = LeaveRequest.query.filter_by(
            employee_id=emp.employee_id
        ).order_by(LeaveRequest.submitted_at.desc()).limit(5).all()
        
        # Calculate days since joining
        days_employed = (today - emp.date_joined).days if emp.date_joined else 0
        years_employed = round(days_employed / 365.25, 1)
    
        # Get today's attendance status
        today_attendance = Attendance.query.filter_by(
            employee_id=emp.employee_id,
            date=today
        ).first()
        
        return render_template('employee_dashboard.html',
                             current_user=emp,
                             attendance_rate=attendance_rate,
                             present_count=present_count,
                             late_count=late_count,
                             absent_count=absent_count,
                             pending_leaves=pending_leaves,
                             approved_leaves=approved_leaves,
                             rejected_leaves=rejected_leaves,
                             recent_leaves=recent_leaves,
                             years_employed=years_employed,
                             today_attendance=today_attendance,
                             user_role=session.get('role'))
    
    except Exception as e:
        app.logger.error(f"Error in employee_dashboard: {str(e)}")
        flash('An error occurred loading your dashboard. Please try again.', 'danger')
        return redirect(url_for('login'))


@app.route('/employee/profile')
@login_required
def employee_profile():
    """View employee's own profile."""
    user = repo.get_user_by_id(session['user_id'])
    
    # Try to find employee by exact email match
    emp = Employee.query.filter_by(email=user.username).first()
    
    # If not found, try with @company.com or @workflowx.com
    if not emp:
        emp = Employee.query.filter(
            (Employee.email == user.username + '@company.com') |
            (Employee.email == user.username + '@workflowx.com')
        ).first()
    
    # If still not found, show error
    if not emp:
        flash('Your employee profile is not linked to this account. Please contact HR.', 'danger')
        return redirect(url_for('logout'))
    
    return render_template('employee_profile.html', current_user=emp)


@app.route('/employee/salary')
@login_required
def my_salary():
    """View employee's own salary and payslips."""
    try:
        from models import Payroll
        user = repo.get_user_by_id(session['user_id'])
        
        # Try to find employee by exact email match
        emp = Employee.query.filter_by(email=user.username).first()
        
        # If not found, try with @company.com or @workflowx.com
        if not emp:
            emp = Employee.query.filter(
                (Employee.email == user.username + '@company.com') |
                (Employee.email == user.username + '@workflowx.com')
            ).first()
        
        # If still not found, show error
        if not emp:
            flash('Your employee profile is not linked to this account. Please contact HR.', 'danger')
            return redirect(url_for('logout'))
        
        # Get all payroll records for this employee
        payrolls = Payroll.query.filter_by(employee_id=emp.employee_id)\
            .order_by(Payroll.pay_period_end.desc()).all()
        
        # Get latest payroll for detailed breakdown
        latest_payroll = payrolls[0] if payrolls else None
        
        # Calculate salary breakdown (assuming monthly salary)
        salary_breakdown = None
        if latest_payroll:
            from decimal import Decimal
            gross = float(latest_payroll.gross_salary)
            # Calculate components as percentages of gross salary
            basic_salary = gross * 0.65  # 65% basic
            housing_allowance = gross * 0.15  # 15% housing
            transport_allowance = gross * 0.10  # 10% transport
            meal_allowance = gross * 0.10  # 10% meal
            
            # Deductions breakdown
            total_ded = float(latest_payroll.total_deductions)
            pension = total_ded * 0.50  # 50% pension (8% of gross)
            tax = total_ded * 0.35  # 35% tax
            nhis = total_ded * 0.10  # 10% health insurance
            other_ded = total_ded * 0.05  # 5% other
            
            # Annual calculations
            annual_gross = gross * 12
            annual_net = float(latest_payroll.net_salary) * 12
            annual_deductions = total_ded * 12
            
            salary_breakdown = {
                'basic_salary': basic_salary,
                'housing_allowance': housing_allowance,
                'transport_allowance': transport_allowance,
                'meal_allowance': meal_allowance,
                'pension': pension,
                'tax': tax,
                'nhis': nhis,
                'other_deductions': other_ded,
                'annual_gross': annual_gross,
                'annual_net': annual_net,
                'annual_deductions': annual_deductions
            }
        
        log_audit('VIEW', 'Salary', emp.employee_id, f'Employee viewed salary')
        return render_template('my_salary.html', 
                             current_user=emp,
                             payrolls=payrolls,
                             latest_payroll=latest_payroll,
                             salary_breakdown=salary_breakdown)
    except Exception as e:
        flash(f'Error loading salary information: {str(e)}', 'danger')
        return redirect(url_for('employee_dashboard'))


@app.route('/employee/payslip/<int:payroll_id>/download')
@login_required
def download_payslip(payroll_id):
    """Download payslip as PDF."""
    try:
        from models import Payroll
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        import io
        
        user = repo.get_user_by_id(session['user_id'])
        emp = Employee.query.filter_by(email=user.username).first()
        
        if not emp:
            flash('Employee profile not found', 'danger')
            return redirect(url_for('my_salary'))
        
        payroll = Payroll.query.get_or_404(payroll_id)
        
        # Verify this payroll belongs to the logged-in employee
        if payroll.employee_id != emp.employee_id:
            flash('Unauthorized access', 'danger')
            return redirect(url_for('my_salary'))
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"<b>PAYSLIP</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Company and Employee Info
        info_data = [
            ['WorkFlowX', ''],
            ['', ''],
            ['Employee Name:', emp.name],
            ['Employee ID:', f'WFX-{emp.employee_id:04d}'],
            ['Department:', emp.department.name if emp.department else 'N/A'],
            ['Pay Period:', f'{payroll.pay_period_start.strftime("%b %d, %Y")} - {payroll.pay_period_end.strftime("%b %d, %Y")}'],
        ]
        
        info_table = Table(info_data, colWidths=[200, 300])
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('FONT', (0, 0), (0, 0), 'Helvetica-Bold', 16),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 20))
        
        # Earnings and Deductions
        payment_data = [
            ['Description', 'Amount'],
            ['Gross Salary', f'₦{payroll.gross_salary:,.2f}'],
            ['', ''],
            ['Deductions', ''],
            ['Total Deductions', f'₦{payroll.total_deductions:,.2f}'],
            ['', ''],
            ['Net Salary', f'₦{payroll.net_salary:,.2f}'],
        ]
        
        payment_table = Table(payment_data, colWidths=[300, 200])
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(payment_table)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        log_audit('DOWNLOAD', 'Payslip', payroll_id, f'Employee downloaded payslip')
        
        return make_response(
            buffer.getvalue(),
            200,
            {
                'Content-Type': 'application/pdf',
                'Content-Disposition': f'attachment; filename=payslip_{emp.name}_{payroll.pay_period_end.strftime("%b_%Y")}.pdf'
            }
        )
    except Exception as e:
        flash(f'Error generating payslip: {str(e)}', 'danger')
        return redirect(url_for('my_salary'))


@app.route('/employee/profile/update', methods=['GET', 'POST'])
@login_required
def update_my_profile():
    """Allow employees to update their own profile information."""
    user = repo.get_user_by_id(session['user_id'])
    
    # Try to find employee by exact email match
    emp = Employee.query.filter_by(email=user.username).first()
    
    # If not found, try with @company.com or @workflowx.com
    if not emp:
        emp = Employee.query.filter(
            (Employee.email == user.username + '@company.com') |
            (Employee.email == user.username + '@workflowx.com')
        ).first()
    
    if not emp:
        flash('Your employee profile is not linked to this account. Please contact HR.', 'danger')
        return redirect(url_for('logout'))
    
    if request.method == 'POST':
        try:
            # Update phone number
            phone = request.form.get('phone', '').strip()
            if phone:
                emp.phone = phone
            
            # Handle profile picture upload
            if 'profile_image' in request.files:
                file = request.files['profile_image']
                if file and file.filename and allowed_file(file.filename):
                    # Save the file
                    filename = save_profile_image(file, emp.first_name + ' ' + emp.last_name)
                    if filename:
                        emp.profile_image = filename
            
            # Handle password change
            current_password = request.form.get('current_password', '').strip()
            new_password = request.form.get('new_password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            if new_password or current_password:
                # Validate current password
                if not current_password:
                    flash('Please enter your current password to change it', 'danger')
                    return redirect(url_for('update_my_profile'))
                
                if not user.check_password(current_password):
                    flash('Current password is incorrect', 'danger')
                    return redirect(url_for('update_my_profile'))
                
                # Validate new password
                if not new_password:
                    flash('Please enter a new password', 'danger')
                    return redirect(url_for('update_my_profile'))
                
                if len(new_password) < 6:
                    flash('New password must be at least 6 characters', 'danger')
                    return redirect(url_for('update_my_profile'))
                
                if new_password != confirm_password:
                    flash('New passwords do not match', 'danger')
                    return redirect(url_for('update_my_profile'))
                
                # Update password
                user.set_password(new_password)
                db.session.add(user)
                
                # Log password change
                log_audit('UPDATE', 'User', user.user_id, 'Password changed by employee')
            
            # Save changes
            db.session.add(emp)
            db.session.commit()
            
            # Log the update
            log_audit('UPDATE', 'Employee', emp.employee_id, 'Profile updated by employee')
            
            flash('Your profile has been updated successfully!', 'success')
            return redirect(url_for('employee_profile'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating employee profile: {str(e)}")
            flash('An error occurred while updating your profile. Please try again.', 'danger')
    
    return render_template('update_my_profile.html', current_user=emp)


@app.route('/employee/leave-history')
@login_required
def my_leave_history():
    """View employee's leave request history."""
    user = repo.get_user_by_id(session['user_id'])
    
    # Try to find employee by exact email match
    emp = Employee.query.filter_by(email=user.username).first()
    
    # If not found, try with @company.com or @workflowx.com
    if not emp:
        emp = Employee.query.filter(
            (Employee.email == user.username + '@company.com') |
            (Employee.email == user.username + '@workflowx.com')
        ).first()
    
    # If still not found, show error
    if not emp:
        flash('Your employee profile is not linked to this account. Please contact HR.', 'danger')
        return redirect(url_for('logout'))
    
    leave_requests = LeaveRequest.query.filter_by(
        employee_id=emp.employee_id
    ).order_by(LeaveRequest.submitted_at.desc()).all()
    
    return render_template('employee_leave_history.html', leave_requests=leave_requests, current_user=emp)


@app.route('/employee/settings')
@login_required
def employee_settings():
    """Employee settings page - appearance, notifications, profile preferences."""
    if session.get('role') != 'employee':
        flash('Access denied', 'danger')
        return redirect(url_for('employee_dashboard'))
    
    user = repo.get_user_by_id(session['user_id'])
    emp = Employee.query.filter_by(email=user.username).first()
    
    if not emp:
        emp = Employee.query.filter_by(email=user.username + '@company.com').first()
    
    if not emp:
        flash('Employee profile not found', 'danger')
        return redirect(url_for('logout'))
    
    return render_template('employee_settings.html', user=user, employee=emp)


@app.route('/employee/upload-photo', methods=['POST'])
@login_required
def upload_employee_photo():
    """Allow employee to upload their own profile photo."""
    user = repo.get_user_by_id(session['user_id'])
    emp = Employee.query.filter_by(email=user.username).first()
    
    if not emp:
        emp = Employee.query.filter_by(email=user.username + '@company.com').first()
    
    if not emp:
        flash('Employee profile not found', 'danger')
        return redirect(url_for('employee_dashboard'))
    
    if 'profile_image' not in request.files:
        flash('No file selected', 'danger')
        return redirect(request.referrer or url_for('employee_dashboard'))
    
    file = request.files['profile_image']
    
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(request.referrer or url_for('employee_dashboard'))
    
    if file and allowed_file(file.filename):
        saved_filename = save_profile_image(file, emp.name)
        if saved_filename:
            emp.profile_image = saved_filename
            db.session.commit()
            flash('✅ Profile photo updated successfully!', 'success')
        else:
            flash('❌ Error uploading photo. Please try again.', 'danger')
    else:
        flash('Invalid file type. Please upload JPG, PNG, or GIF only.', 'danger')
    
    return redirect(request.referrer or url_for('employee_dashboard'))


@app.route('/employee/attendance')
@login_required
def my_attendance():
    """View employee's attendance records."""
    user = repo.get_user_by_id(session['user_id'])
    
    # Try to find employee by exact username match
    emp = Employee.query.filter_by(email=user.username).first()
    
    # If not found, try with common email domains
    if not emp:
        emp = Employee.query.filter(
            (Employee.email == user.username + '@company.com') |
            (Employee.email == user.username + '@workflowx.com') |
            (Employee.email.like(f'%{user.username}%'))
        ).first()
    
    # CRITICAL: Never fall back to another employee's data!
    if not emp:
        flash('Your employee profile could not be found. Please contact HR to link your account.', 'danger')
        return redirect(url_for('employee_dashboard'))
    
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


# ==================== QR CODE ATTENDANCE CHECK-IN ====================

@app.route('/admin/qr-checkin')
@login_required
def admin_qr_checkin():
    """Display QR code for employee attendance check-in (Admin/HR view)."""
    if session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Automatically ensure token exists for today
    today = date.today().isoformat()
    token = get_or_create_qr_token(today)
    print(f"[QR PAGE] Using token for {today}")
    
    # Create check-in URL using the appropriate base URL for the environment
    # This works for both local development and Railway deployment
    base_url = get_base_url()
    checkin_url = f"{base_url}/checkin/{token}?date={today}"
    print(f"[QR PAGE] Generated QR URL: {checkin_url}")
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(checkin_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return render_template('admin_qr_checkin.html',
                         qr_code=qr_code_base64,
                         checkin_url=checkin_url,
                         today=today)


@app.route('/checkin/<token>')
def employee_qr_checkin(token):
    """Handle QR code scan and redirect to login if needed, then to check-in page."""
    checkin_date = request.args.get('date')
    print(f"[QR PAGE] Accessed with token: {token}, date: {checkin_date}, user_id: {session.get('user_id')}")
    
    if not checkin_date:
        flash('Invalid check-in link', 'danger')
        return redirect(url_for('login'))
    
    # Store token and date in session for later verification
    session['pending_checkin_token'] = token
    session['pending_checkin_date'] = checkin_date
    
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please login to check in', 'info')
        return redirect(url_for('login'))
    
    # Check if logged in user is an employee
    if session.get('role') != 'employee':
        flash('Only employees can use QR check-in', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check if date matches today (QR code expires after 24 hours)
    today_date = date.today().isoformat()
    if checkin_date != today_date:
        flash('This QR code has expired. It was valid for a different day.', 'warning')
        return redirect(url_for('employee_dashboard'))
    
    # Verify token exists and matches (don't auto-generate, just verify)
    stored_token = qr_tokens.get(checkin_date)
    if not stored_token:
        # Token doesn't exist - admin needs to generate QR code
        flash('No valid QR code found for today. Please ask admin to generate the QR code.', 'warning')
        return redirect(url_for('employee_dashboard'))
    
    if stored_token != token:
        flash('Invalid check-in link. This QR code is not valid.', 'danger')
        return redirect(url_for('employee_dashboard'))
    
    # Get employee information
    user = repo.get_user_by_id(session['user_id'])
    emp = Employee.query.filter_by(email=user.username).first()
    
    if not emp:
        emp = Employee.query.filter(
            (Employee.email == user.username + '@company.com') |
            (Employee.email == user.username + '@workflowx.com')
        ).first()
    
    # Check if employee has already checked in today
    today = date.today()
    existing_attendance = None
    if emp:
        existing_attendance = Attendance.query.filter_by(
            employee_id=emp.employee_id,
            date=today
        ).first()
        
        if existing_attendance:
            print(f"[QR PAGE] Found attendance: check_in_time={existing_attendance.check_in_time}, check_out_time={existing_attendance.check_out_time}")
        else:
            print(f"[QR PAGE] No attendance record found for today")
    
    # User is logged in and token is valid, show check-in/check-out page
    return render_template('employee_qr_checkin.html',
                         token=token,
                         checkin_date=checkin_date,
                         attendance=existing_attendance,
                         employee=emp)


@app.route('/checkin/submit', methods=['POST'])
@login_required
def submit_qr_checkin():
    """Process employee check-in from QR code scan."""
    print(f"[QR CHECK-IN] Received submission from user: {session.get('user_id')}, role: {session.get('role')}")
    
    if session.get('role') != 'employee':
        flash('This feature is only available for employees', 'danger')
        return redirect(url_for('dashboard'))
    
    token = request.form.get('token')
    checkin_date_str = request.form.get('date')
    print(f"[QR CHECK-IN] Token: {token}, Date: {checkin_date_str}")
    
    if not token or not checkin_date_str:
        flash('Invalid check-in data', 'danger')
        return redirect(url_for('employee_dashboard'))
    
    # Verify date is today
    if checkin_date_str != date.today().isoformat():
        flash('This QR code has expired. It was valid for a different day.', 'warning')
        return redirect(url_for('employee_dashboard'))
    
    # Token was already validated when the page loaded (in employee_qr_checkin route)
    # No need to validate again here - just process the check-in
    
    try:
        checkin_date = datetime.strptime(checkin_date_str, '%Y-%m-%d').date()
        
        # Get employee
        user = repo.get_user_by_id(session['user_id'])
        emp = Employee.query.filter_by(email=user.username).first()
        
        if not emp:
            emp = Employee.query.filter(
                (Employee.email == user.username + '@company.com') |
                (Employee.email == user.username + '@workflowx.com')
            ).first()
        
        if not emp:
            flash('Employee profile not found', 'danger')
            return redirect(url_for('employee_dashboard'))
        
        # Check if already checked in today (with actual check_in_time)
        existing = Attendance.query.filter_by(
            employee_id=emp.employee_id,
            date=checkin_date
        ).first()
        
        if existing and existing.check_in_time:
            flash(f'You have already checked in today at {existing.check_in_time.strftime("%I:%M %p")}', 'info')
            return redirect(f'/checkin/{token}?date={checkin_date_str}')
        
        # If there's an old record without check_in_time, delete it
        if existing and not existing.check_in_time:
            db.session.delete(existing)
            db.session.commit()
        
        # Determine status based on time
        now = datetime.now()
        check_in_time = now.time()
        
        # Define late cutoff time (9:20 AM as per template)
        late_cutoff_time = datetime.strptime('09:20', '%H:%M').time()
        
        if check_in_time < late_cutoff_time:
            status = 'Present'
        else:
            status = 'Late'
        
        # Create attendance record
        attendance = Attendance(
            employee_id=emp.employee_id,
            date=checkin_date,
            status=status,
            check_in_time=now,
            notes=''
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        # Log the action
        log_audit('CREATE', 'Attendance', attendance.attendance_id, 
                 f'Employee {emp.name} checked in via QR code - {status}')
        
        flash(f'Check-in successful! Status: {status} at {check_in_time.strftime("%I:%M %p")}', 'success')
        
        # Clear pending session data and redirect to employee dashboard
        session.pop('pending_checkin_token', None)
        session.pop('pending_checkin_date', None)
        return redirect(url_for('employee_dashboard'))
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error processing QR check-in: {str(e)}")
        flash('An error occurred during check-in. Please contact HR.', 'danger')
        return redirect(url_for('employee_dashboard'))


@app.route('/employee/checkout', methods=['POST'])
@login_required
def employee_checkout():
    """Process employee check-out."""
    if session.get('role') != 'employee':
        flash('This feature is only available for employees', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        today = date.today()
        
        # Get employee
        user = repo.get_user_by_id(session['user_id'])
        emp = Employee.query.filter_by(email=user.username).first()
        
        if not emp:
            emp = Employee.query.filter(
                (Employee.email == user.username + '@company.com') |
                (Employee.email == user.username + '@workflowx.com')
            ).first()
        
        if not emp:
            flash('Employee profile not found', 'danger')
            return redirect(url_for('employee_dashboard'))
        
        # Find today's attendance record
        attendance = Attendance.query.filter_by(
            employee_id=emp.employee_id,
            date=today
        ).first()
        
        if not attendance:
            flash('No check-in record found for today. Please check in first.', 'warning')
            return redirect(url_for('employee_dashboard'))
        
        if attendance.check_out_time:
            flash(f'You have already checked out today at {attendance.check_out_time.strftime("%I:%M %p")}', 'info')
            return redirect(url_for('employee_dashboard'))
        
        # Record check-out time
        now = datetime.now()
        attendance.check_out_time = now
        
        # Calculate hours worked
        hours_worked = attendance.calculate_hours_worked()
        
        # Update notes
        attendance.notes = f'Checked in: {attendance.check_in_time.strftime("%I:%M %p")} | Checked out: {now.strftime("%I:%M %p")} | Hours: {hours_worked}h'
        
        db.session.commit()
        
        # Log the action
        log_audit('UPDATE', 'Attendance', attendance.attendance_id, 
                 f'Employee {emp.name} checked out - {hours_worked}h worked')
        
        flash(f'Check-out successful at {now.strftime("%I:%M %p")}! Hours worked: {hours_worked}h', 'success')
        return redirect(url_for('employee_dashboard'))
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error processing check-out: {str(e)}")
        flash('An error occurred during check-out. Please contact HR.', 'danger')
        return redirect(url_for('employee_dashboard'))


# REMOVED: Manual check-in feature removed for security reasons
# Employees must physically scan QR code at office to verify presence
# @app.route('/employee/manual-checkin')
# @login_required
# def manual_checkin():
#     """Allow employees to manually check in if they can't scan QR code."""
#     if session.get('role') != 'employee':
#         flash('This feature is only available for employees', 'danger')
#         return redirect(url_for('dashboard'))
#     
#    oday = date.today()
    
    # Get employee
    user = repo.get_user_by_id(session['user_id'])
    emp = Employee.query.filter_by(email=user.username).first()
    
    if not emp:
        emp = Employee.query.filter(
            (Employee.email == user.username + '@company.com') |
            (Employee.email == user.username + '@workflowx.com')
        ).first()
    
    if not emp:
        flash('Employee profile not found', 'danger')
        return redirect(url_for('employee_dashboard'))
    
    # Find today's attendance record
    attendance = Attendance.query.filter_by(
        employee_id=emp.employee_id,
        date=today
    ).first()
    
    if not attendance:
        flash('No check-in record found for today. Please check in first.', 'warning')
        return redirect(url_for('employee_dashboard'))
    
    if attendance.check_out_time:
        flash(f'You have already checked out today at {attendance.check_out_time.strftime("%I:%M %p")}', 'info')
        return redirect(url_for('employee_dashboard'))
    
    # Record check-out time
    now = datetime.now()
    attendance.check_out_time = now
    
    # Calculate hours worked
    hours_worked = attendance.calculate_hours_worked()
    
    # Update notes to remove QR code text and add simple summary
    attendance.notes = f'Checked in: {attendance.check_in_time.strftime("%I:%M %p")} | Checked out: {now.strftime("%I:%M %p")} | Hours: {hours_worked}h'
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error processing check-out: {str(e)}")
        flash('An error occurred during check-out. Please contact HR.', 'danger')
        return redirect(url_for('employee_dashboard'))
    
    # Log the action (after successful commit)
    try:
        log_audit('UPDATE', 'Attendance', attendance.attendance_id, 
                 f'Employee {emp.first_name} {emp.last_name} checked out - {hours_worked}h worked')
    except Exception as e:
        app.logger.error(f"Error logging checkout audit: {str(e)}")
        # Don't show error to user, checkout was successful
    
    flash(f'Check-out successful at {now.strftime("%I:%M %p")}! Hours worked: {hours_worked}h', 'success')
    
    # If coming from QR flow, redirect back to QR page to show completion
    if request.form.get('from_qr') == 'true':
        token = request.form.get('token')
        checkin_date = request.form.get('date')
        if token and checkin_date:
            return redirect(f'/checkin/{token}?date={checkin_date}')
    
    
        db.session.commit()
        
        # Log the action
        log_audit('UPDATE', 'Attendance', attendance.attendance_id, 
                 f'Employee {emp.first_name} {emp.last_name} checked out - {hours_worked}h worked')
        
        flash(f'Check-out successful at {now.strftime("%I:%M %p")}! Hours worked: {hours_worked}h', 'success')
        
        # If coming from QR flow, redirect back to QR page to show completion
        if request.form.get('from_qr') == 'true':
            token = request.form.get('token')
            checkin_date = request.form.get('date')
            if token and checkin_date:
                return redirect(f'/checkin/{token}?date={checkin_date}')
        
        return redirect(url_for('employee_dashboard'))


# ==================== PAYROLL MANAGEMENT ROUTES ====================

@app.route('/payroll/regenerate-all', methods=['POST'])
@login_required
def regenerate_all_payroll():
    """Regenerate all payroll records for all employees from hire date to current month."""
    from models import Payroll
    if session.get('role') != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        from datetime import date
        from decimal import Decimal
        import calendar
        from dateutil.relativedelta import relativedelta
        from models import Deduction
        
        # Delete deductions first (FK constraint), then payroll records
        Deduction.query.delete()
        db.session.commit()
        
        Payroll.query.delete()
        db.session.commit()
        
        # Get all employees
        employees = Employee.query.all()
        company_start = date(2024, 1, 1)
        today = date.today()
        total_records = 0
        
        for emp in employees:
            if not emp.salary:
                continue
            
            # Calculate monthly salary from annual salary
            annual_salary = Decimal(str(emp.salary))
            monthly_gross = annual_salary / 12
            
            # Start from employee's hire date or company start, whichever is later
            start_from = max(emp.date_joined, company_start)
            current_date = start_from
            
            # Generate payroll from start date to current month
            while current_date <= today:
                last_day = calendar.monthrange(current_date.year, current_date.month)[1]
                period_start = date(current_date.year, current_date.month, 1)
                period_end = date(current_date.year, current_date.month, last_day)
                
                # Calculate realistic deductions
                pension = monthly_gross * Decimal('0.055')  # 5.5%
                income_tax = monthly_gross * Decimal('0.10')  # 10%
                health_insurance = monthly_gross * Decimal('0.025')  # 2.5%
                total_deductions = pension + income_tax + health_insurance
                monthly_net = monthly_gross - total_deductions
                
                payroll = Payroll(
                    employee_id=emp.employee_id,
                    pay_period_start=period_start,
                    pay_period_end=period_end,
                    gross_salary=monthly_gross
                )
                # Set additional attributes after initialization
                payroll.total_deductions = total_deductions
                payroll.net_salary = monthly_net
                payroll.payment_date = period_end
                payroll.payment_status = 'paid'
                
                db.session.add(payroll)
                total_records += 1
                
                # Move to next month
                current_date = (current_date + relativedelta(months=1)).replace(day=1)
        
        db.session.commit()
        
        log_audit('CREATE', 'Payroll', None, f'Initialized {total_records} payroll records from Jan 2024 for all employees')
        flash(f'Successfully initialized {total_records} payroll records for {len(employees)} employees from January 2024 to present!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error regenerating payroll: {str(e)}', 'danger')
    
    return redirect(url_for('payroll_dashboard'))


@app.route('/payroll')
@login_required
def payroll_dashboard():
    """Display payroll dashboard."""
    from models import Payroll
    if session.get('role') != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))
    
    user = repo.get_user_by_id(session['user_id'])
    
    # Get all payroll records
    payrolls = Payroll.query.order_by(Payroll.pay_period_end.desc()).all()
    
    # Calculate stats
    total_paid = sum(float(p.net_salary) for p in payrolls if p.payment_status == 'paid')
    pending_count = len([p for p in payrolls if p.payment_status == 'pending'])
    
    return render_template('payroll_dashboard.html', 
                         user=user, 
                         payrolls=payrolls,
                         total_paid=total_paid,
                         pending_count=pending_count)


@app.route('/payroll/generate', methods=['GET', 'POST'])
@login_required
def generate_payroll():
    """Generate payroll for selected month."""
    from models import Payroll, Deduction
    if session.get('role') != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        month = int(request.form.get('month'))
        year = int(request.form.get('year'))
        
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        # Get all active employees
        employees = Employee.query.filter_by(status='active').all()
        
        generated_count = 0
        for emp in employees:
            if emp.salary:
                # Create pay period
                start_date = date(year, month, 1)
                if month == 12:
                    end_date = date(year + 1, 1, 1) - relativedelta(days=1)
                else:
                    end_date = date(year, month + 1, 1) - relativedelta(days=1)
                
                # Check if payroll already exists
                existing = Payroll.query.filter_by(
                    employee_id=emp.employee_id,
                    pay_period_start=start_date,
                    pay_period_end=end_date
                ).first()
                
                if not existing:
                    payroll = Payroll(
                        employee_id=emp.employee_id,
                        pay_period_start=start_date,
                        pay_period_end=end_date,
                        gross_salary=emp.salary
                    )
                    
                    # Add statutory deductions (example: 10% tax, 5% insurance)
                    tax_amount = float(emp.salary) * 0.10
                    insurance_amount = float(emp.salary) * 0.05
                    
                    db.session.add(payroll)
                    db.session.flush()  # Get payroll_id
                    
                    tax_deduction = Deduction(
                        payroll_id=payroll.payroll_id,
                        deduction_type='tax',
                        deduction_name='Income Tax',
                        amount=tax_amount,
                        percentage=10.0,
                        is_statutory=True
                    )
                    
                    insurance_deduction = Deduction(
                        payroll_id=payroll.payroll_id,
                        deduction_type='insurance',
                        deduction_name='Health Insurance',
                        amount=insurance_amount,
                        percentage=5.0,
                        is_statutory=True
                    )
                    
                    db.session.add(tax_deduction)
                    db.session.add(insurance_deduction)
                    
                    payroll.add_deduction(tax_amount)
                    payroll.add_deduction(insurance_amount)
                    
                    generated_count += 1
        
        db.session.commit()
        
        repo.log_action(
            user_id=session['user_id'],
            action='generate_payroll',
            entity_type='payroll',
            description=f'Generated payroll for {month}/{year} ({generated_count} records)'
        )
        
        flash(f'Successfully generated {generated_count} payroll records for {month}/{year}', 'success')
        return redirect(url_for('payroll_dashboard'))
    
    user = repo.get_user_by_id(session['user_id'])
    return render_template('payroll_generate.html', user=user)


@app.route('/payroll/payslip/<int:payroll_id>')
@login_required
def view_payslip(payroll_id):
    """View detailed payslip."""
    from models import Payroll
    payroll = Payroll.query.get_or_404(payroll_id)
    
    # Check permissions
    if session.get('role') != 'admin':
        # Employees can only view their own payslips
        employee = Employee.query.filter_by(
            employee_id=payroll.employee_id
        ).first()
        if not employee or employee.email != session.get('username'):
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
    
    user = repo.get_user_by_id(session['user_id'])
    employee = Employee.query.get(payroll.employee_id)
    
    return render_template('payslip_view.html', 
                         user=user, 
                         payroll=payroll, 
                         employee=employee)


@app.route('/payroll/employee/<int:employee_id>')
@login_required
def salary_history(employee_id):
    """View salary history for employee."""
    from models import Payroll
    employee = Employee.query.get_or_404(employee_id)
    
    # Check permissions
    if session.get('role') != 'admin' and employee.email != session.get('username'):
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    user = repo.get_user_by_id(session['user_id'])
    payrolls = Payroll.query.filter_by(employee_id=employee_id).order_by(Payroll.pay_period_end.desc()).all()
    
    return render_template('salary_history.html', 
                         user=user, 
                         employee=employee, 
                         payrolls=payrolls)


@app.route('/payroll/mark_paid/<int:payroll_id>', methods=['POST'])
@login_required
def mark_payroll_paid(payroll_id):
    """Mark payroll as paid."""
    from models import Payroll
    if session.get('role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    payroll = Payroll.query.get_or_404(payroll_id)
    payroll.mark_as_paid()
    db.session.commit()
    
    repo.log_action(
        user_id=session['user_id'],
        action='mark_paid',
        entity_type='payroll',
        entity_id=payroll_id,
        description=f'Marked payroll {payroll_id} as paid'
    )
    
    flash('Payroll marked as paid', 'success')
    return redirect(url_for('payroll_dashboard'))


# ==================== PERFORMANCE MANAGEMENT ROUTES ====================

@app.route('/performance/reviews')
@login_required
def performance_reviews():
    """Display all performance reviews."""
    from models import PerformanceReview
    if session.get('role') != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))
    
    user = repo.get_user_by_id(session['user_id'])
    reviews = PerformanceReview.query.order_by(PerformanceReview.created_at.desc()).all()
    
    return render_template('reviews_list.html', user=user, reviews=reviews)


@app.route('/performance/review/select-employee')
@login_required
def select_employee_for_review():
    """Select employee to create performance review."""
    if session.get('role') != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))
    
    user = repo.get_user_by_id(session['user_id'])
    employees = repo.get_all_employees()
    
    return render_template('select_employee_review.html', user=user, employees=employees)


@app.route('/performance/review/create/<int:employee_id>', methods=['GET', 'POST'])
@login_required
def create_review(employee_id):
    """Create performance review."""
    from models import PerformanceReview
    if session.get('role') != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))
    
    employee = Employee.query.get_or_404(employee_id)
    
    if request.method == 'POST':
        from datetime import datetime
        
        review = PerformanceReview(
            employee_id=employee_id,
            reviewer_id=session['user_id'],
            review_period_start=datetime.strptime(request.form.get('period_start'), '%Y-%m-%d').date(),
            review_period_end=datetime.strptime(request.form.get('period_end'), '%Y-%m-%d').date()
        )
        
        review.overall_rating = int(request.form.get('rating', 0))
        review.strengths = request.form.get('strengths')
        review.areas_for_improvement = request.form.get('improvements')
        review.goals_met = request.form.get('goals_met') == 'on'
        review.comments = request.form.get('comments')
        review.status = 'submitted'
        
        db.session.add(review)
        db.session.commit()
        
        repo.log_action(
            user_id=session['user_id'],
            action='create_review',
            entity_type='performance_review',
            entity_id=review.review_id,
            description=f'Created performance review for employee {employee.name}'
        )
        
        flash('Performance review created successfully', 'success')
        return redirect(url_for('performance_reviews'))
    
    user = repo.get_user_by_id(session['user_id'])
    return render_template('review_form.html', user=user, employee=employee)


@app.route('/performance/review/view/<int:review_id>')
@login_required
def view_review(review_id):
    """View a specific performance review."""
    from models import PerformanceReview
    if session.get('role') != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))
    
    review = PerformanceReview.query.get_or_404(review_id)
    user = repo.get_user_by_id(session['user_id'])
    
    return render_template('review_detail.html', user=user, review=review)


@app.route('/performance/goals')
@login_required
def goals_dashboard():
    """Display goals dashboard."""
    from models import Goal
    user = repo.get_user_by_id(session['user_id'])
    
    if session.get('role') == 'admin':
        goals = Goal.query.order_by(Goal.target_date.desc()).all()
    else:
        # Employees see only their goals
        employee = Employee.query.filter_by(email=session.get('username')).first()
        if employee:
            goals = Goal.query.filter_by(employee_id=employee.employee_id).all()
        else:
            goals = []
    
    return render_template('goals_dashboard.html', user=user, goals=goals)


@app.route('/performance/goal/create', methods=['GET', 'POST'])
@login_required
def create_goal():
    """Create new goal."""
    from models import Goal
    
    if request.method == 'POST':
        employee_id = int(request.form.get('employee_id'))
        
        # Check permissions
        if session.get('role') != 'admin':
            employee = Employee.query.filter_by(email=session.get('username')).first()
            if not employee or employee.employee_id != employee_id:
                flash('Access denied.', 'danger')
                return redirect(url_for('dashboard'))
        
        from datetime import datetime
        
        goal = Goal(
            employee_id=employee_id,
            goal_title=request.form.get('title'),
            description=request.form.get('description'),
            target_date=datetime.strptime(request.form.get('target_date'), '%Y-%m-%d').date() if request.form.get('target_date') else None,
            priority=request.form.get('priority', 'medium'),
            created_by=session['user_id']
        )
        
        db.session.add(goal)
        db.session.commit()
        
        repo.log_action(
            user_id=session['user_id'],
            action='create_goal',
            entity_type='goal',
            entity_id=goal.goal_id,
            description=f'Created goal: {goal.goal_title}'
        )
        
        flash('Goal created successfully', 'success')
        return redirect(url_for('goals_dashboard'))
    
    user = repo.get_user_by_id(session['user_id'])
    employees = Employee.query.filter_by(status='active').all()
    return render_template('goal_form.html', user=user, employees=employees)


@app.route('/performance/goal/update/<int:goal_id>', methods=['POST'])
@login_required
def update_goal_progress(goal_id):
    """Update goal progress."""
    from models import Goal
    goal = Goal.query.get_or_404(goal_id)
    
    progress = int(request.form.get('progress', 0))
    goal.update_progress(progress)
    db.session.commit()
    
    flash('Goal progress updated', 'success')
    return redirect(url_for('goals_dashboard'))


@app.route('/performance/feedback/submit', methods=['GET', 'POST'])
@login_required
def submit_feedback():
    """Submit 360-degree feedback."""
    from models import Feedback
    
    if request.method == 'POST':
        employee_id = int(request.form.get('employee_id'))
        
        feedback = Feedback(
            employee_id=employee_id,
            from_user_id=session['user_id'],
            feedback_type=request.form.get('feedback_type'),
            rating=int(request.form.get('rating', 0)) if request.form.get('rating') else None,
            comments=request.form.get('comments'),
            is_anonymous=request.form.get('is_anonymous') == 'on'
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        repo.log_action(
            user_id=session['user_id'],
            action='submit_feedback',
            entity_type='feedback',
            entity_id=feedback.feedback_id,
            description=f'Submitted {feedback.feedback_type} feedback'
        )
        
        flash('Feedback submitted successfully', 'success')
        return redirect(url_for('dashboard'))
    
    user = repo.get_user_by_id(session['user_id'])
    employees = Employee.query.filter_by(status='active').all()
    return render_template('feedback_form.html', user=user, employees=employees)


# ==================== RECRUITMENT & ONBOARDING ROUTES ====================

@app.route('/recruitment')
@login_required
def recruitment_pipeline():
    """Display recruitment pipeline."""
    from models import Recruitment
    if session.get('role') != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))
    
    user = repo.get_user_by_id(session['user_id'])
    
    # Get candidates by status
    candidates = Recruitment.query.order_by(Recruitment.application_date.desc()).all()
    
    # Group by status
    by_status = {
        'applied': [c for c in candidates if c.status == 'applied'],
        'screening': [c for c in candidates if c.status == 'screening'],
        'interview': [c for c in candidates if c.status == 'interview'],
        'offer': [c for c in candidates if c.status == 'offer'],
        'hired': [c for c in candidates if c.status == 'hired'],
        'rejected': [c for c in candidates if c.status == 'rejected']
    }
    
    return render_template('recruitment_pipeline.html', user=user, by_status=by_status)


@app.route('/recruitment/candidate/add', methods=['GET', 'POST'])
@login_required
def add_candidate():
    """Add new candidate."""
    from models import Recruitment
    if session.get('role') != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        candidate = Recruitment(
            candidate_name=request.form.get('name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            position_applied=request.form.get('position'),
            department_id=int(request.form.get('department_id')) if request.form.get('department_id') else None
        )
        
        candidate.notes = request.form.get('notes')
        
        db.session.add(candidate)
        db.session.commit()
        
        repo.log_action(
            user_id=session['user_id'],
            action='add_candidate',
            entity_type='recruitment',
            entity_id=candidate.recruitment_id,
            description=f'Added candidate: {candidate.candidate_name}'
        )
        
        flash('Candidate added successfully', 'success')
        return redirect(url_for('recruitment_pipeline'))
    
    user = repo.get_user_by_id(session['user_id'])
    departments = Department.query.all()
    return render_template('candidate_form.html', user=user, departments=departments)


@app.route('/recruitment/candidate/<int:recruitment_id>/update_status', methods=['POST'])
@login_required
def update_candidate_status(recruitment_id):
    """Update candidate status."""
    from models import Recruitment
    if session.get('role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    candidate = Recruitment.query.get_or_404(recruitment_id)
    new_status = request.form.get('status')
    
    candidate.update_status(new_status)
    db.session.commit()
    
    repo.log_action(
        user_id=session['user_id'],
        action='update_candidate',
        entity_type='recruitment',
        entity_id=recruitment_id,
        description=f'Updated candidate status to {new_status}'
    )
    
    flash('Candidate status updated', 'success')
    return redirect(url_for('recruitment_pipeline'))


@app.route('/onboarding/tasks/<int:employee_id>')
@login_required
def onboarding_tasks(employee_id):
    """View onboarding tasks for employee."""
    from models import OnboardingTask
    employee = Employee.query.get_or_404(employee_id)
    
    # Check permissions
    if session.get('role') != 'admin' and employee.email != session.get('username'):
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    user = repo.get_user_by_id(session['user_id'])
    tasks = OnboardingTask.query.filter_by(employee_id=employee_id).order_by(OnboardingTask.due_date).all()
    
    return render_template('onboarding_tasks.html', user=user, employee=employee, tasks=tasks)


@app.route('/onboarding/task/create/<int:employee_id>', methods=['POST'])
@login_required
def create_onboarding_task(employee_id):
    """Create onboarding task."""
    from models import OnboardingTask
    if session.get('role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    from datetime import datetime
    
    task = OnboardingTask(
        employee_id=employee_id,
        task_title=request.form.get('title'),
        description=request.form.get('description'),
        due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date() if request.form.get('due_date') else None,
        priority=request.form.get('priority', 'medium'),
        assigned_to=int(request.form.get('assigned_to')) if request.form.get('assigned_to') else None
    )
    
    db.session.add(task)
    db.session.commit()
    
    flash('Onboarding task created', 'success')
    return redirect(url_for('onboarding_tasks', employee_id=employee_id))


@app.route('/onboarding/task/complete/<int:task_id>', methods=['POST'])
@login_required
def complete_onboarding_task(task_id):
    """Mark onboarding task as completed."""
    from models import OnboardingTask
    task = OnboardingTask.query.get_or_404(task_id)
    
    task.mark_completed()
    db.session.commit()
    
    flash('Task marked as completed', 'success')
    return redirect(url_for('onboarding_tasks', employee_id=task.employee_id))


# ==================== SCHEDULING ROUTES ====================

@app.route('/schedule')
@login_required
def schedule_calendar():
    """Display schedule calendar."""
    from models import Schedule
    user = repo.get_user_by_id(session['user_id'])
    
    if session.get('role') == 'admin':
        schedules = Schedule.query.filter(Schedule.schedule_date >= date.today()).order_by(Schedule.schedule_date).all()
    else:
        # Employees see only their schedules
        employee = Employee.query.filter_by(email=session.get('username')).first()
        if employee:
            schedules = Schedule.query.filter_by(employee_id=employee.employee_id).filter(
                Schedule.schedule_date >= date.today()
            ).order_by(Schedule.schedule_date).all()
        else:
            schedules = []
    
    return render_template('schedule_calendar.html', user=user, schedules=schedules)


@app.route('/schedule/create', methods=['GET', 'POST'])
@login_required
def create_schedule():
    """Create new schedule."""
    from models import Schedule, Shift
    if session.get('role') != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        from datetime import datetime
        
        employee_id = int(request.form.get('employee_id'))
        shift_id = int(request.form.get('shift_id')) if request.form.get('shift_id') else None
        
        schedule = Schedule(
            employee_id=employee_id,
            schedule_date=datetime.strptime(request.form.get('date'), '%Y-%m-%d').date(),
            start_time=datetime.strptime(request.form.get('start_time'), '%H:%M').time(),
            end_time=datetime.strptime(request.form.get('end_time'), '%H:%M').time(),
            shift_id=shift_id
        )
        
        schedule.notes = request.form.get('notes')
        
        db.session.add(schedule)
        db.session.commit()
        
        repo.log_action(
            user_id=session['user_id'],
            action='create_schedule',
            entity_type='schedule',
            entity_id=schedule.schedule_id,
            description=f'Created schedule for employee {employee_id}'
        )
        
        flash('Schedule created successfully', 'success')
        return redirect(url_for('schedule_calendar'))
    
    user = repo.get_user_by_id(session['user_id'])
    employees = Employee.query.filter_by(status='active').all()
    shifts = Shift.query.filter_by(is_active=True).all()
    return render_template('schedule_form.html', user=user, employees=employees, shifts=shifts)


@app.route('/schedule/shifts', methods=['GET', 'POST'])
@login_required
def manage_shifts():
    """Manage shift templates."""
    from models import Shift
    if session.get('role') != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        from datetime import datetime
        
        shift = Shift(
            shift_name=request.form.get('name'),
            start_time=datetime.strptime(request.form.get('start_time'), '%H:%M').time(),
            end_time=datetime.strptime(request.form.get('end_time'), '%H:%M').time(),
            description=request.form.get('description')
        )
        
        db.session.add(shift)
        db.session.commit()
        
        flash('Shift created successfully', 'success')
        return redirect(url_for('manage_shifts'))
    
    user = repo.get_user_by_id(session['user_id'])
    shifts = Shift.query.all()
    return render_template('shift_manager.html', user=user, shifts=shifts)


# ==================== MESSAGING SYSTEM ====================

@app.route('/admin/messages')
@admin_required
def admin_messages():
    """Admin view all sent messages (broadcast and specific) with drafts."""
    from models import Message
    from sqlalchemy import inspect, text
    
    user = repo.get_user_by_id(session['user_id'])
    
    # Check if new columns exist
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('messages')]
    has_draft = 'is_draft' in columns
    has_deleted = 'deleted_at' in columns
    
    # Get tab parameter (sent, drafts)
    tab = request.args.get('tab', 'sent')
    
    try:
        # Use raw SQL if columns don't exist to avoid ORM issues
        if not has_draft and not has_deleted:
            # Old schema - select only existing columns
            query = text("""
                SELECT message_id, sender_id, recipient_id, subject, body, 
                       is_broadcast, is_read, sent_at, read_at
                FROM messages 
                WHERE sender_id = :user_id 
                ORDER BY sent_at DESC
            """)
            result = db.session.execute(query, {'user_id': session['user_id']})
            rows = result.fetchall()
            
            # Manually create Message-like objects from raw SQL results
            # Define proxy class once
            class MessageProxy:
                def __init__(self, row_data):
                    try:
                        from datetime import datetime
                        self.message_id = row_data[0]
                        self.sender_id = row_data[1]
                        self.recipient_id = row_data[2]
                        self.subject = row_data[3]
                        self.body = row_data[4]
                        self.is_broadcast = bool(row_data[5])
                        self.is_read = bool(row_data[6])
                        # Convert string dates to datetime objects (SQLite stores as strings)
                        self.sent_at = datetime.fromisoformat(row_data[7]) if row_data[7] else None
                        self.read_at = datetime.fromisoformat(row_data[8]) if row_data[8] else None
                        # Load relationships with error handling
                        try:
                            self.sender = User.query.get(self.sender_id) if self.sender_id else None
                        except Exception as e:
                            app.logger.error(f"Error loading sender {self.sender_id}: {e}")
                            self.sender = None
                        
                        try:
                            self.recipient = User.query.get(self.recipient_id) if self.recipient_id else None
                        except Exception as e:
                            app.logger.error(f"Error loading recipient {self.recipient_id}: {e}")
                            self.recipient = None
                        
                        # Add employees attribute unconditionally (templates expect this)
                        if self.sender:
                            self.sender.employees = []
                        if self.recipient:
                            self.recipient.employees = []
                    except Exception as e:
                        app.logger.error(f"Error creating MessageProxy: {e}")
                        raise
            
            messages = [MessageProxy(row) for row in rows]
            drafts_count = 0
            app.logger.info(f"Loaded {len(messages)} admin messages for tab={tab} using old schema")
            
        else:
            # New schema with draft/deleted columns
            if tab == 'drafts' and has_draft:
                query = Message.query.filter_by(sender_id=session['user_id'], is_draft=True)
                if has_deleted:
                    query = query.filter(Message.deleted_at.is_(None))
                messages = query.order_by(Message.sent_at.desc()).all()
            else:  # sent messages
                query = Message.query.filter_by(sender_id=session['user_id'])
                if has_draft:
                    query = query.filter_by(is_draft=False)
                if has_deleted:
                    query = query.filter(Message.deleted_at.is_(None))
                messages = query.order_by(Message.sent_at.desc()).all()
            
            # Count drafts
            drafts_count = 0
            if has_draft:
                drafts_query = Message.query.filter_by(sender_id=session['user_id'], is_draft=True)
                if has_deleted:
                    drafts_query = drafts_query.filter(Message.deleted_at.is_(None))
                drafts_count = drafts_query.count()
        
        # Get all employees for compose modal (search) - convert to dict
        employees = Employee.query.order_by(Employee.name).all()
        employees_data = [emp.to_dict() for emp in employees]
        
        log_audit('VIEW', 'Messages', None, f'Admin viewed messages ({tab})')
        return render_template('admin_messages.html', user=user, messages=messages, 
                             employees_data=employees_data, current_tab=tab, drafts_count=drafts_count)
    except Exception as e:
        app.logger.error(f"Error in admin_messages: {str(e)}")
        flash('Error loading messages. Please try again.', 'danger')
        return redirect(url_for('dashboard'))


@app.route('/admin/messages/compose', methods=['GET', 'POST'])
@admin_required
def compose_message():
    """Admin compose and send message (specific or broadcast)."""
    from models import Message
    
    if request.method == 'POST':
        message_type = request.form.get('message_type')  # 'specific' or 'broadcast'
        subject = request.form.get('subject')
        body = request.form.get('body')
        
        if not subject or not body:
            flash('Subject and message body are required', 'danger')
            return redirect(url_for('compose_message'))
        
        try:
            from sqlalchemy import inspect, text
            # Check if draft columns exist
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('messages')]
            has_draft = 'is_draft' in columns
            
            if message_type == 'broadcast':
                # Send to all employees
                employees = Employee.query.all()
                sent_count = 0
                
                if not has_draft:
                    # Use raw SQL for broadcast without draft columns
                    for emp in employees:
                        user = User.query.filter_by(username=emp.email).first()
                        if user:
                            query = text("""
                                INSERT INTO messages (sender_id, recipient_id, subject, body, is_broadcast, is_read, sent_at)
                                VALUES (:sender_id, :recipient_id, :subject, :body, :is_broadcast, :is_read, :sent_at)
                            """)
                            db.session.execute(query, {
                                'sender_id': session['user_id'],
                                'recipient_id': user.user_id,
                                'subject': subject,
                                'body': body,
                                'is_broadcast': True,
                                'is_read': False,
                                'sent_at': datetime.utcnow().isoformat()
                            })
                            sent_count += 1
                else:
                    # Use ORM with draft columns
                    for emp in employees:
                        user = User.query.filter_by(username=emp.email).first()
                        if user:
                            message = Message(
                                sender_id=session['user_id'],
                                recipient_id=user.user_id,
                                subject=subject,
                                body=body,
                                is_broadcast=True
                            )
                            db.session.add(message)
                            sent_count += 1
                
                db.session.commit()
                log_audit('CREATE', 'Message', None, f'Broadcast message: {subject}')
                flash(f'Broadcast message sent to {sent_count} employees', 'success')
                
            else:  # specific employee
                recipient_id = request.form.get('recipient_id')
                if not recipient_id:
                    flash('Please select a recipient', 'danger')
                    return redirect(url_for('compose_message'))
                
                if not has_draft:
                    # Use raw SQL without draft columns
                    query = text("""
                        INSERT INTO messages (sender_id, recipient_id, subject, body, is_broadcast, is_read, sent_at)
                        VALUES (:sender_id, :recipient_id, :subject, :body, :is_broadcast, :is_read, :sent_at)
                    """)
                    db.session.execute(query, {
                        'sender_id': session['user_id'],
                        'recipient_id': int(recipient_id),
                        'subject': subject,
                        'body': body,
                        'is_broadcast': False,
                        'is_read': False,
                        'sent_at': datetime.utcnow().isoformat()
                    })
                    db.session.commit()
                else:
                    # Use ORM with draft columns
                    message = Message(
                        sender_id=session['user_id'],
                        recipient_id=int(recipient_id),
                        subject=subject,
                        body=body,
                        is_broadcast=False
                    )
                    db.session.add(message)
                    db.session.commit()
                
                log_audit('CREATE', 'Message', None, f'Message sent: {subject}')
                flash('Message sent successfully', 'success')
            
            return redirect(url_for('admin_messages'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error sending message: {str(e)}', 'danger')
            return redirect(url_for('compose_message'))
    
    # GET request - show compose form
    user = repo.get_user_by_id(session['user_id'])
    employees = Employee.query.order_by(Employee.name).all()
    employees_data = [emp.to_dict() for emp in employees]
    return render_template('compose_message.html', user=user, employees=employees_data)


@app.route('/employee/messages')
@login_required
def employee_messages():
    """Employee Gmail-style messaging interface (inbox, sent, drafts, compose)."""
    from models import Message
    from sqlalchemy import inspect, text
    
    user = repo.get_user_by_id(session['user_id'])
    
    # Check if new columns exist
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('messages')]
    has_draft = 'is_draft' in columns
    has_deleted = 'deleted_at' in columns
    
    # Get tab parameter (inbox, sent, or drafts)
    tab = request.args.get('tab', 'inbox')
    
    try:
        # Use raw SQL to avoid ORM column mapping issues with missing columns
        if not has_draft and not has_deleted:
            # Old schema - no draft or deleted columns
            # Build a custom query that only selects existing columns
            if tab == 'sent':
                query = text("""
                    SELECT message_id, sender_id, recipient_id, subject, body, 
                           is_broadcast, is_read, sent_at, read_at
                    FROM messages 
                    WHERE sender_id = :user_id 
                    ORDER BY sent_at DESC
                """)
            else:  # inbox (drafts tab won't work without the column)
                query = text("""
                    SELECT message_id, sender_id, recipient_id, subject, body, 
                           is_broadcast, is_read, sent_at, read_at
                    FROM messages 
                    WHERE recipient_id = :user_id 
                    ORDER BY sent_at DESC
                """)
            
            result = db.session.execute(query, {'user_id': session['user_id']})
            rows = result.fetchall()
            
            # Manually create Message-like objects from raw SQL results
            # Define proxy class once
            class MessageProxy:
                def __init__(self, row_data):
                    try:
                        from datetime import datetime
                        self.message_id = row_data[0]
                        self.sender_id = row_data[1]
                        self.recipient_id = row_data[2]
                        self.subject = row_data[3]
                        self.body = row_data[4]
                        self.is_broadcast = bool(row_data[5])
                        self.is_read = bool(row_data[6])
                        # Convert string dates to datetime objects (SQLite stores as strings)
                        self.sent_at = datetime.fromisoformat(row_data[7]) if row_data[7] else None
                        self.read_at = datetime.fromisoformat(row_data[8]) if row_data[8] else None
                        # Load relationships with error handling
                        try:
                            self.sender = User.query.get(self.sender_id) if self.sender_id else None
                        except Exception as e:
                            app.logger.error(f"Error loading sender {self.sender_id}: {e}")
                            self.sender = None
                        
                        try:
                            self.recipient = User.query.get(self.recipient_id) if self.recipient_id else None
                        except Exception as e:
                            app.logger.error(f"Error loading recipient {self.recipient_id}: {e}")
                            self.recipient = None
                        
                        # Add employees attribute unconditionally (templates expect this)
                        if self.sender:
                            self.sender.employees = []
                        if self.recipient:
                            self.recipient.employees = []
                    except Exception as e:
                        app.logger.error(f"Error creating MessageProxy: {e}")
                        raise
            
            messages = [MessageProxy(row) for row in rows]
            app.logger.info(f"Loaded {len(messages)} messages for tab={tab} using old schema")
            
            unread_count = db.session.execute(
                text("SELECT COUNT(*) FROM messages WHERE recipient_id = :user_id AND is_read = 0"),
                {'user_id': session['user_id']}
            ).scalar()
            drafts_count = 0
            
        else:
            # New schema with draft/deleted columns
            if tab == 'sent':
                query = Message.query.filter_by(sender_id=session['user_id'])
                if has_draft:
                    query = query.filter_by(is_draft=False)
                if has_deleted:
                    query = query.filter(Message.deleted_at.is_(None))
                messages = query.order_by(Message.sent_at.desc()).all()
                
            elif tab == 'drafts' and has_draft:
                query = Message.query.filter_by(sender_id=session['user_id'], is_draft=True)
                if has_deleted:
                    query = query.filter(Message.deleted_at.is_(None))
                messages = query.order_by(Message.sent_at.desc()).all()
                
            else:  # inbox
                query = Message.query.filter_by(recipient_id=session['user_id'])
                if has_draft:
                    query = query.filter_by(is_draft=False)
                if has_deleted:
                    query = query.filter(Message.deleted_at.is_(None))
                messages = query.order_by(Message.sent_at.desc()).all()
            
            # Count unread messages
            unread_query = Message.query.filter_by(recipient_id=session['user_id'], is_read=False)
            if has_deleted:
                unread_query = unread_query.filter(Message.deleted_at.is_(None))
            unread_count = unread_query.count()
            
            # Count drafts
            drafts_count = 0
            if has_draft:
                drafts_query = Message.query.filter_by(sender_id=session['user_id'], is_draft=True)
                if has_deleted:
                    drafts_query = drafts_query.filter(Message.deleted_at.is_(None))
                drafts_count = drafts_query.count()
        
        # Get all employees for compose modal (search) - convert to dict
        employees = Employee.query.order_by(Employee.name).all()
        employees_data = [emp.to_dict() for emp in employees]
        
        log_audit('VIEW', 'Messages', None, f'Employee viewed messages ({tab})')
        return render_template('employee_messages.html', 
                              user=user, 
                              messages=messages, 
                              unread_count=unread_count,
                              drafts_count=drafts_count,
                              employees=employees_data,
                              current_tab=tab)
    except Exception as e:
        import traceback
        app.logger.error(f"Error in employee_messages (tab={tab}): {str(e)}")
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        flash('Error loading messages. Please try again.', 'danger')
        return redirect(url_for('employee_dashboard'))


@app.route('/employee/messages/<int:message_id>')
@login_required
def view_message(message_id):
    """View specific message and mark as read."""
    from models import Message
    from sqlalchemy import inspect, text
    
    # Check if new columns exist
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('messages')]
    has_draft = 'is_draft' in columns
    has_deleted = 'deleted_at' in columns
    
    # Use raw SQL if columns don't exist
    if not has_draft and not has_deleted:
        # Get message with raw SQL
        query = text("""
            SELECT message_id, sender_id, recipient_id, subject, body, 
                   is_broadcast, is_read, sent_at, read_at
            FROM messages 
            WHERE message_id = :message_id
        """)
        result = db.session.execute(query, {'message_id': message_id})
        row = result.fetchone()
        
        if not row:
            abort(404)
        
        # Create MessageProxy
        from datetime import datetime
        class MessageProxy:
            def __init__(self, row_data):
                self.message_id = row_data[0]
                self.sender_id = row_data[1]
                self.recipient_id = row_data[2]
                self.subject = row_data[3]
                self.body = row_data[4]
                self.is_broadcast = bool(row_data[5])
                self.is_read = bool(row_data[6])
                self.sent_at = datetime.fromisoformat(row_data[7]) if row_data[7] else None
                self.read_at = datetime.fromisoformat(row_data[8]) if row_data[8] else None
                self.sender = User.query.get(self.sender_id) if self.sender_id else None
                self.recipient = User.query.get(self.recipient_id) if self.recipient_id else None
                if self.sender:
                    self.sender.employees = []
                if self.recipient:
                    self.recipient.employees = []
            
            def mark_as_read(self):
                """Mark message as read using raw SQL"""
                from datetime import datetime
                update_query = text("""
                    UPDATE messages 
                    SET is_read = 1, read_at = :read_at 
                    WHERE message_id = :message_id
                """)
                db.session.execute(update_query, {
                    'read_at': datetime.utcnow().isoformat(),
                    'message_id': self.message_id
                })
                self.is_read = True
                self.read_at = datetime.utcnow()
        
        message = MessageProxy(row)
    else:
        message = Message.query.get_or_404(message_id)
    
    # Ensure user can view messages they sent OR received
    if message.recipient_id != session['user_id'] and message.sender_id != session['user_id']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('employee_messages'))
    
    # Mark as read if not already (only for received messages)
    if message.recipient_id == session['user_id'] and not message.is_read:
        message.mark_as_read()
        db.session.commit()
    
    user = repo.get_user_by_id(session['user_id'])
    
    # Get conversation thread (all messages between these two users) - use raw SQL if needed
    if not has_draft and not has_deleted:
        conv_query = text("""
            SELECT message_id, sender_id, recipient_id, subject, body, 
                   is_broadcast, is_read, sent_at, read_at
            FROM messages 
            WHERE (sender_id = :sender_id AND recipient_id = :recipient_id)
               OR (sender_id = :recipient_id AND recipient_id = :sender_id)
            ORDER BY sent_at ASC
        """)
        result = db.session.execute(conv_query, {
            'sender_id': message.sender_id,
            'recipient_id': message.recipient_id
        })
        rows = result.fetchall()
        conversation = [MessageProxy(row) for row in rows]
    else:
        conversation = Message.query.filter(
            ((Message.sender_id == message.sender_id) & (Message.recipient_id == message.recipient_id)) |
            ((Message.sender_id == message.recipient_id) & (Message.recipient_id == message.sender_id))
        ).order_by(Message.sent_at.asc()).all()
    
    # Get employee profiles for all users in conversation
    user_ids = set([msg.sender_id for msg in conversation if msg.sender_id])
    user_profiles = {}
    for uid in user_ids:
        u = User.query.get(uid)
        if u:
            emp = Employee.query.filter_by(email=u.username).first()
            user_profiles[uid] = {'username': u.username, 'profile_image': emp.profile_image if emp else 'default-avatar.png'}
    
    return render_template('view_message.html', user=user, message=message, conversation=conversation, user_profiles=user_profiles)


@app.route('/admin/message/<int:message_id>')
@admin_required
def admin_view_message(message_id):
    """Admin view sent message."""
    from models import Message
    from sqlalchemy import inspect, text
    
    # Check if new columns exist
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('messages')]
    has_draft = 'is_draft' in columns
    has_deleted = 'deleted_at' in columns
    
    # Use raw SQL if columns don't exist
    if not has_draft and not has_deleted:
        # Get message with raw SQL
        query = text("""
            SELECT message_id, sender_id, recipient_id, subject, body, 
                   is_broadcast, is_read, sent_at, read_at
            FROM messages 
            WHERE message_id = :message_id
        """)
        result = db.session.execute(query, {'message_id': message_id})
        row = result.fetchone()
        
        if not row:
            abort(404)
        
        # Create MessageProxy (same class as in view_message)
        from datetime import datetime
        class MessageProxy:
            def __init__(self, row_data):
                self.message_id = row_data[0]
                self.sender_id = row_data[1]
                self.recipient_id = row_data[2]
                self.subject = row_data[3]
                self.body = row_data[4]
                self.is_broadcast = bool(row_data[5])
                self.is_read = bool(row_data[6])
                self.sent_at = datetime.fromisoformat(row_data[7]) if row_data[7] else None
                self.read_at = datetime.fromisoformat(row_data[8]) if row_data[8] else None
                self.sender = User.query.get(self.sender_id) if self.sender_id else None
                self.recipient = User.query.get(self.recipient_id) if self.recipient_id else None
                if self.sender:
                    self.sender.employees = []
                if self.recipient:
                    self.recipient.employees = []
        
        message = MessageProxy(row)
    else:
        message = Message.query.get_or_404(message_id)
    
    # Ensure admin can only view messages they sent
    if message.sender_id != session['user_id']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('admin_messages'))
    
    user = repo.get_user_by_id(session['user_id'])
    
    # Get conversation thread - use raw SQL if needed
    if not has_draft and not has_deleted:
        conv_query = text("""
            SELECT message_id, sender_id, recipient_id, subject, body, 
                   is_broadcast, is_read, sent_at, read_at
            FROM messages 
            WHERE (sender_id = :sender_id AND recipient_id = :recipient_id)
               OR (sender_id = :recipient_id AND recipient_id = :sender_id)
            ORDER BY sent_at ASC
        """)
        result = db.session.execute(conv_query, {
            'sender_id': message.sender_id,
            'recipient_id': message.recipient_id
        })
        rows = result.fetchall()
        conversation = [MessageProxy(row) for row in rows]
    else:
        conversation = Message.query.filter(
            ((Message.sender_id == message.sender_id) & (Message.recipient_id == message.recipient_id)) |
            ((Message.sender_id == message.recipient_id) & (Message.recipient_id == message.sender_id))
        ).order_by(Message.sent_at.asc()).all()
    
    # Get employee profiles for all users in conversation
    user_ids = set([msg.sender_id for msg in conversation if msg.sender_id])
    user_profiles = {}
    for uid in user_ids:
        u = User.query.get(uid)
        if u:
            emp = Employee.query.filter_by(email=u.username).first()
            user_profiles[uid] = {'username': u.username, 'profile_image': emp.profile_image if emp else 'default-avatar.png'}
    
    return render_template('admin_view_message.html', user=user, message=message, conversation=conversation, user_profiles=user_profiles)


@app.route('/employee/messages/send', methods=['POST'])
@login_required
def employee_send_message():
    """Employee send message to HR/Admin or reply to existing message."""
    from models import Message
    from sqlalchemy import inspect, text
    
    recipient_id = request.form.get('recipient_id')
    subject = request.form.get('subject')
    body = request.form.get('body')
    
    if not recipient_id or not subject or not body:
        flash('All fields are required', 'danger')
        return redirect(url_for('employee_messages'))
    
    try:
        # Check if draft columns exist
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('messages')]
        has_draft = 'is_draft' in columns
        
        if not has_draft:
            # Use raw SQL to insert without draft columns
            query = text("""
                INSERT INTO messages (sender_id, recipient_id, subject, body, is_broadcast, is_read, sent_at)
                VALUES (:sender_id, :recipient_id, :subject, :body, :is_broadcast, :is_read, :sent_at)
            """)
            result = db.session.execute(query, {
                'sender_id': session['user_id'],
                'recipient_id': int(recipient_id),
                'subject': subject,
                'body': body,
                'is_broadcast': False,
                'is_read': False,
                'sent_at': datetime.utcnow().isoformat()
            })
            db.session.commit()
            log_audit('CREATE', 'Message', None, f'Employee sent message: {subject}')
        else:
            # Use ORM with draft columns
            message = Message(
                sender_id=session['user_id'],
                recipient_id=int(recipient_id),
                subject=subject,
                body=body,
                is_broadcast=False
            )
            db.session.add(message)
            db.session.commit()
            log_audit('CREATE', 'Message', message.message_id, f'Employee sent message: {subject}')
        
        flash('Message sent successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error sending message: {str(e)}', 'danger')
    
    return redirect(url_for('employee_messages', tab='sent'))


@app.route('/messages/save-draft', methods=['POST'])
@login_required
def save_draft():
    """Save message as draft (admin or employee)."""
    from models import Message
    from sqlalchemy import inspect, text
    
    message_type = request.form.get('message_type')
    recipient_id = request.form.get('recipient_id')
    subject = request.form.get('subject', '(No Subject)')
    body = request.form.get('body', '')
    draft_id = request.form.get('draft_id')  # For updating existing draft
    
    try:
        # Check if draft columns exist
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('messages')]
        has_draft = 'is_draft' in columns
        
        if not has_draft:
            flash('Draft functionality is not yet available. Migration is running on next restart.', 'info')
            return redirect(url_for('compose_message' if session.get('role') == 'admin' else 'employee_messages'))
        
        if draft_id:
            # Update existing draft
            draft = Message.query.filter_by(
                message_id=int(draft_id),
                sender_id=session['user_id'],
                is_draft=True
            ).first()
            
            if not draft:
                flash('Draft not found or access denied', 'danger')
                return redirect(url_for('compose_message' if session.get('role') == 'admin' else 'employee_messages'))
            
            draft.subject = subject
            draft.body = body
            draft.recipient_id = int(recipient_id) if recipient_id and recipient_id != 'broadcast' else None
            draft.is_broadcast = (message_type == 'broadcast')
            
            flash('Draft updated successfully', 'success')
        else:
            # Create new draft using raw SQL to ensure is_draft=1
            is_broadcast = 1 if message_type == 'broadcast' else 0
            recipient = int(recipient_id) if recipient_id and recipient_id != 'broadcast' else None
            
            query = text("""
                INSERT INTO messages (sender_id, recipient_id, subject, body, is_broadcast, is_read, is_draft, sent_at)
                VALUES (:sender_id, :recipient_id, :subject, :body, :is_broadcast, :is_read, :is_draft, :sent_at)
            """)
            db.session.execute(query, {
                'sender_id': session['user_id'],
                'recipient_id': recipient,
                'subject': subject,
                'body': body,
                'is_broadcast': is_broadcast,
                'is_read': 0,
                'is_draft': 1,
                'sent_at': datetime.utcnow().isoformat()
            })
            flash('Draft saved successfully', 'success')
        
        db.session.commit()
        log_audit('CREATE' if not draft_id else 'UPDATE', 'Message', None, f'Draft saved: {subject}')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error saving draft: {str(e)}', 'danger')
    
    return redirect(url_for('compose_message' if session.get('role') == 'admin' else 'employee_messages'))


@app.route('/messages/delete/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    """Soft delete a message (marks as deleted without removing from database)."""
    from models import Message
    
    try:
        message = Message.query.get(message_id)
        
        if not message:
            flash('Message not found', 'danger')
        elif message.sender_id != session['user_id'] and message.recipient_id != session['user_id']:
            flash('You do not have permission to delete this message', 'danger')
        else:
            # Soft delete - mark as deleted instead of removing
            message.deleted_at = datetime.utcnow()
            db.session.commit()
            
            log_audit('DELETE', 'Message', message_id, f'Message deleted: {message.subject}')
            flash('Message deleted successfully', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting message: {str(e)}', 'danger')
    
    # Redirect based on role
    if session.get('role') == 'admin':
        return redirect(url_for('admin_messages'))
    else:
        return redirect(url_for('employee_messages'))


@app.route('/messages/send-draft/<int:draft_id>', methods=['POST'])
@login_required
def send_draft(draft_id):
    """Convert a draft message to sent message."""
    from models import Message
    
    try:
        draft = Message.query.filter_by(
            message_id=draft_id,
            sender_id=session['user_id'],
            is_draft=True
        ).first()
        
        if not draft:
            flash('Draft not found or already sent', 'danger')
            return redirect(url_for('compose_message' if session.get('role') == 'admin' else 'employee_messages'))
        
        # Validate required fields
        if not draft.subject or not draft.body:
            flash('Subject and body are required to send message', 'danger')
            return redirect(url_for('compose_message' if session.get('role') == 'admin' else 'employee_messages'))
        
        if draft.is_broadcast:
            # Send broadcast - create copies for all employees
            employees = Employee.query.all()
            sent_count = 0
            for emp in employees:
                user = User.query.filter_by(username=emp.email).first()
                if user:
                    message = Message(
                        sender_id=draft.sender_id,
                        recipient_id=user.user_id,
                        subject=draft.subject,
                        body=draft.body,
                        is_broadcast=True,
                        is_draft=False
                    )
                    db.session.add(message)
                    sent_count += 1
            
            # Delete the draft
            db.session.delete(draft)
            db.session.commit()
            
            log_audit('CREATE', 'Message', None, f'Broadcast sent from draft: {draft.subject}')
            flash(f'Broadcast message sent to {sent_count} employees', 'success')
        else:
            # Send to specific recipient
            if not draft.recipient_id:
                flash('Please select a recipient', 'danger')
                return redirect(url_for('compose_message' if session.get('role') == 'admin' else 'employee_messages'))
            
            # Mark as sent
            draft.is_draft = False
            draft.sent_at = datetime.utcnow()
            db.session.commit()
            
            log_audit('UPDATE', 'Message', draft.message_id, f'Draft sent: {draft.subject}')
            flash('Message sent successfully', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error sending draft: {str(e)}', 'danger')
    
    if session.get('role') == 'admin':
        return redirect(url_for('admin_messages'))
    else:
        return redirect(url_for('employee_messages'))


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
