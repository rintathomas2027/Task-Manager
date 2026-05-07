@echo off
set MYSQL_BIN="C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"
set DB_NAME=task_manager_db
set DB_USER=root
set DB_PASS=ajce
set OUTPUT_FILE=db_backup.sql

echo Exporting database %DB_NAME% to %OUTPUT_FILE%...
%MYSQL_BIN% -u %DB_USER% -p%DB_PASS% %DB_NAME% > %OUTPUT_FILE%

if %ERRORLEVEL% EQU 0 (
    echo Export successful! File created: %OUTPUT_FILE%
) else (
    echo Export failed. Please check your MySQL settings.
)
pause
