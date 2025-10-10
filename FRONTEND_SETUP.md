# Frontend Setup Guide

Complete guide to run the Library Management System with the new React frontend.

## Quick Start

### 1. Start Infrastructure (PostgreSQL, Redis, pgAdmin)

```bash
cd infrastructure
docker-compose -f docker-compose.infrastructure.yml down -v
docker-compose -f docker-compose.infrastructure.yml up -d
```

This will:
- Start PostgreSQL on port 5432
- Start Redis on port 6379
- Start pgAdmin on port 5050
- Initialize the database with sample data (users and books)

### 2. Start Backend (Flask API)

```bash
cd arch1_layered
python3 app.py
```

The backend will be available at `http://localhost:5000`

### 3. Start Frontend (React)

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Access the Application

### Frontend
- **URL**: http://localhost:3000
- **Sample Login**: Use student ID `STU001`, `STU002`, etc.
- **Librarian Login**: Use student ID `LIB001`

### Backend API
- **URL**: http://localhost:5000/api
- **Health Check**: http://localhost:5000/api/health

### pgAdmin (Database Manager)
- **URL**: http://localhost:5050
- **Email**: admin@example.com
- **Password**: admin123

### Redis
- **Host**: localhost
- **Port**: 6379

## Sample Users

The database is initialized with these users:

### Students
- **STU001** - John Student (john@university.edu)
- **STU002** - Jane Learner (jane@university.edu)
- **STU003** - Bob Reader (bob@university.edu)
- **STU004** - Alice Scholar (alice@university.edu)

### Librarian
- **LIB001** - Library Admin (admin@library.edu)

## Features to Test

### As a Student

1. **Browse Books**
   - Visit homepage to see all books
   - Use category filters (Programming, Web Development, etc.)
   - Search by title or author

2. **Borrow Books**
   - Login with student ID (e.g., STU001)
   - Click "Borrow Book" on any available book
   - Maximum 3 books at a time

3. **View Dashboard**
   - Click "My Books" in navigation
   - See all currently borrowed books
   - View due dates and days remaining

4. **Return Books**
   - From dashboard, click "Return Book"
   - If overdue, fine amount will be displayed

### As a Librarian

1. **Admin Dashboard**
   - Login with LIB001
   - Click "Admin" in navigation
   - View system statistics:
     - Total books, users, borrowings
     - Active vs available breakdown

2. **Monitor Overdue Books**
   - See list of all overdue books
   - View borrower details
   - Email contact links for each borrower

## Architecture Overview

```
┌─────────────┐      ┌─────────────┐      ┌──────────────┐
│   React     │─────▶│   Flask     │─────▶│  PostgreSQL  │
│  Frontend   │◀─────│   Backend   │◀─────│   Database   │
│  Port 3000  │      │  Port 5000  │      │  Port 5432   │
└─────────────┘      └─────────────┘      └──────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │    Redis    │
                     │   Cache     │
                     │  Port 6379  │
                     └─────────────┘
```

## Troubleshooting

### Frontend cannot connect to backend

**Error**: `Network Error` or `ERR_CONNECTION_REFUSED`

**Solution**:
1. Check if backend is running: `curl http://localhost:5000/api/health`
2. Verify CORS is enabled in Flask app (already configured in app.py)
3. Check if proxy is configured in vite.config.js

### Database is empty

**Solution**:
```bash
cd infrastructure
docker-compose -f docker-compose.infrastructure.yml down -v
docker-compose -f docker-compose.infrastructure.yml up -d
```

The `-v` flag removes volumes, forcing re-initialization with sample data.

### Redis connection error

**Error**: `Redis cache not available`

**Solution**:
1. Check if Redis container is running: `docker ps`
2. Test connection: `redis-cli -h localhost -p 6379 ping`
3. Backend will work without Redis (caching disabled)

### Port already in use

**Frontend Error**: `Port 3000 is already in use`

**Solution**:
```bash
# Find process using port 3000
lsof -ti:3000 | xargs kill -9

# Or change port in vite.config.js
```

**Backend Error**: `Port 5000 is already in use`

**Solution**:
```bash
# Find and kill process
lsof -ti:5000 | xargs kill -9
```

### Books not showing up

1. Check backend logs for errors
2. Verify database connection:
   - Open pgAdmin (localhost:5050)
   - Connect to library database
   - Run: `SELECT * FROM books;`
3. Check browser console for API errors

## Development Workflow

### Making Changes to Frontend

1. Edit files in `frontend/src/`
2. Changes auto-reload with Hot Module Replacement
3. Check browser console for errors
4. Test API calls in Network tab

### Making Changes to Backend

1. Edit files in `arch1_layered/`
2. Flask auto-reloads in debug mode
3. Check terminal for errors
4. Test endpoints with curl or Postman

### Database Changes

1. Modify SQL files in `infrastructure/init-db/`
2. Recreate containers:
   ```bash
   docker-compose -f docker-compose.infrastructure.yml down -v
   docker-compose -f docker-compose.infrastructure.yml up -d
   ```

## Testing the System

### Test Borrowing Flow

1. Login as STU001
2. Borrow "Python Programming"
3. Go to Dashboard - verify book appears
4. Return the book
5. Verify book is available again in catalog

### Test Overdue Books

1. Manually update a borrowing due_date in database to past date
2. Login as LIB001
3. Check Admin dashboard - overdue book should appear
4. Login as the borrowing user
5. Dashboard shows overdue warning
6. Return book - fine is calculated

### Test Borrowing Limit

1. Login as a student
2. Borrow 3 books (maximum)
3. Try to borrow 4th book
4. Should see error: "Borrowing limit reached"
5. Return one book
6. Now can borrow another

## API Testing with curl

```bash
# Health check
curl http://localhost:5000/api/health

# Get all books
curl http://localhost:5000/api/books

# Search books
curl "http://localhost:5000/api/books/search?q=python"

# Login
curl -X POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"student_id": "STU001"}'

# Borrow book
curl -X POST http://localhost:5000/api/borrow \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "book_id": 1}'

# Get statistics
curl http://localhost:5000/api/admin/stats
```

## Production Deployment

### Build Frontend

```bash
cd frontend
npm run build
```

Output will be in `frontend/dist/`

### Deploy Options

1. **Static Hosting** (Netlify, Vercel, GitHub Pages)
   - Deploy `frontend/dist/` folder
   - Configure API URL environment variable

2. **Docker** (Full Stack)
   - Create Dockerfile for frontend (serve dist/)
   - Create Dockerfile for backend
   - Use docker-compose to orchestrate all services

3. **Cloud Platforms** (AWS, GCP, Azure)
   - Frontend: S3 + CloudFront / Cloud Storage + CDN
   - Backend: EC2 / Cloud Run / App Service
   - Database: RDS / Cloud SQL / Azure Database

## Next Steps

1. **Implement Reservations**: Add UI for book reservations
2. **Popular Books**: Create homepage section for trending books
3. **User Profiles**: Add profile editing functionality
4. **Email Notifications**: Send reminders for due dates
5. **Search Enhancements**: Add filters for year, ISBN, etc.
6. **Analytics**: Add charts for borrowing trends
7. **Book Reviews**: Let users rate and review books
8. **Fine Payments**: Integrate payment gateway for fines

## Need Help?

- Check browser console for frontend errors
- Check terminal for backend errors
- Check Docker logs: `docker logs library_postgres`
- Review API responses in Network tab
- Test API endpoints with Postman or curl
