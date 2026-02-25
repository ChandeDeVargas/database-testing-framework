#!/bin/bash

echo "================================================================"
echo "   DATABASE TESTING FRAMEWORK"
echo "   Comprehensive Database Test Suite with HTML Report"
echo "================================================================"
echo

# Check for virtual environment
if [ -f "venv/bin/python" ]; then
    echo "[INFO] Using virtual environment"
    PYTHON_CMD="venv/bin/python"
    PYTEST_CMD="venv/bin/pytest"
else
    echo "[WARNING] Virtual environment not found, using global Python"
    PYTHON_CMD="python3"
    PYTEST_CMD="pytest"
fi

# Set UTF-8 encoding
export PYTHONIOENCODING=utf-8

# Create reports directory
mkdir -p reports

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Set report filename
REPORT_FILE="reports/database_test_report_${TIMESTAMP}.html"

echo
echo "[INFO] Starting database tests..."
echo "[INFO] Report will be saved to: ${REPORT_FILE}"
echo

# Run all tests with HTML report
$PYTEST_CMD tests/ \
    --html=$REPORT_FILE \
    --self-contained-html \
    -v \
    --tb=short

echo
echo "================================================================"
echo "   TEST EXECUTION COMPLETE"
echo "================================================================"
echo
echo "Report generated: ${REPORT_FILE}"
echo
echo "To view the report:"
echo "  Open the HTML file in your browser"
echo
echo "Or run: open ${REPORT_FILE}"  # macOS
echo "Or run: xdg-open ${REPORT_FILE}"  # Linux
echo

# Make script executable
chmod +x run_all_tests.sh