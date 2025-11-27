"""
WorkFlowX - Database Models

This module defines all database models using SQLAlchemy ORM.
Demonstrates Object-Oriented Programming principles:
- Encapsulation: Data and methods bundled together
- Abstraction: Complex database operations hidden behind simple interfaces
- Classes with __init__, __str__, __repr__, and custom methods
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
            'total_leave_days': self.get_total_leave_days()
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
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Composite unique constraint: one attendance record per employee per date
    __table_args__ = (
        db.UniqueConstraint('employee_id', 'date', name='unique_employee_date'),
    )
    
    def __init__(self, employee_id, date, status, notes=None):
        """
        Initialize a new Attendance record.
        
        Args:
            employee_id: ID of employee
            date: Date of attendance
            status: Attendance status
            notes: Optional notes
        """
        self.employee_id = employee_id
        self.date = date
        self.status = status
        self.notes = notes
    
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
            'reviewed_at': self.reviewed_at.strftime('%Y-%m-%d %H:%M:%S') if self.reviewed_at else None
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
