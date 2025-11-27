"""
WorkFlowX - Database Repository Layer

This module contains all database operations using SQLAlchemy ORM.
Demonstrates:
- Database CRUD operations
- Transaction management
- Exception handling with try/except/finally blocks
- Parameterized queries (SQLAlchemy ORM prevents SQL injection by default)
- Function design following Single Responsibility Principle
"""

from app import db
from models import User, Department, Role, Employee, Attendance, LeaveRequest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import Optional, List, Dict
from datetime import date


# ==================== USER REPOSITORY ====================

def create_user(username: str, password: str, role: str = 'employee') -> tuple:
    """
    Create a new user in the database.
    
    Week 3 Concept: Exception handling with try/except/finally
    Week 7 Concept: Database operations with transaction management
    
    Args:
        username: Unique username
        password: Plain text password (will be hashed by User model)
        role: User role ('admin' or 'employee')
        
    Returns:
        tuple: (success: bool, message: str, user: User or None)
    """
    try:
        # Create new User instance (OOP Week 4-5)
        user = User(username=username, password=password, role=role)
        
        # Add to database session
        db.session.add(user)
        
        # Commit transaction
        db.session.commit()
        
        return True, "User created successfully", user
        
    except IntegrityError:
        # Rollback on error (Week 7: transaction management)
        db.session.rollback()
        return False, "Username already exists", None
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error creating user: {str(e)}", None


def get_user_by_username(username: str) -> Optional[User]:
    """
    Retrieve user by username.
    
    Args:
        username: Username to search for
        
    Returns:
        Optional[User]: User object or None if not found
    """
    try:
        # SQLAlchemy ORM query (prevents SQL injection)
        return User.query.filter_by(username=username).first()
    except Exception:
        return None


def get_user_by_id(user_id: int) -> Optional[User]:
    """
    Retrieve user by ID.
    
    Args:
        user_id: User ID
        
    Returns:
        Optional[User]: User object or None
    """
    try:
        return User.query.get(user_id)
    except Exception:
        return None


# ==================== DEPARTMENT REPOSITORY ====================

def create_department(name: str, description: str = None) -> tuple:
    """
    Create a new department.
    
    Args:
        name: Department name
        description: Optional description
        
    Returns:
        tuple: (success: bool, message: str, department: Department or None)
    """
    try:
        department = Department(name=name, description=description)
        db.session.add(department)
        db.session.commit()
        return True, "Department created successfully", department
        
    except IntegrityError:
        db.session.rollback()
        return False, "Department name already exists", None
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error creating department: {str(e)}", None


def get_all_departments() -> List[Department]:
    """
    Retrieve all departments.
    
    Week 5 Concept: Lists to store query results
    
    Returns:
        List[Department]: List of all departments
    """
    try:
        return Department.query.order_by(Department.name).all()
    except Exception:
        return []


def get_department_by_id(department_id: int) -> Optional[Department]:
    """
    Retrieve department by ID.
    
    Args:
        department_id: Department ID
        
    Returns:
        Optional[Department]: Department object or None
    """
    try:
        return Department.query.get(department_id)
    except Exception:
        return None


def update_department(department_id: int, name: str, description: str = None) -> tuple:
    """
    Update department details.
    
    Args:
        department_id: ID of department to update
        name: New department name
        description: New description
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        department = Department.query.get(department_id)
        
        if not department:
            return False, "Department not found"
        
        department.name = name
        department.description = description
        
        db.session.commit()
        return True, "Department updated successfully"
        
    except IntegrityError:
        db.session.rollback()
        return False, "Department name already exists"
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error updating department: {str(e)}"


def delete_department(department_id: int) -> tuple:
    """
    Delete a department (only if no employees assigned).
    
    Business Rule: Cannot delete department with active employees
    
    Args:
        department_id: ID of department to delete
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        department = Department.query.get(department_id)
        
        if not department:
            return False, "Department not found"
        
        # Check if department can be deleted (Week 2: if/else logic)
        if not department.can_delete():
            return False, "Cannot delete department with assigned employees"
        
        db.session.delete(department)
        db.session.commit()
        return True, "Department deleted successfully"
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error deleting department: {str(e)}"


# ==================== ROLE REPOSITORY ====================

def create_role(title: str, description: str = None) -> tuple:
    """
    Create a new role.
    
    Args:
        title: Role title
        description: Optional description
        
    Returns:
        tuple: (success: bool, message: str, role: Role or None)
    """
    try:
        role = Role(title=title, description=description)
        db.session.add(role)
        db.session.commit()
        return True, "Role created successfully", role
        
    except IntegrityError:
        db.session.rollback()
        return False, "Role title already exists", None
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error creating role: {str(e)}", None


