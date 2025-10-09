# Library Management System - Frontend

A modern React frontend for the Library Management System built with Vite.

## Features

### For Students
- **Browse Books**: View paginated catalog with search and category filters
- **Search Functionality**: Search books by title or author
- **Borrow Books**: Borrow available books with one click
- **Dashboard**: View currently borrowed books with due dates
- **Return Books**: Return borrowed books and view any fines
- **Overdue Warnings**: Clear indicators for overdue books

### For Librarians
- **Admin Dashboard**: View system statistics
  - Total books, users, borrowings, and reservations
  - Active vs. available books breakdown
- **Overdue Management**: Monitor all overdue books with borrower details
- **Contact Integration**: Email links for easy communication with borrowers

## Tech Stack

- **React 18** - UI library
- **React Router** - Client-side routing
- **Axios** - HTTP client for API requests
- **Vite** - Fast build tool and dev server
- **Context API** - State management for authentication

## Prerequisites

- Node.js 16+ and npm
- Backend API running on `http://localhost:5000`

## Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`

## Project Structure

```
frontend/
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── Navbar.jsx
│   │   └── Navbar.css
│   ├── context/          # React Context for state management
│   │   └── AuthContext.jsx
│   ├── pages/            # Page components
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Books.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Admin.jsx
│   │   └── *.css
│   ├── services/         # API service layer
│   │   └── api.js
│   ├── App.jsx           # Main app component with routing
│   └── main.jsx          # Entry point
├── .env                  # Environment variables
└── vite.config.js        # Vite configuration
```

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:5000/api
```

## Available Scripts

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## API Integration

The frontend communicates with the backend REST API through the following endpoints:

### User APIs
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - User login
- `GET /api/users/:id` - Get user details

### Book APIs
- `GET /api/books` - Get books (paginated, with filters)
- `GET /api/books/search?q=query` - Search books
- `GET /api/books/:id` - Get book details
- `GET /api/books/popular` - Get popular books

### Borrowing APIs
- `POST /api/borrow` - Borrow a book
- `POST /api/return/:id` - Return a book
- `GET /api/users/:id/borrowed` - Get user's borrowed books
- `GET /api/overdue` - Get all overdue books

### Admin APIs
- `GET /api/admin/stats` - Get system statistics

## Routes

- `/` - Books catalog (public)
- `/login` - User login
- `/register` - User registration
- `/dashboard` - User dashboard (protected)
- `/admin` - Admin dashboard (protected, librarian only)

## Authentication

The app uses a simple authentication system:
- Login with student ID
- User data stored in localStorage
- Context API for global auth state
- Protected routes redirect to login

## Features Highlight

### Real-time Updates
- Book availability updates after borrowing/returning
- Dashboard refreshes after returning books
- Admin statistics refresh

### Responsive Design
- Mobile-friendly layouts
- Adaptive grid systems
- Touch-friendly buttons

### User Experience
- Loading states for async operations
- Error messages with auto-dismiss
- Success confirmations
- Empty state handling

### Fine Calculation
- Automatic fine calculation for overdue books
- $1 per day overdue rate
- Displayed on book return

## Sample Users (from init-db)

### Students
- STU001 / John Student
- STU002 / Jane Learner
- STU003 / Bob Reader
- STU004 / Alice Scholar

### Librarian
- LIB001 / Library Admin

## Development Tips

1. **Hot Module Replacement**: Vite provides instant updates during development
2. **API Proxy**: Configured to proxy `/api` requests to backend
3. **Error Handling**: Check browser console for API errors
4. **State Management**: Auth state persists across page refreshes

## Troubleshooting

### Cannot connect to backend
- Ensure backend is running on `http://localhost:5000`
- Check CORS is enabled in Flask backend
- Verify `.env` file has correct API URL

### Login not working
- Check if user exists in database
- Verify backend is connected to PostgreSQL
- Check browser console for errors

### Books not loading
- Ensure database has been initialized with sample data
- Check backend `/api/health` endpoint
- Verify Redis is running for caching

## Building for Production

```bash
# Build optimized production bundle
npm run build

# Files will be in dist/ directory
# Deploy dist/ folder to your hosting service
```

## Future Enhancements

- [ ] Book reservation functionality
- [ ] Popular books section on home page
- [ ] User profile management
- [ ] Book reviews and ratings
- [ ] Advanced search filters
- [ ] Notification system for due dates
- [ ] Dark mode support
