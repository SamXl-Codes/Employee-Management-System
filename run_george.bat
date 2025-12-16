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

REM Database name
set MSSQL_DATABASE=workflowx

REM *** USE WINDOWS AUTHENTICATION (No username/password needed) ***
set USE_WINDOWS_AUTH=1

REM If you want to use SQL Authentication instead, comment out the line above
REM and uncomment these:
REM set MSSQL_USERNAME=workflowx_admin
REM set MSSQL_PASSWORD=WorkFlowDB@2025

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
