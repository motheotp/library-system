# Library System Test Guide

## Prerequisites
Make sure you're in the correct directory:
```bash
cd /Users/aashishmaharjan/projects/library-system/arch1_layered
```

## Running Tests

### Option 1: Run all tests
```bash
python3 -m pytest -v
```

### Option 2: Run specific test file
```bash
python3 -m pytest test_user_management.py -v
python3 -m pytest test_book_management.py -v
python3 -m pytest test_borrowing_system.py -v
python3 -m pytest test_reservation_system.py -v
python3 -m pytest test_statistics_health.py -v
python3 -m pytest test_services.py -v
```

### Option 3: Run a specific test
```bash
python3 -m pytest test_user_management.py::TestUserManagement::test_register_user_success -v
```

### Option 4: Run with coverage
```bash
python3 -m pytest --cov=. --cov-report=html
```

## Test Files Created

1. **conftest.py** - Test configuration and fixtures
2. **test_user_management.py** - User registration, login, get user tests
3. **test_book_management.py** - Book listing, search, pagination tests
4. **test_borrowing_system.py** - Borrow, return, overdue, fines tests
5. **test_reservation_system.py** - Reservation creation and priority queue tests
6. **test_statistics_health.py** - System statistics and health check tests
7. **test_services.py** - Service layer business logic tests

## Current Test Status

- **Total Tests**: 122
- **Passing**: 114 (93.4%)
- **Failing**: 8 (minor bugs in services.py)

## Known Issues to Fix

1. **services.py line 161** - Indentation issue in search_books
2. Minor assertion text mismatches
3. Date parsing edge cases

## Troubleshooting

### If tests won't run:
```bash
# Check you're in the right directory
pwd

# Should output: /Users/aashishmaharjan/projects/library-system/arch1_layered

# Check Python version
python3 --version

# Check pytest is installed
python3 -m pytest --version

# Install dependencies if needed
pip3 install -r requirements.txt
```

### If you get import errors:
Make sure you're running from the arch1_layered directory where all the files are located.

### Quick smoke test:
```bash
python3 -m pytest test_user_management.py::TestUserManagement::test_register_user_success -v
```

This should pass and confirm everything is working.
