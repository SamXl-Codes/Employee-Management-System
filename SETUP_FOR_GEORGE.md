# Quick Setup Guide for George Sherman

## Problem: SQL Server Connection Error
Your SQL Server instance name is different from Samuel's. **Solution: Configure your SQL Server instance!**

---

## **STEP 1: Find Your SQL Server Instance Name**

### Method 1: Using PowerShell
```powershell
# Run this command to see all SQL Server instances on your computer
Get-Service -Name "MSSQL*" | Select-Object Name, DisplayName, Status

# Common instance names:
# - MSSQLSERVER (default instance) → Use: localhost
# - MSSQL$SQLEXPRESS → Use: localhost\SQLEXPRESS
# - MSSQL$EXPRESS → Use: localhost\EXPRESS
# - MSSQL$SQLEXPRESS01 → Use: localhost\SQLEXPRESS01
```

### Method 2: Using SQL Server Management Studio (SSMS)
```
1. Open SSMS
2. Look at "Server name" dropdown when connecting
3. Your instance name is shown there
4. Copy it exactly as shown
```

### Method 3: Using Command Prompt
```cmd
sqlcmd -L
```
This lists all SQL Server instances on your network.

---

## **STEP 2: Create Batch File with YOUR Instance Name**

### Edit `run_george.bat` in project folder:
```batch
@echo off
echo ========================================
echo   WorkFlowX - Employee Management System
echo   George's SQL Server Configuration
echo ========================================
echo.

REM *** CHANGE THIS TO YOUR SQL SERVER INSTANCE NAME ***
set MSSQL_SERVER=localhost\SQLEXPRESS

REM Database credentials (same as Samuel's)
set MSSQL_DATABASE=workflowx
set MSSQL_USERNAME=workflowx_admin
set MSSQL_PASSWORD=WorkFlowDB@2025

echo Connecting to SQL Server: %MSSQL_SERVER%
echo Database: %MSSQL_DATABASE%
echo.

REM Run the Flask application
python main.py

pause
```

### **IMPORTANT:** Change `localhost\SQLEXPRESS` to YOUR instance name!

### Common Instance Names:
- **Default instance:** `localhost` (no backslash)
- **Named instance:** `localhost\SQLEXPRESS` or `localhost\EXPRESS`
- **Samuel's instance:** `localhost\SQLEXPRESS01`

---

## **STEP 3: Double-Click `run_george.bat` to Start**

Just double-click the batch file and it will:
1. Set your SQL Server instance name
2. Connect to the database
3. Start the application on http://127.0.0.1:8080

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
