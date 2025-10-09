# Library System

Distributed Library Management System — two architectures (microservices + layered monolith).

## Overview

This project demonstrates two approaches to building a distributed library management system:

1. **Layered Monolith** (`arch1_layered/`):  
   A traditional Flask application using a layered architecture (models, services, routes) with PostgreSQL and Redis for caching.

2. **Microservices** (`arch2_microservices/`):  
   A microservices-based architecture (WIP) with separate services for books, users, borrowing, and a gateway.

## Features

- User registration and authentication
- Book catalog with search and filtering
- Borrowing and returning books (with overdue and fine calculation)
- Book reservation system
- System statistics and admin endpoints
- Caching with Redis for performance
- Dockerized for easy deployment

## Project Structure

```
library-system/
│
├── arch1_layered/           # Layered monolith Flask app
│   ├── app.py               # Application factory and entrypoint
│   ├── models.py            # SQLAlchemy models (User, Book, Borrowing, Reservation)
│   ├── services.py          # Business logic and caching
│   ├── routes.py            # API endpoints (Flask Blueprints)
│   ├── config.py            # Configuration (env, DB, Redis, etc.)
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Docker build for monolith
│
├── arch2_microservices/     # Microservices (WIP)
│   ├── book_service/
│   ├── borrowing_service/
│   ├── user_service/
│   ├── gateway_service/
│   └── docker/
│
├── docker-compose/
│   └── layered.yaml         # Compose file for layered monolith stack
│
└── README.md                # Project overview (this file)
```

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.9+ (for local development)
- PostgreSQL (if running outside Docker)
- Redis (for caching)

### Running the Layered Monolith (Recommended)

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/library-system.git
   cd library-system
   ```

2. **Start with Docker Compose:**
   ```sh
   cd docker-compose
   docker-compose -f layered.yaml up --build
   ```

   This will start:
   - PostgreSQL database
   - Redis (if configured)
   - Flask backend (on port 5000)
   - (Optional) Frontend (on port 8080, if implemented)

3. **API Endpoints:**
   - Base URL: `http://localhost:5000/api`
   - Health Check: `GET /api/health`
   - User Registration: `POST /api/users/register`
   - Book List: `GET /api/books`
   - Borrow Book: `POST /api/borrow`
   - Return Book: `POST /api/return/<borrowing_id>`
   - Admin Stats: `GET /api/admin/stats`

4. **Sample Data:**  
   On first run, the app seeds the database with sample users and books.

### Environment Variables

Set these in a `.env` file or your environment:

- `DATABASE_URL` (e.g., `postgresql://postgres:postgres@db:5432/library`)
- `SECRET_KEY`
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB` (optional, for caching)

### Running Tests

```sh
cd arch1_layered
pytest
```

## Microservices Architecture

The `arch2_microservices/` directory is a work in progress and will contain separate services for each domain (books, users, borrowing, etc.), each with its own API and database.

## Contributing

Contributions are welcome! Please open issues or submit pull requests.

## License

MIT License
