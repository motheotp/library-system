#!/bin/bash
# Test runner script for library system

echo "🧪 Running Library System Tests..."
echo "=================================="
echo ""

# Run all tests with coverage
pytest -v --cov=. --cov-report=term-missing --cov-report=html

echo ""
echo "=================================="
echo "📊 Test Summary Complete"
echo ""
echo "To view detailed coverage report, open: htmlcov/index.html"
