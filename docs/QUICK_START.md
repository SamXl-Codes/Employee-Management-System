# Quick Start Guide
**WorkFlowX Employee Management System**

Samuel Ogunlusi (20086108) & George M. Sherman (20079442)

---

## Getting It Running (5 Minutes)

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```

Or if you prefer installing individually:
```powershell
pip install Flask==3.0.0 Flask-SQLAlchemy==3.1.1 email-validator==2.1.0 Werkzeug==3.0.1
```

### Step 2: Create the Database
```powershell
python init_data.py
```

This creates the SQLite database file and loads sample data (departments, roles, 50 employees, attendance records). Also creates test accounts:
- **Admin:** admin / admin123
- **Employee:** employee1 / emp123

### Step 3: Start the App
```powershell
python main.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

### Step 4: Open Browser
Go to **http://localhost:5000** and log in with admin/admin123

---

## What to Test

Once logged in as admin, try these:

1. **Dashboard** - See overall statistics (employees, departments, pending leaves)
2. **Employees Page** - View list, search, add/edit/delete employees
3. **Attendance** - Record daily attendance, view percentages
4. **Leave Requests** - See pending requests, approve/reject them
5. **Reports** - Generate attendance/leave summaries, export to CSV/JSON
6. **Audit Logs** - Check who did what and when

You can also log out and log in as `employee1`/`emp123` to see the employee view (limited access).

---

## Running Tests

To run all tests:
```powershell
python run_tests.py
```

To run specific test modules:
```powershell
python run_tests.py models
python run_tests.py utils
python run_tests.py repository
python run_tests.py integration
```

All 45+ tests should pass.

---

## Troubleshooting

**"Module not found" error:**
```powershell
pip install -r requirements.txt
```

**Port 5000 already in use:**
Edit `main.py` and change the port:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

**Database issues:**
Delete `workflowx.db` and run `python init_data.py` again to start fresh.

**Tests failing:**
Make sure the database is initialized first (`python init_data.py`).

---

## Project Structure

Key files to review:
- `models.py` - Database models (OOP, relationships)
- `routes.py` - All the Flask routes and business logic
- `repository.py` - Data access layer
- `utils.py` - Validation functions
- `tests/` - Unit and integration tests
- `templates/` - HTML templates (Jinja2)
- `static/css/` - Stylesheet

---

## Default Data

The init script creates:

**Departments:** Engineering, HR, Sales, Marketing, Finance

**Roles:** Software Engineer, Senior Engineer, Manager, HR Specialist, Sales Rep, etc.

**Users:**
- admin / admin123 (Admin role)
- employee1 / emp123 (Employee role)

**Sample Employees:** 50 employees with realistic names, emails, salaries

**Attendance Records:** 200+ records across different dates/statuses

---

## CA-2 Requirements Verification

✅ **SQLite Database:** Check - `workflowx.db` created  
✅ **Unit Tests:** Check - 30+ tests in `tests/test_models.py`, `tests/test_utils.py`  
✅ **Integration Tests:** Check - 15+ tests in `tests/test_integration.py`  
✅ **REST API:** Check - `/api/employees` and `/api/stats` endpoints  
✅ **Security:** Check - Password hashing, SQL injection prevention, XSS protection  
✅ **Week 1-9 Concepts:** Check - Comments throughout code

---

## For Video Demonstration

Good things to show:
1. Login process
2. Dashboard overview
3. Adding a new employee
4. Recording attendance
5. Submitting and approving a leave request
6. Running reports and exporting data
7. Code walkthrough (models, routes, tests)
8. Test execution

---

**That's it! The app should be fully functional.**

If you run into any issues, check the README.md for more detailed documentation or refer to ARCHITECTURE.md for technical details about how everything is structured.