def get_all_roles() -> List[Role]:
    """
    Retrieve all roles.
    
    Returns:
        List[Role]: List of all roles
    """
    try:
        return Role.query.order_by(Role.title).all()
    except Exception:
        return []


def get_role_by_id(role_id: int) -> Optional[Role]:
    """
    Retrieve role by ID.
    
    Args:
        role_id: Role ID
        
    Returns:
        Optional[Role]: Role object or None
    """
    try:
        return Role.query.get(role_id)
    except Exception:
        return None


def update_role(role_id: int, title: str, description: str = None) -> tuple:
    """
    Update role details.
    
    Args:
        role_id: ID of role to update
        title: New role title
        description: New description
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        role = Role.query.get(role_id)
        
        if not role:
            return False, "Role not found"
        
        role.title = title
        role.description = description
        
        db.session.commit()
        return True, "Role updated successfully"
        
    except IntegrityError:
        db.session.rollback()
        return False, "Role title already exists"
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error updating role: {str(e)}"


def delete_role(role_id: int) -> tuple:
    """
    Delete a role (only if no employees assigned).
    
    Args:
        role_id: ID of role to delete
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        role = Role.query.get(role_id)
        
        if not role:
            return False, "Role not found"
        
        if not role.can_delete():
            return False, "Cannot delete role with assigned employees"
        
        db.session.delete(role)
        db.session.commit()
        return True, "Role deleted successfully"
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error deleting role: {str(e)}"


# ==================== EMPLOYEE REPOSITORY ====================

def create_employee(name: str, email: str, phone: str, department_id: int, 
                   role_id: int, salary: float, date_joined: date, status: str = 'active') -> tuple:
    """
    Create a new employee.
    
    Args:
        name: Employee name
        email: Email address
        phone: Phone number
        department_id: Department ID
        role_id: Role ID
        salary: Salary amount
        date_joined: Date joined
        status: Employment status
        
    Returns:
        tuple: (success: bool, message: str, employee: Employee or None)
    """
    try:
        employee = Employee(
            name=name,
            email=email,
            phone=phone,
            department_id=department_id,
            role_id=role_id,
            salary=salary,
            date_joined=date_joined,
            status=status
        )
        
        db.session.add(employee)
        db.session.commit()
        return True, "Employee created successfully", employee
        
    except IntegrityError:
        db.session.rollback()
        return False, "Email already exists", None
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error creating employee: {str(e)}", None


def get_all_employees(include_inactive: bool = False) -> List[Employee]:
    """
    Retrieve all employees.
    
    Args:
        include_inactive: Whether to include inactive employees
        
    Returns:
        List[Employee]: List of employees
    """
    try:
        query = Employee.query
        
        # Filter by status if not including inactive (Week 2: if/else)
        if not include_inactive:
            query = query.filter_by(status='active')
        
        return query.order_by(Employee.name).all()
    except Exception:
        return []


def get_employee_by_id(employee_id: int) -> Optional[Employee]:
    """
    Retrieve employee by ID.
    
    Args:
        employee_id: Employee ID
        
    Returns:
        Optional[Employee]: Employee object or None
    """
    try:
        return Employee.query.get(employee_id)
    except Exception:
        return None


def search_employees(search_term: str) -> List[Employee]:
    """
    Search employees by name or email.
    
    Args:
        search_term: Search term
        
    Returns:
        List[Employee]: Matching employees
    """
    try:
        search_pattern = f"%{search_term}%"
        return Employee.query.filter(
            (Employee.name.ilike(search_pattern)) | 
            (Employee.email.ilike(search_pattern))
        ).all()
    except Exception:
        return []


def update_employee(employee_id: int, **kwargs) -> tuple:
    """
    Update employee details.
    
    Args:
        employee_id: Employee ID
        **kwargs: Fields to update
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        employee = Employee.query.get(employee_id)
        
        if not employee:
            return False, "Employee not found"
        
        # Update fields (Week 5: dictionary operations)
        for key, value in kwargs.items():
            if hasattr(employee, key):
                setattr(employee, key, value)
        
        db.session.commit()
        return True, "Employee updated successfully"
        
    except IntegrityError:
        db.session.rollback()
        return False, "Email already exists"
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error updating employee: {str(e)}"


def delete_employee(employee_id: int, soft_delete: bool = True) -> tuple:
    """
    Delete or deactivate an employee.
    
    Args:
        employee_id: Employee ID
        soft_delete: If True, mark inactive; if False, hard delete
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        employee = Employee.query.get(employee_id)
        
        if not employee:
            return False, "Employee not found"
        
        if soft_delete:
            # Soft delete: mark as inactive
            employee.deactivate()
            db.session.commit()
            return True, "Employee marked as inactive"
        else:
            # Hard delete: remove from database
            db.session.delete(employee)
            db.session.commit()
            return True, "Employee deleted permanently"
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error deleting employee: {str(e)}"


