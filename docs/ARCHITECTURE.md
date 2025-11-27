# WorkFlowX - System Architecture & UML Diagrams

**Team:** Samuel Ogunlusi (20086108) & George M. Sherman (20079442)  
**Date:** November 2024

---

## 1. Architecture Overview - MVC Pattern

We built WorkFlowX using the MVC (Model-View-Controller) pattern because it's what Flask naturally supports and it keeps our code organized. Here's how it breaks down:

**Why MVC?**
- Keeps presentation, logic, and data separate (easier to debug when things go wrong)
- We can test each part independently
- Changes to the UI don't break backend logic
- Both of us could work on different parts without conflicts

### Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                    │
│         (templates/*.html - Jinja2 Templates)           │
│                                                          │
│  • User Interface Components                            │
│  • HTML Forms                                            │
│  • Data Display Tables                                   │
│  • Client-side Validation                               │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│                    CONTROLLER LAYER                      │
│              (routes.py - Flask Routes)                  │
│                                                          │
│  • HTTP Request Handling                                 │
│  • Input Validation                                      │
│  • Session Management                                    │
│  • Response Generation                                   │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                   │
│         (utils.py, repository.py - Services)            │
│                                                          │
│  • Data Validation (Regex, Business Rules)              │
│  • Business Calculations                                 │
│  • Transaction Management                                │
│  • Audit Logging                                         │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│                       DATA LAYER                         │
│        (models.py - SQLAlchemy ORM Models)              │
│                                                          │
│  • Database Schema Definition                            │
│  • CRUD Operations                                       │
│  • Relationships & Constraints                           │
│  • Data Integrity                                        │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                      │
│                (workflowx.db - SQLite)                   │
│                                                          │
│  • Persistent Data Storage                               │
│  • ACID Transactions                                     │
│  • Data Relationships                                    │
└─────────────────────────────────────────────────────────┘
```

---

## 2. UML DIAGRAMS

### 2.1 Use Case Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  WorkFlowX System                        │
│                                                          │
│  Admin                              Employee             │
│  ┌─┐                                ┌─┐                  │
│  │▪│                                │▪│                  │
│  └┬┘                                └┬┘                  │
│   │                                  │                   │
│   ├──► Manage Employees              │                   │
│   │    • Add Employee                │                   │
│   │    • Edit Employee               │                   │
│   │    • Delete Employee             │                   │
│   │    • Search Employee             │                   │
│   │                                  │                   │
│   ├──► Manage Departments           │                   │
│   │    • Add Department              │                   │
│   │    • Edit Department             │                   │
│   │    • Delete Department           │                   │
│   │                                  │                   │
│   ├──► Manage Roles                 │                   │
│   │    • Add Role                    │                   │
│   │    • Edit Role                   │                   │
│   │    • Delete Role                 │                   │
│   │                                  │                   │
│   ├──► Mark Attendance               │                   │
│   │    • Daily Attendance            │                   │
│   │    • Bulk Marking                │                   │
│   │                                  │                   │
│   ├──► Approve Leave Requests        │                   │
│   │    • Review Requests             │                   │
│   │    • Approve/Reject              ├───► View Profile  │
│   │    • Send Notifications          │                   │
│   │                                  │                   │
│   ├──► Generate Reports              ├───► View Attendance│
│   │    • Attendance Reports          │                   │
│   │    • Leave Reports               │                   │
│   │    • Payroll Reports             ├───► Request Leave │
│   │                                  │                   │
│   ├──► Export Data                   ├───► View Leave    │
│   │    • CSV Export                  │     History       │
│   │    • JSON Export                 │                   │
│   │                                  │                   │
│   ├──► View Audit Logs               │                   │
│   │                                  │                   │
│   └──► Import Employees (CSV)        │                   │
│        • Bulk Upload                 │                   │
│        • Validation                  │                   │
│                                      │                   │
└──────────────────────────────────────────────────────────┘
```

### 2.2 Class Diagram

```
┌────────────────────────┐       ┌────────────────────────┐
│       User             │       │      Department        │
├────────────────────────┤       ├────────────────────────┤
│ - user_id: int (PK)    │       │ - department_id: int   │
│ - username: str        │       │ - name: str            │
│ - password_hash: str   │       │ - description: str     │
│ - role: str            │       │ - created_at: datetime │
│ - created_at: datetime │       ├────────────────────────┤
├────────────────────────┤       │ + get_employee_count() │
│ + set_password()       │       │ + can_delete(): bool   │
│ + check_password()     │       │ + to_dict(): dict      │
│ + to_dict(): dict      │       └────────────────────────┘
└────────────────────────┘                 △
                                           │ 1
                                           │
         ┌────────────────────────┐        │
         │        Role            │        │ *
         ├────────────────────────┤   ┌────────────────────────┐
         │ - role_id: int (PK)    │   │      Employee          │
         │ - title: str           │   ├────────────────────────┤
         │ - description: str     │   │ - employee_id: int (PK)│
         │ - created_at: datetime │   │ - name: str            │
         ├────────────────────────┤   │ - email: str (unique)  │
         │ + get_employee_count() │   │ - phone: str           │
         │ + can_delete(): bool   │   │ - department_id: int   │◄──┐
         │ + to_dict(): dict      │   │ - role_id: int         │   │
         └────────────────────────┘   │ - salary: Decimal      │   │ *
                  △                   │ - date_joined: Date    │   │
                  │ 1                 │ - status: str          │   │
                  │                   ├────────────────────────┤   │
                  │ *                 │ + get_attendance_%()   │   │
         ┌────────────────────────┐   │ + get_total_leave_days()  │
         │     Attendance         │   │ + is_active(): bool    │   │
         ├────────────────────────┤   │ + activate()           │   │
         │ - attendance_id: int   │   │ + deactivate()         │   │
         │ - employee_id: int (FK)├───┤ + to_dict(): dict      │   │
         │ - date: Date           │   └────────────────────────┘   │
         │ - status: str          │                                │
         │ - notes: str           │                                │
         │ - created_at: datetime │   ┌────────────────────────┐   │
         ├────────────────────────┤   │    LeaveRequest        │   │
         │ + to_dict(): dict      │   ├────────────────────────┤   │
         └────────────────────────┘   │ - leave_id: int (PK)   │   │
                                      │ - employee_id: int (FK)├───┘
                                      │ - start_date: Date     │
                                      │ - end_date: Date       │
                                      │ - leave_type: str      │
                                      │ - reason: str          │
                                      │ - status: str          │
                                      │ - submitted_at: DateTime│
                                      │ - reviewed_at: DateTime│
                                      ├────────────────────────┤
                                      │ + calculate_days(): int│
                                      │ + approve()            │
                                      │ + reject()             │
                                      │ + is_pending(): bool   │
                                      │ + to_dict(): dict      │
                                      └────────────────────────┘
```

### 2.3 Component Diagram

```
┌──────────────────────────────────────────────────────────┐
│                   WorkFlowX System                        │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │          Web Browser (Client)                   │    │
│  │  • HTML5                                         │    │
│  │  • CSS (Tailwind)                                │    │
│  │  • JavaScript (Chart.js)                         │    │
│  └─────────────────────────────────────────────────┘    │
│                        ↕ HTTP/HTTPS                      │
│  ┌─────────────────────────────────────────────────┐    │
│  │          Flask Application Server               │    │
│  │                                                  │    │
│  │  ┌─────────────────┐   ┌────────────────────┐  │    │
│  │  │   routes.py     │   │   Authentication   │  │    │
│  │  │  (Controllers)  │───│   Middleware       │  │    │
│  │  │                 │   │   • Login/Logout   │  │    │
│  │  │ • /login        │   │   • Session Mgmt   │  │    │
│  │  │ • /dashboard    │   │   • Authorization  │  │    │
│  │  │ • /employees    │   └────────────────────┘  │    │
│  │  │ • /departments  │                            │    │
│  │  │ • /attendance   │   ┌────────────────────┐  │    │
│  │  │ • /reports      │   │   Security Layer   │  │    │
│  │  │ • /api/*        │───│  • Password Hash   │  │    │
│  │  └─────────────────┘   │  • Input Valid.    │  │    │
│  │          ↕              │  • XSS Protection  │  │    │
│  │  ┌─────────────────┐   │  • CSRF Protection │  │    │
│  │  │   repository.py │   └────────────────────┘  │    │
│  │  │  (Data Access)  │                            │    │
│  │  │                 │   ┌────────────────────┐  │    │
│  │  │ • CRUD Ops      │   │     utils.py       │  │    │
│  │  │ • Transactions  │───│   (Utilities)      │  │    │
│  │  └─────────────────┘   │                    │  │    │
│  │          ↕              │ • Validation       │  │    │
│  │  ┌─────────────────┐   │ • Sanitization     │  │    │
│  │  │    models.py    │   │ • Date Parsing     │  │    │
│  │  │   (ORM Models)  │   │ • Currency Format  │  │    │
│  │  │                 │   └────────────────────┘  │    │
│  │  │ • User          │                            │    │
│  │  │ • Employee      │   ┌────────────────────┐  │    │
│  │  │ • Department    │   │  Template Engine   │  │    │
│  │  │ • Role          │───│     (Jinja2)       │  │    │
│  │  │ • Attendance    │   │                    │  │    │
│  │  │ • LeaveRequest  │   │ • Auto-escaping    │  │    │
│  │  │ • AuditLog      │   │ • Template Inherit │  │    │
│  │  └─────────────────┘   └────────────────────┘  │    │
│  │          ↕                                       │    │
│  │  ┌─────────────────────────────────────────┐   │    │
│  │  │     SQLAlchemy ORM Layer                │   │    │
│  │  │  • Query Builder                         │   │    │
│  │  │  • Connection Pooling                    │   │    │
│  │  │  • Transaction Management                │   │    │
│  │  └─────────────────────────────────────────┘   │    │
│  └──────────────────────────────────────────────────┘    │
│                        ↕                                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │         SQLite Database (workflowx.db)           │   │
│  │  • users                                          │   │
│  │  • employees                                      │   │
│  │  • departments                                    │   │
│  │  • roles                                          │   │
│  │  • attendance                                     │   │
│  │  • leave_requests                                 │   │
│  │  • audit_logs                                     │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### 2.4 Sequence Diagram - Employee Creation Flow

```
Admin        →    routes.py    →    utils.py    →  repository.py  →  models.py  →  Database
  │                  │                 │               │               │              │
  │──POST /add───────│                 │               │               │              │
  │ employee         │                 │               │               │              │
  │                  │                 │               │               │              │
  │                  │──validate_email()│              │               │              │
  │                  │◄────valid────────│              │               │              │
  │                  │                 │               │               │              │
  │                  │──validate_phone()│              │               │              │
  │                  │◄────valid────────│              │               │              │
  │                  │                 │               │               │              │
  │                  │──validate_salary()              │               │              │
  │                  │◄────valid────────│              │               │              │
  │                  │                                 │               │              │
  │                  │───create_employee()─────────────│               │              │
  │                  │                                 │               │              │
  │                  │                                 │──new Employee()│             │
  │                  │                                 │               │              │
  │                  │                                 │               │──INSERT──────│
  │                  │                                 │               │◄──success───│
  │                  │                                 │◄──employee────│              │
  │                  │◄────(True, msg, emp)────────────│               │              │
  │                  │                                 │               │              │
  │◄──redirect───────│                                 │               │              │
  │  /employees      │                                 │               │              │
```

---

## 3. DESIGN DECISIONS

### 3.1 Why Flask Framework?

**Pros:**
- Lightweight and easy to learn
- Flexible and unopinionated
- Excellent documentation
- Large ecosystem of extensions
- Perfect for small-to-medium projects like WorkFlowX

**Alternatives Considered:**
- Django: Too heavyweight for this project
- FastAPI: Overkill for CRUD operations
- Node.js/Express: Team expertise in Python

### 3.2 Why SQLite Database?

**CA-2 Requirement:** SQLite is mandated for this project

**Advantages:**
- **Zero Configuration**: No server setup required
- **Portable**: Single file database
- **Lightweight**: Perfect for development and testing
- **Built into Python**: No additional installation
- **ACID Compliant**: Reliable transactions

**Production Alternative:** PostgreSQL for multi-user concurrent access

### 3.3 Why Jinja2 Templating?

- **Server-side rendering**: SEO-friendly
- **Template inheritance**: DRY principle
- **Auto-escaping**: XSS protection built-in
- **Flask integration**: Native support
- **Python syntax**: Easy for Python developers

### 3.4 Why Repository Pattern?

- **Abstraction**: Hides database complexity
- **Testability**: Easy to mock for unit tests
- **Maintainability**: Database changes isolated
- **Reusability**: Functions used across routes

---

## 4. SECURITY ARCHITECTURE

### 4.1 Authentication Layer

```
User Login Request
      │
      ↓
[Validate Credentials]
      │
      ├─ Check username exists
      │
      ├─ Verify password hash (Werkzeug PBKDF2)
      │
      ├─ Create session
      │
      └─ Set secure cookies
            │
            ↓
      [Session Active]
```

### 4.2 Authorization Layers

1. **@login_required**: All protected routes
2. **@admin_required**: Admin-only routes
3. **Role-based checks**: Dynamic permission validation

### 4.3 Data Protection

- **Password Hashing**: Werkzeug PBKDF2 SHA-256
- **SQL Injection**: SQLAlchemy parameterized queries
- **XSS Prevention**: Jinja2 auto-escaping + input sanitization
- **CSRF Protection**: Flask session tokens
- **Session Security**: HTTPOnly, Secure, SameSite cookies

---

## 5. DATA FLOW ARCHITECTURE

### Request Processing Flow:

```
1. HTTP Request → Flask Router
                    ↓
2. Authentication Middleware Check
                    ↓
3. Route Handler (Controller)
                    ↓
4. Input Validation (utils.py)
                    ↓
5. Business Logic (repository.py)
                    ↓
6. Database Operation (models.py + SQLAlchemy)
                    ↓
7. Database (SQLite)
                    ↓
8. Response Generation (Jinja2 Template)
                    ↓
9. HTTP Response → Client Browser
```

---

## 6. SCALABILITY CONSIDERATIONS

### Current Architecture Supports:
- **Horizontal Scaling**: Add more Flask instances behind load balancer
- **Database Migration**: Easy switch from SQLite to PostgreSQL
- **API Integration**: REST endpoints already implemented
- **Caching Layer**: Redis can be added for session storage
- **Background Jobs**: Celery integration for async tasks

### Future Enhancements:
- Microservices architecture for large enterprises
- Message queue for notifications
- Distributed database for global access
- CDN for static assets

---

## 7. TECHNOLOGY JUSTIFICATION

| Technology | Purpose | Justification |
|-----------|---------|---------------|
| **Flask** | Web Framework | Lightweight, flexible, Python-native |
| **SQLAlchemy** | ORM | Abstraction, security, portability |
| **SQLite** | Database | CA-2 requirement, simple, portable |
| **Jinja2** | Templating | Flask integration, security |
| **Werkzeug** | Security | Industry-standard password hashing |
| **Tailwind CSS** | Styling | Modern, responsive, maintainable |
| **Chart.js** | Visualization | Interactive, lightweight charts |

---

**Document Version:** 1.0  
**Last Updated:** November 2024  
**CA-2 Submission: Advanced Programming Techniques**
