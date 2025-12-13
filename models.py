"""
WorkFlowX - Database Models

This module defines all database models using SQLAlchemy ORM.
Uses Object-Oriented Programming with classes that bundle data and methods together.
Database operations are abstracted through clean interfaces, with custom methods
for calculations and business logic. Each model includes initialization, string
representation, and conversion methods for easy data handling.
"""

from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """
    User model for authentication and authorization.
    
    Attributes:
        user_id: Primary key
        username: Unique username for login
        password_hash: Hashed password (never store plain text!)
        role: User role ('admin' or 'employee')
        created_at: Timestamp of account creation
    """
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='employee')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, username, password, role='employee'):
        """
        Initialize a new User instance.
        
        Args:
            username: Unique username
            password: Plain text password (will be hashed)
            role: User role (admin or employee)
        """
        self.username = username
        self.set_password(password)
        self.role = role
    
    def set_password(self, password):
        """
        Hash and set the user's password.
        Security: Uses werkzeug's generate_password_hash for secure hashing.
        
        Args:
            password: Plain text password to hash
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Verify a password against the stored hash.
        
        Args:
            password: Plain text password to check
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """
        Convert user object to dictionary for JSON serialization.
        
        Returns:
            dict: User data (excluding sensitive password)
        """
        return {
            'user_id': self.user_id,
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
    
    def __str__(self):
        """String representation for debugging."""
        return f"User('{self.username}', '{self.role}')"
    
    def __repr__(self):
        """Official string representation."""
        return f"<User {self.user_id}: {self.username}>"


class Department(db.Model):
    """
    Department model for organizing employees.
    
    Attributes:
        department_id: Primary key
        name: Unique department name
        description: Department description
        created_at: Timestamp of creation
        employees: Relationship to Employee model
    """
    __tablename__ = 'departments'
    
    department_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship: One department has many employees
    employees = db.relationship('Employee', backref='department', lazy='dynamic')
    
    def __init__(self, name, description=None):
        """
        Initialize a new Department.
        
        Args:
            name: Department name
            description: Optional department description
        """
        self.name = name
        self.description = description
    
    def get_employee_count(self):
        """
        Calculate the number of employees in this department.
        
        Returns:
            int: Number of employees
        """
        return self.employees.count()
    
    def can_delete(self):
        """
        Check if department can be deleted (no employees assigned).
        Business rule: Cannot delete department with active employees.
        
        Returns:
            bool: True if safe to delete, False otherwise
        """
        return self.get_employee_count() == 0
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'department_id': self.department_id,
            'name': self.name,
            'description': self.description,
            'employee_count': self.get_employee_count(),
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        }
    
    def __str__(self):
        return f"Department('{self.name}')"
    
    def __repr__(self):
        return f"<Department {self.department_id}: {self.name}>"


class Role(db.Model):
    """
    Role/Job Title model.
    
    Attributes:
        role_id: Primary key
        title: Unique role title (e.g., "Software Engineer", "HR Manager")
        description: Role description and responsibilities
        created_at: Timestamp of creation
        employees: Relationship to Employee model
    """
    __tablename__ = 'roles'
    
    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship: One role can be assigned to many employees
    employees = db.relationship('Employee', backref='role', lazy='dynamic')
    
    def __init__(self, title, description=None):
        """
        Initialize a new Role.
        
        Args:
            title: Role/job title
            description: Optional role description
        """
        self.title = title
        self.description = description
    
    def get_employee_count(self):
        """
        Calculate the number of employees with this role.
        
        Returns:
            int: Number of employees
        """
        return self.employees.count()
    
    def can_delete(self):
        """
        Check if role can be deleted (no employees assigned).
        
        Returns:
            bool: True if safe to delete, False otherwise
        """
        return self.get_employee_count() == 0
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'role_id': self.role_id,
            'title': self.title,
            'description': self.description,
            'employee_count': self.get_employee_count(),
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        }
    
    def __str__(self):
        return f"Role('{self.title}')"
    
    def __repr__(self):
        return f"<Role {self.role_id}: {self.title}>"


class Employee(db.Model):
    """
    Employee model - core entity of the system.
    
    Attributes:
        employee_id: Primary key
        name: Employee full name
        email: Unique email address
        phone: Contact phone number
        department_id: Foreign key to Department
        role_id: Foreign key to Role
        salary: Employee salary
        date_joined: Date employee joined company
        status: Employment status ('active' or 'inactive')
        created_at: Timestamp of record creation
    """
    __tablename__ = 'employees'
    
    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    profile_image = db.Column(db.String(255), default='default-avatar.png')  # Profile image filename
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    salary = db.Column(db.Numeric(10, 2))  # Decimal for precise currency values
    date_joined = db.Column(db.Date)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    leave_requests = db.relationship('LeaveRequest', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, name, email, phone, department_id, role_id, salary, date_joined, status='active'):
        """
        Initialize a new Employee.
        
        Args:
            name: Employee full name
            email: Email address
            phone: Phone number
            department_id: ID of department
            role_id: ID of role
            salary: Salary amount
            date_joined: Date of joining
            status: Employment status (default: 'active')
        """
        self.name = name
        self.email = email
        self.phone = phone
        self.department_id = department_id
        self.role_id = role_id
        self.salary = salary
        self.date_joined = date_joined
        self.status = status
    
    def get_attendance_percentage(self):
        """
        Calculate employee's attendance percentage.
        
        Returns:
            float: Attendance percentage (0-100)
        """
        total_records = self.attendance_records.count()
        if total_records == 0:
            return 0.0
        
        present_count = self.attendance_records.filter_by(status='Present').count()
        return round((present_count / total_records) * 100, 2)
    
    def get_total_leave_days(self):
        """
        Calculate total approved leave days for employee.
        
        Returns:
            int: Total number of approved leave days
        """
        approved_leaves = self.leave_requests.filter_by(status='Approved').all()
        total_days = 0
        
        for leave in approved_leaves:
            # Calculate days between start and end date
            if leave.start_date and leave.end_date:
                delta = leave.end_date - leave.start_date
                total_days += delta.days + 1  # +1 to include both start and end dates
        
        return total_days
    
    def is_active(self):
        """
        Check if employee is currently active.
        
        Returns:
            bool: True if active, False otherwise
        """
        return self.status.lower() == 'active'
    
    def deactivate(self):
        """Soft delete: Mark employee as inactive instead of deleting."""
        self.status = 'inactive'
    
    def activate(self):
        """Reactivate an inactive employee."""
        self.status = 'active'
    
    def to_dict(self):
        """Convert to dictionary."""
        # Get user_id by finding user with matching email
        user = User.query.filter_by(username=self.email).first()
        return {
            'employee_id': self.employee_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'role_id': self.role_id,
            'role_title': self.role.title if self.role else None,
            'salary': float(self.salary) if self.salary else None,
            'date_joined': self.date_joined.strftime('%Y-%m-%d') if self.date_joined else None,
            'status': self.status,
            'attendance_percentage': self.get_attendance_percentage(),
            'total_leave_days': self.get_total_leave_days(),
            'photo_filename': self.profile_image,
            'profile_image': self.profile_image,  # Add for message search compatibility
            'user_id': user.user_id if user else None
        }
    
    def __str__(self):
        return f"Employee('{self.name}', '{self.email}')"
    
    def __repr__(self):
        return f"<Employee {self.employee_id}: {self.name}>"


class Attendance(db.Model):
    """
    Attendance tracking model.
    
    Attributes:
        attendance_id: Primary key
        employee_id: Foreign key to Employee
        date: Date of attendance
        status: Attendance status ('Present', 'Absent', 'Late')
        notes: Optional notes
        created_at: Timestamp of record creation
    """
    __tablename__ = 'attendance'
    
    attendance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'Present', 'Absent', 'Late'
    check_in_time = db.Column(db.DateTime)  # Timestamp of check-in
    check_out_time = db.Column(db.DateTime)  # Timestamp of check-out
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Composite unique constraint: one attendance record per employee per date
    __table_args__ = (
        db.UniqueConstraint('employee_id', 'date', name='unique_employee_date'),
    )
    
    def __init__(self, employee_id, date, status, check_in_time=None, check_out_time=None, notes=None):
        """
        Initialize a new Attendance record.
        
        Args:
            employee_id: ID of employee
            date: Date of attendance
            status: Attendance status
            check_in_time: Check-in timestamp
            check_out_time: Check-out timestamp
            notes: Optional notes
        """
        self.employee_id = employee_id
        self.date = date
        self.status = status
        self.check_in_time = check_in_time
        self.check_out_time = check_out_time
        self.notes = notes
    
    def calculate_hours_worked(self):
        """Calculate hours worked based on check-in and check-out times."""
        if self.check_in_time and self.check_out_time:
            delta = self.check_out_time - self.check_in_time
            hours = delta.total_seconds() / 3600
            return round(hours, 2)
        return 0
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'attendance_id': self.attendance_id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'status': self.status,
            'notes': self.notes
        }
    
    def __str__(self):
        return f"Attendance({self.employee.name if self.employee else 'Unknown'}, {self.date}, {self.status})"
    
    def __repr__(self):
        return f"<Attendance {self.attendance_id}: Employee {self.employee_id} on {self.date}>"


class LeaveRequest(db.Model):
    """
    Leave request management model.
    
    Attributes:
        leave_id: Primary key
        employee_id: Foreign key to Employee
        start_date: Leave start date
        end_date: Leave end date
        leave_type: Type of leave ('Annual', 'Sick', 'Personal')
        reason: Reason for leave
        status: Request status ('Pending', 'Approved', 'Rejected')
        submitted_at: Timestamp of submission
        reviewed_at: Timestamp of review (approval/rejection)
    """
    __tablename__ = 'leave_requests'
    
    leave_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)  # 'Annual', 'Sick', 'Personal'
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')  # 'Pending', 'Approved', 'Rejected'
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    hr_notes = db.Column(db.Text, nullable=True)  # HR notes for approval/rejection decision
    
    def __init__(self, employee_id, start_date, end_date, leave_type, reason=None):
        """
        Initialize a new Leave Request.
        
        Args:
            employee_id: ID of employee requesting leave
            start_date: Leave start date
            end_date: Leave end date
            leave_type: Type of leave
            reason: Optional reason for leave
        """
        self.employee_id = employee_id
        self.start_date = start_date
        self.end_date = end_date
        self.leave_type = leave_type
        self.reason = reason
    
    def calculate_days(self):
        """
        Calculate number of days for this leave request.
        
        Returns:
            int: Number of days (inclusive of start and end dates)
        """
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            return delta.days + 1  # +1 to include both start and end dates
        return 0
    
    def approve(self):
        """Approve the leave request."""
        self.status = 'Approved'
        self.reviewed_at = datetime.utcnow()
    
    def reject(self):
        """Reject the leave request."""
        self.status = 'Rejected'
        self.reviewed_at = datetime.utcnow()
    
    def is_pending(self):
        """
        Check if request is still pending.
        
        Returns:
            bool: True if pending, False otherwise
        """
        return self.status == 'Pending'
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'leave_id': self.leave_id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'leave_type': self.leave_type,
            'reason': self.reason,
            'status': self.status,
            'days': self.calculate_days(),
            'submitted_at': self.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if self.submitted_at else None,
            'reviewed_at': self.reviewed_at.strftime('%Y-%m-%d %H:%M:%S') if self.reviewed_at else None,
            'hr_notes': self.hr_notes
        }
    
    def __str__(self):
        return f"LeaveRequest({self.employee.name if self.employee else 'Unknown'}, {self.leave_type}, {self.status})"
    
    def __repr__(self):
        return f"<LeaveRequest {self.leave_id}: Employee {self.employee_id} - {self.status}>"


class AuditLog(db.Model):
    """
    AuditLog model for tracking all critical operations.
    
    Attributes:
        audit_id: Primary key
        user_id: User who performed the action
        action: Type of action performed
        entity_type: Type of entity affected (Employee, Leave, etc)
        entity_id: ID of entity affected
        description: Detailed description of what changed
        timestamp: When the action occurred
        ip_address: IP address of the user
    """
    __tablename__ = 'audit_logs'
    
    audit_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # CREATE, UPDATE, DELETE, APPROVE, REJECT
    entity_type = db.Column(db.String(50), nullable=False)  # Employee, Leave, Attendance, etc
    entity_id = db.Column(db.Integer)
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(45))
    
    user = db.relationship('User', backref='audit_logs')
    
    def __init__(self, user_id, action, entity_type, entity_id=None, description=None, ip_address=None):
        self.user_id = user_id
        self.action = action
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.description = description
        self.ip_address = ip_address
    
    def to_dict(self):
        return {
            'audit_id': self.audit_id,
            'user_id': self.user_id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'description': self.description,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None,
            'ip_address': self.ip_address
        }
    
    def __repr__(self):
        return f"<AuditLog {self.audit_id}: {self.action} on {self.entity_type}>"


# ==================== PAYROLL MANAGEMENT MODELS ====================

class Payroll(db.Model):
    """
    Payroll model for managing employee salary payments.
    
    Attributes:
        payroll_id: Primary key
        employee_id: Foreign key to Employee
        pay_period_start: Start date of pay period
        pay_period_end: End date of pay period
        gross_salary: Base salary before deductions
        total_deductions: Sum of all deductions
        net_salary: Final salary after deductions
        payment_date: Date salary was paid
        payment_status: Status of payment (pending/paid/failed)
        payment_method: Method of payment (bank transfer, cash, check)
        created_at: Record creation timestamp
    """
    __tablename__ = 'payroll'
    
    payroll_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    pay_period_start = db.Column(db.Date, nullable=False)
    pay_period_end = db.Column(db.Date, nullable=False)
    gross_salary = db.Column(db.Numeric(10, 2), nullable=False)
    total_deductions = db.Column(db.Numeric(10, 2), default=0)
    net_salary = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.Date)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed
    payment_method = db.Column(db.String(50), default='bank_transfer')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = db.relationship('Employee', backref='payroll_records')
    deductions = db.relationship('Deduction', backref='payroll', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, employee_id, pay_period_start, pay_period_end, gross_salary):
        self.employee_id = employee_id
        self.pay_period_start = pay_period_start
        self.pay_period_end = pay_period_end
        self.gross_salary = gross_salary
        self.total_deductions = 0  # Initialize to 0 before calculating
        self.calculate_net_salary()
    
    def calculate_net_salary(self):
        """Calculate net salary by subtracting deductions from gross salary."""
        deductions = self.total_deductions if self.total_deductions is not None else 0
        self.net_salary = float(self.gross_salary) - float(deductions)
    
    def add_deduction(self, deduction_amount):
        """Add a deduction and recalculate net salary."""
        self.total_deductions = float(self.total_deductions) + deduction_amount
        self.calculate_net_salary()
    
    def mark_as_paid(self, payment_date=None):
        """Mark payroll as paid."""
        self.payment_status = 'paid'
        self.payment_date = payment_date or datetime.now().date()
    
    def to_dict(self):
        return {
            'payroll_id': self.payroll_id,
            'employee_id': self.employee_id,
            'pay_period_start': self.pay_period_start.isoformat() if self.pay_period_start else None,
            'pay_period_end': self.pay_period_end.isoformat() if self.pay_period_end else None,
            'gross_salary': float(self.gross_salary),
            'total_deductions': float(self.total_deductions),
            'net_salary': float(self.net_salary),
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method
        }
    
    def __repr__(self):
        return f"<Payroll {self.payroll_id}: Employee {self.employee_id} - ${self.net_salary}>"


class Deduction(db.Model):
    """
    Deduction model for salary deductions (tax, insurance, etc.).
    
    Attributes:
        deduction_id: Primary key
        payroll_id: Foreign key to Payroll
        deduction_type: Type of deduction (tax, insurance, loan, etc.)
        deduction_name: Name/description of deduction
        amount: Deduction amount
        percentage: Percentage of gross salary (if applicable)
        created_at: Record creation timestamp
    """
    __tablename__ = 'deductions'
    
    deduction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    payroll_id = db.Column(db.Integer, db.ForeignKey('payroll.payroll_id'), nullable=False)
    deduction_type = db.Column(db.String(50), nullable=False)  # tax, insurance, loan, pension, etc.
    deduction_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    percentage = db.Column(db.Numeric(5, 2))  # Optional percentage
    is_statutory = db.Column(db.Boolean, default=False)  # Required by law
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, payroll_id, deduction_type, deduction_name, amount, percentage=None, is_statutory=False):
        self.payroll_id = payroll_id
        self.deduction_type = deduction_type
        self.deduction_name = deduction_name
        self.amount = amount
        self.percentage = percentage
        self.is_statutory = is_statutory
    
    def to_dict(self):
        return {
            'deduction_id': self.deduction_id,
            'deduction_type': self.deduction_type,
            'deduction_name': self.deduction_name,
            'amount': float(self.amount),
            'percentage': float(self.percentage) if self.percentage else None,
            'is_statutory': self.is_statutory
        }
    
    def __repr__(self):
        return f"<Deduction {self.deduction_id}: {self.deduction_name} - ${self.amount}>"


# ==================== PERFORMANCE MANAGEMENT MODELS ====================

class PerformanceReview(db.Model):
    """
    Performance review model for employee evaluations.
    
    Attributes:
        review_id: Primary key
        employee_id: Foreign key to Employee
        reviewer_id: Foreign key to User (reviewer)
        review_period_start: Start of review period
        review_period_end: End of review period
        overall_rating: Overall performance rating (1-5)
        strengths: Employee strengths
        areas_for_improvement: Areas needing improvement
        goals_met: Were goals achieved
        comments: Additional comments
        status: Review status (draft, submitted, completed)
        created_at: Record creation timestamp
    """
    __tablename__ = 'performance_reviews'
    
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    review_period_start = db.Column(db.Date, nullable=False)
    review_period_end = db.Column(db.Date, nullable=False)
    overall_rating = db.Column(db.Integer)  # 1-5 scale
    strengths = db.Column(db.Text)
    areas_for_improvement = db.Column(db.Text)
    goals_met = db.Column(db.Boolean, default=False)
    comments = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')  # draft, submitted, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = db.relationship('Employee', backref='performance_reviews')
    reviewer = db.relationship('User', backref='reviews_given')
    
    def __init__(self, employee_id, reviewer_id, review_period_start, review_period_end):
        self.employee_id = employee_id
        self.reviewer_id = reviewer_id
        self.review_period_start = review_period_start
        self.review_period_end = review_period_end
    
    def submit(self):
        """Submit the review."""
        self.status = 'submitted'
        self.updated_at = datetime.utcnow()
    
    def complete(self):
        """Mark review as completed."""
        self.status = 'completed'
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'review_id': self.review_id,
            'employee_id': self.employee_id,
            'reviewer_id': self.reviewer_id,
            'review_period_start': self.review_period_start.isoformat() if self.review_period_start else None,
            'review_period_end': self.review_period_end.isoformat() if self.review_period_end else None,
            'overall_rating': self.overall_rating,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<PerformanceReview {self.review_id}: Employee {self.employee_id} - Rating {self.overall_rating}>"


class Goal(db.Model):
    """
    Goal model for employee goal setting and tracking.
    
    Attributes:
        goal_id: Primary key
        employee_id: Foreign key to Employee
        goal_title: Title of the goal
        description: Detailed description
        target_date: Target completion date
        status: Goal status (not_started, in_progress, completed, cancelled)
        progress: Progress percentage (0-100)
        priority: Priority level (low, medium, high)
        created_by: User who created the goal
        created_at: Record creation timestamp
    """
    __tablename__ = 'goals'
    
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    goal_title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    target_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, completed, cancelled
    progress = db.Column(db.Integer, default=0)  # 0-100
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = db.relationship('User', backref='goals_created')
    
    def __init__(self, employee_id, goal_title, description=None, target_date=None, priority='medium', created_by=None):
        self.employee_id = employee_id
        self.goal_title = goal_title
        self.description = description
        self.target_date = target_date
        self.priority = priority
        self.created_by = created_by
    
    def update_progress(self, progress):
        """Update goal progress."""
        self.progress = min(100, max(0, progress))
        if self.progress == 100:
            self.status = 'completed'
        elif self.progress > 0:
            self.status = 'in_progress'
        self.updated_at = datetime.utcnow()
    
    def is_overdue(self):
        """Check if goal is overdue."""
        if self.target_date and self.status not in ['completed', 'cancelled']:
            return datetime.now().date() > self.target_date
        return False
    
    def to_dict(self):
        return {
            'goal_id': self.goal_id,
            'employee_id': self.employee_id,
            'goal_title': self.goal_title,
            'description': self.description,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'status': self.status,
            'progress': self.progress,
            'priority': self.priority,
            'is_overdue': self.is_overdue()
        }
    
    def __repr__(self):
        return f"<Goal {self.goal_id}: {self.goal_title} - {self.progress}%>"


class Feedback(db.Model):
    """
    Feedback model for 360-degree feedback system.
    
    Attributes:
        feedback_id: Primary key
        employee_id: Foreign key to Employee (recipient)
        from_user_id: Foreign key to User (feedback giver)
        feedback_type: Type of feedback (peer, manager, self, subordinate)
        rating: Rating score (1-5)
        comments: Feedback comments
        is_anonymous: Whether feedback is anonymous
        created_at: Record creation timestamp
    """
    __tablename__ = 'feedback'
    
    feedback_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    feedback_type = db.Column(db.String(20), nullable=False)  # peer, manager, self, subordinate
    rating = db.Column(db.Integer)  # 1-5
    comments = db.Column(db.Text)
    is_anonymous = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    from_user = db.relationship('User', backref='feedback_given')
    
    def __init__(self, employee_id, from_user_id, feedback_type, rating=None, comments=None, is_anonymous=False):
        self.employee_id = employee_id
        self.from_user_id = from_user_id
        self.feedback_type = feedback_type
        self.rating = rating
        self.comments = comments
        self.is_anonymous = is_anonymous
    
    def to_dict(self):
        return {
            'feedback_id': self.feedback_id,
            'employee_id': self.employee_id,
            'from_user_id': self.from_user_id if not self.is_anonymous else None,
            'feedback_type': self.feedback_type,
            'rating': self.rating,
            'comments': self.comments,
            'is_anonymous': self.is_anonymous,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<Feedback {self.feedback_id}: {self.feedback_type} for Employee {self.employee_id}>"


# ==================== ONBOARDING & RECRUITMENT MODELS ====================

class Recruitment(db.Model):
    """
    Recruitment model for tracking job candidates.
    
    Attributes:
        recruitment_id: Primary key
        candidate_name: Name of candidate
        email: Candidate email
        phone: Candidate phone
        position_applied: Position applied for
        department_id: Foreign key to Department
        resume_file: Resume filename
        status: Recruitment status (applied, screening, interview, offer, hired, rejected)
        application_date: Date of application
        interview_date: Scheduled interview date
        notes: Recruitment notes
        created_at: Record creation timestamp
    """
    __tablename__ = 'recruitment'
    
    recruitment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    candidate_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    position_applied = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'))
    resume_file = db.Column(db.String(255))
    status = db.Column(db.String(20), default='applied')  # applied, screening, interview, offer, hired, rejected
    application_date = db.Column(db.Date, default=datetime.utcnow)
    interview_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, candidate_name, email, position_applied, phone=None, department_id=None):
        self.candidate_name = candidate_name
        self.email = email
        self.position_applied = position_applied
        self.phone = phone
        self.department_id = department_id
    
    def update_status(self, new_status):
        """Update recruitment status."""
        self.status = new_status
        self.updated_at = datetime.utcnow()
    
    def schedule_interview(self, interview_date):
        """Schedule interview."""
        self.interview_date = interview_date
        self.status = 'interview'
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'recruitment_id': self.recruitment_id,
            'candidate_name': self.candidate_name,
            'email': self.email,
            'position_applied': self.position_applied,
            'status': self.status,
            'application_date': self.application_date.isoformat() if self.application_date else None,
            'interview_date': self.interview_date.isoformat() if self.interview_date else None
        }
    
    def __repr__(self):
        return f"<Recruitment {self.recruitment_id}: {self.candidate_name} - {self.status}>"


class OnboardingTask(db.Model):
    """
    Onboarding task model for new hire checklist.
    
    Attributes:
        task_id: Primary key
        employee_id: Foreign key to Employee
        task_title: Title of onboarding task
        description: Task description
        assigned_to: User responsible for completing task
        due_date: Task due date
        status: Task status (pending, in_progress, completed)
        completed_date: Date task was completed
        priority: Task priority (low, medium, high)
        created_at: Record creation timestamp
    """
    __tablename__ = 'onboarding_tasks'
    
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    task_title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    completed_date = db.Column(db.Date)
    priority = db.Column(db.String(20), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    assigned_user = db.relationship('User', backref='onboarding_tasks_assigned')
    
    def __init__(self, employee_id, task_title, description=None, assigned_to=None, due_date=None, priority='medium'):
        self.employee_id = employee_id
        self.task_title = task_title
        self.description = description
        self.assigned_to = assigned_to
        self.due_date = due_date
        self.priority = priority
    
    def mark_completed(self):
        """Mark task as completed."""
        self.status = 'completed'
        self.completed_date = datetime.now().date()
    
    def is_overdue(self):
        """Check if task is overdue."""
        if self.due_date and self.status != 'completed':
            return datetime.now().date() > self.due_date
        return False
    
    def to_dict(self):
        return {
            'task_id': self.task_id,
            'employee_id': self.employee_id,
            'task_title': self.task_title,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'priority': self.priority,
            'is_overdue': self.is_overdue()
        }
    
    def __repr__(self):
        return f"<OnboardingTask {self.task_id}: {self.task_title} - {self.status}>"


# ==================== SCHEDULING MODELS ====================

class Schedule(db.Model):
    """
    Schedule model for managing employee work schedules.
    
    Attributes:
        schedule_id: Primary key
        employee_id: Foreign key to Employee
        shift_id: Foreign key to Shift
        schedule_date: Date of scheduled shift
        start_time: Shift start time
        end_time: Shift end time
        status: Schedule status (scheduled, completed, cancelled, no_show)
        notes: Additional notes
        created_at: Record creation timestamp
    """
    __tablename__ = 'schedules'
    
    schedule_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    shift_id = db.Column(db.Integer, db.ForeignKey('shifts.shift_id'))
    schedule_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled, no_show
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, employee_id, schedule_date, start_time, end_time, shift_id=None):
        self.employee_id = employee_id
        self.schedule_date = schedule_date
        self.start_time = start_time
        self.end_time = end_time
        self.shift_id = shift_id
    
    def get_duration_hours(self):
        """Calculate shift duration in hours."""
        from datetime import datetime, timedelta
        start = datetime.combine(self.schedule_date, self.start_time)
        end = datetime.combine(self.schedule_date, self.end_time)
        if end < start:
            end += timedelta(days=1)
        duration = end - start
        return duration.total_seconds() / 3600
    
    def mark_completed(self):
        """Mark schedule as completed."""
        self.status = 'completed'
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'schedule_id': self.schedule_id,
            'employee_id': self.employee_id,
            'schedule_date': self.schedule_date.isoformat() if self.schedule_date else None,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'status': self.status,
            'duration_hours': self.get_duration_hours()
        }
    
    def __repr__(self):
        return f"<Schedule {self.schedule_id}: Employee {self.employee_id} on {self.schedule_date}>"


class Shift(db.Model):
    """
    Shift model for defining shift templates.
    
    Attributes:
        shift_id: Primary key
        shift_name: Name of shift (e.g., Morning, Evening, Night)
        start_time: Default start time
        end_time: Default end time
        description: Shift description
        is_active: Whether shift is currently active
        created_at: Record creation timestamp
    """
    __tablename__ = 'shifts'
    
    shift_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shift_name = db.Column(db.String(50), nullable=False, unique=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    schedules = db.relationship('Schedule', backref='shift', lazy='dynamic')
    
    def __init__(self, shift_name, start_time, end_time, description=None):
        self.shift_name = shift_name
        self.start_time = start_time
        self.end_time = end_time
        self.description = description
    
    def to_dict(self):
        return {
            'shift_id': self.shift_id,
            'shift_name': self.shift_name,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f"<Shift {self.shift_id}: {self.shift_name}>"


class Message(db.Model):
    """
    Message model for internal communication between admin and employees.
    Supports both specific employee messages and broadcast messages to all employees.
    
    Attributes:
        message_id: Primary key
        sender_id: Foreign key to User (admin who sent the message)
        recipient_id: Foreign key to User (employee recipient, NULL for broadcasts)
        subject: Message subject/title
        body: Message content
        is_broadcast: Boolean indicating if message is sent to all employees
        is_read: Boolean indicating if recipient has read the message
        sent_at: Timestamp when message was sent
        read_at: Timestamp when message was read (NULL if unread)
    """
    __tablename__ = 'messages'
    
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)  # NULL for broadcast
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    is_broadcast = db.Column(db.Boolean, default=False)
    is_read = db.Column(db.Boolean, default=False)
    is_draft = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')
    
    def __init__(self, sender_id, subject, body, recipient_id=None, is_broadcast=False, is_draft=False):
        """
        Initialize a new Message.
        
        Args:
            sender_id: ID of admin/user sending the message
            subject: Message subject
            body: Message content
            recipient_id: ID of employee recipient (None for broadcast)
            is_broadcast: Whether message is broadcast to all employees
            is_draft: Whether message is saved as draft (not sent yet)
        """
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.subject = subject
        self.body = body
        self.is_broadcast = is_broadcast
        self.is_draft = is_draft
    
    def mark_as_read(self):
        """Mark message as read and record the timestamp."""
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert message to dictionary representation."""
        return {
            'message_id': self.message_id,
            'sender_id': self.sender_id,
            'sender_name': self.sender.username if self.sender else None,
            'recipient_id': self.recipient_id,
            'recipient_name': self.recipient.username if self.recipient else 'All Employees',
            'subject': self.subject,
            'body': self.body,
            'is_broadcast': self.is_broadcast,
            'is_read': self.is_read,
            'is_draft': self.is_draft,
            'sent_at': self.sent_at.strftime('%Y-%m-%d %H:%M:%S') if self.sent_at else None,
            'read_at': self.read_at.strftime('%Y-%m-%d %H:%M:%S') if self.read_at else None,
            'deleted_at': self.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if self.deleted_at else None
        }
    
    def __repr__(self):
        recipient_str = 'Broadcast' if self.is_broadcast else f'User {self.recipient_id}'
        return f"<Message {self.message_id}: {self.subject} to {recipient_str}>"