# ==================== ATTENDANCE REPOSITORY ====================

def mark_attendance(employee_id: int, attendance_date: date, status: str, notes: str = None) -> tuple:
    """
    Mark attendance for an employee.
    
    Args:
        employee_id: Employee ID
        attendance_date: Date of attendance
        status: Attendance status ('Present', 'Absent', 'Late')
        notes: Optional notes
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Check if attendance already exists for this employee and date
        existing = Attendance.query.filter_by(
            employee_id=employee_id,
            date=attendance_date
        ).first()
        
        if existing:
            # Update existing record
            existing.status = status
            existing.notes = notes
            message = "Attendance updated successfully"
        else:
            # Create new record
            attendance = Attendance(
                employee_id=employee_id,
                date=attendance_date,
                status=status,
                notes=notes
            )
            db.session.add(attendance)
            message = "Attendance marked successfully"
        
        db.session.commit()
        return True, message
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error marking attendance: {str(e)}"


def get_attendance_by_date(attendance_date: date) -> List[Attendance]:
    """
    Get all attendance records for a specific date.
    
    Args:
        attendance_date: Date to query
        
    Returns:
        List[Attendance]: Attendance records
    """
    try:
        return Attendance.query.filter_by(date=attendance_date).all()
    except Exception:
        return []


def get_attendance_by_employee(employee_id: int) -> List[Attendance]:
    """
    Get all attendance records for a specific employee.
    
    Args:
        employee_id: Employee ID
        
    Returns:
        List[Attendance]: Attendance records
    """
    try:
        return Attendance.query.filter_by(employee_id=employee_id).order_by(Attendance.date.desc()).all()
    except Exception:
        return []


# ==================== LEAVE REQUEST REPOSITORY ====================

def create_leave_request(employee_id: int, start_date: date, end_date: date, 
                        leave_type: str, reason: str = None) -> tuple:
    """
    Create a new leave request.
    
    Args:
        employee_id: Employee ID
        start_date: Leave start date
        end_date: Leave end date
        leave_type: Type of leave
        reason: Reason for leave
        
    Returns:
        tuple: (success: bool, message: str, leave_request: LeaveRequest or None)
    """
    try:
        leave_request = LeaveRequest(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            leave_type=leave_type,
            reason=reason
        )
        
        db.session.add(leave_request)
        db.session.commit()
        return True, "Leave request submitted successfully", leave_request
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error creating leave request: {str(e)}", None


def get_all_leave_requests(status: str = None) -> List[LeaveRequest]:
    """
    Get all leave requests, optionally filtered by status.
    
    Args:
        status: Optional status filter ('Pending', 'Approved', 'Rejected')
        
    Returns:
        List[LeaveRequest]: Leave requests
    """
    try:
        query = LeaveRequest.query
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(LeaveRequest.submitted_at.desc()).all()
    except Exception:
        return []


def get_leave_request_by_id(leave_id: int) -> Optional[LeaveRequest]:
    """
    Get leave request by ID.
    
    Args:
        leave_id: Leave request ID
        
    Returns:
        Optional[LeaveRequest]: Leave request or None
    """
    try:
        return LeaveRequest.query.get(leave_id)
    except Exception:
        return None


def update_leave_status(leave_id: int, status: str) -> tuple:
    """
    Update leave request status (approve or reject).
    
    Args:
        leave_id: Leave request ID
        status: New status ('Approved' or 'Rejected')
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        leave_request = LeaveRequest.query.get(leave_id)
        
        if not leave_request:
            return False, "Leave request not found"
        
        if status == 'Approved':
            leave_request.approve()
        elif status == 'Rejected':
            leave_request.reject()
        else:
            return False, "Invalid status"
        
        db.session.commit()
        return True, f"Leave request {status.lower()}"
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error updating leave status: {str(e)}"


# ==================== DASHBOARD STATISTICS ====================

def get_dashboard_stats() -> Dict:
    """
    Get statistics for the dashboard.
    
    Week 5 Concept: Dictionary to store and return data
    
    Returns:
        Dict: Dashboard statistics
    """
    try:
        stats = {
            'total_employees': Employee.query.filter_by(status='active').count(),
            'total_departments': Department.query.count(),
            'total_roles': Role.query.count(),
            'pending_leaves': LeaveRequest.query.filter_by(status='Pending').count(),
            'today_attendance': Attendance.query.filter_by(date=date.today()).count()
        }
        return stats
    except Exception:
        return {
            'total_employees': 0,
            'total_departments': 0,
            'total_roles': 0,
            'pending_leaves': 0,
            'today_attendance': 0
        }
