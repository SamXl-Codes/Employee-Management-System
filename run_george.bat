@echo off
echo ========================================
echo   WorkFlowX - Employee Management System
echo   George's SQL Server Configuration
echo ========================================
echo.

REM *** CHANGE THIS TO YOUR SQL SERVER INSTANCE NAME ***
REM Common values:
REM   - localhost              (for default instance)
REM   - localhost\SQLEXPRESS   (for SQL Express default)
REM   - localhost\EXPRESS      (alternative name)
REM   - localhost\SQLEXPRESS01 (Samuel's instance)

set MSSQL_SERVER=localhost\SQLEXPRESS

REM Database credentials (keep these the same)
set MSSQL_DATABASE=workflowx
set MSSQL_USERNAME=workflowx_admin
set MSSQL_PASSWORD=WorkFlowDB@2025

echo.
echo Connecting to SQL Server: %MSSQL_SERVER%
echo Database: %MSSQL_DATABASE%
echo Username: %MSSQL_USERNAME%
echo.
echo If connection fails, update MSSQL_SERVER in this file!
echo.

REM Run the Flask application
python main.py

pause
