# Quick Setup Guide for George Sherman

## Problem: MS SQL Server Not Installed
Your computer doesn't have MS SQL Server like Samuel's machine. **Solution: Use SQLite instead!**

---

## **OPTION 1: Use SQLite (RECOMMENDED - Fastest)**

### Step 1: Set Environment Variable Before Running
```powershell
# In PowerShell, run this BEFORE python main.py:
$env:USE_SQLITE = "1"
python main.py
```

### Step 2: Run Application
```powershell
python main.py
```

Application will run on: **http://127.0.0.1:8080**

### To Always Use SQLite (Permanent)
```powershell
# Set environment variable permanently (Run PowerShell as Administrator)
[System.Environment]::SetEnvironmentVariable('USE_SQLITE', '1', 'User')

# Restart PowerShell, then:
python main.py
```

---

## **OPTION 2: Create a Batch File (EASIEST)**

### Create `run_george.bat` in project folder:
```batch
@echo off
echo Starting WorkFlowX with SQLite...
set USE_SQLITE=1
python main.py
pause
```

### Then just double-click `run_george.bat` to start the app!

---

## **OPTION 3: Install MS SQL Server (NOT RECOMMENDED - Takes 2+ hours)**

Only do this if you really want SQL Server:
1. Download SQL Server Express: https://www.microsoft.com/en-us/sql-server/sql-server-downloads
2. Install with default settings
3. Note the instance name during installation
4. Update app.py with your instance name

**This is overkill - use SQLite instead!**

---

## **Verifying Setup**

### Check if SQLite is working:
```powershell
# Set environment variable
$env:USE_SQLITE = "1"

# Run the app
python main.py

# You should see:
# * Running on http://127.0.0.1:8080
# No errors!
```

### Open browser:
```
http://127.0.0.1:8080
```

### Login with:
```
Email: admin@workflowx.com
Password: Admin@123
```

---

## **Why This Error Happened**

The app tries to connect to Samuel's SQL Server:
```
MSSQL_SERVER = 'localhost\\SQLEXPRESS01'
```

This doesn't exist on your computer! Setting `USE_SQLITE=1` tells the app to use SQLite instead.

---

## **Quick Commands for George**

```powershell
# Navigate to project
cd "C:\Users\gsherman\Desktop\Employee-Management System (Backend)\Employee-Management-System"

# Set SQLite mode
$env:USE_SQLITE = "1"

# Install dependencies (if needed)
pip install -r requirements.txt

# Run the app
python main.py

# Open in browser
start http://127.0.0.1:8080
```

---

## **Benefits of SQLite for George:**
✅ No installation needed
✅ Instant setup
✅ Works exactly like SQL Server for development
✅ All features work the same
✅ Can still test and develop everything
✅ Database stored as `workflowx.db` file in project folder

---

## **For Testing:**
```powershell
# Tests already use SQLite automatically
pytest

# Or
python -m pytest tests/
```

---

## **Need Help?**
Contact Samuel if you still get errors!
