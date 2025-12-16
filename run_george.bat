@echo off
echo ========================================
echo   WorkFlowX - Employee Management System
echo   Running with SQLite Database
echo ========================================
echo.

REM Set environment variable to use SQLite
set USE_SQLITE=1

REM Run the Flask application
python main.py

pause
