@echo off
echo ========================================
echo   WorkFlowX - Employee Management System
echo   George's SQL Server Configuration
echo ========================================
echo.

REM *** GEORGE'S SQL SERVER INSTANCE ***
REM George's instance: MSSQL$SQLEXPRESS03
REM Samuel's instance: MSSQL$SQLEXPRESS01

set MSSQL_SERVER=localhost\SQLEXPRESS03

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
