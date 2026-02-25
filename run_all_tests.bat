@echo off
echo ================================================================
echo    DATABASE TESTING FRAMEWORK
echo    Comprehensive Database Test Suite with HTML Report
echo ================================================================
echo.

REM Check for virtual environment
if exist "venv\Scripts\python.exe" (
    echo [INFO] Using virtual environment
    set "PYTHON_CMD=venv\Scripts\python.exe"
    set "PYTEST_CMD=venv\Scripts\pytest.exe"
) else (
    echo [WARNING] Virtual environment not found, using global Python
    set "PYTHON_CMD=python"
    set "PYTEST_CMD=pytest"
)

REM Set UTF-8 encoding
set PYTHONIOENCODING=utf-8

REM Create reports directory
if not exist "reports" mkdir reports

REM Generate timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%

REM Set report filename
set REPORT_FILE=reports\database_test_report_%TIMESTAMP%.html

echo.
echo [INFO] Starting database tests...
echo [INFO] Report will be saved to: %REPORT_FILE%
echo.

REM Run all tests with HTML report
%PYTEST_CMD% tests/ ^
    --html=%REPORT_FILE% ^
    --self-contained-html ^
    -v ^
    --tb=short

echo.
echo ================================================================
echo    TEST EXECUTION COMPLETE
echo ================================================================
echo.
echo Report generated: %REPORT_FILE%
echo.
echo To view the report:
echo   1. Open File Explorer
echo   2. Navigate to the 'reports' folder
echo   3. Double-click the HTML file
echo.
echo Or run: start %REPORT_FILE%
echo.

REM Count test results
echo Test Summary:
%PYTEST_CMD% tests/ --collect-only -q | find /c "test session starts" > nul
echo.

pause