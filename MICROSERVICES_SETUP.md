# Architecture 2: Microservices Setup Guide

Complete guide to run the Library Management System using the microservices architecture with gRPC and HTTP communication.

## Quick Start

### 1. Start All Services (One Command)

```bash
cd arch2_microservices
docker-compose up --build
```

This will:
- Start 3 PostgreSQL databases (user_db, book_db, borrowing_db)
- Start 3 microservices (user_service, book_service, borrowing_service)
- Start the HTTP gateway (gateway_service)
- Start the web frontend (Nginx)
- All services communicate via a shared Docker network

### 2. That's It!

Everything runs in Docker containers. No additional setup needed.

## Access the Application

### Frontend
- **URL**: http://localhost:3000
- Web-based interface for the library system

### Gateway API (HTTP/REST)
- **URL**: http://localhost:8080
- **Health Check**: http://localhost:8080/health

### Individual Services (gRPC - Internal Only)
- **User Service**: localhost:50051 (internal only)
- **Book Service**: localhost:50053 (internal only)
- **Borrowing Service**: localhost:50055 (internal only)

## Architecture Overview

```
┌──────────────────────────────┐
│     React Frontend           │
│     (Nginx - Port 3000)      │
└──────────────┬───────────────┘
               │ HTTP/REST
┌──────────────▼───────────────────────────┐
│      Gateway Service (Flask)             │
│      (Port 8000)                         │
│   (Translates HTTP ↔ gRPC)               │
└──┬─────────────────┬─────────────────┬───┘
   │ gRPC            │ gRPC            │ gRPC
   │ Port 50051      │ Port 50053      │ Port 50055
   │                 │                 │
┌──▼──────────┐  ┌───▼─────────┐  ┌───▼──────────┐
│ User        │  │ Book        │  │ Borrowing    │
│ Service     │  │ Service     │  │ Service      │
└──┬──────────┘  └───┬─────────┘  └───┬──────────┘
   │                 │                 │
┌──▼──────────┐  ┌───▼─────────┐  ┌───▼──────────┐
│ user_db     │  │ book_db     │  │ borrowing_db │
│ PostgreSQL  │  │ PostgreSQL  │  │ PostgreSQL   │
└─────────────┘  └─────────────┘  └─────────────┘
```

## Features to Test

### Browse Books
- Visit http://localhost:3000
- View all books in the catalog
- Use category filters
- Search by title or author

### Create User
```bash
curl -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123",
    "user_type": "student"
  }'
```

### Get Books
```bash
curl http://localhost:8080/books
```

### Borrow Book
```bash
curl -X POST http://localhost:8080/borrowings \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "1",
    "book_id": "1"
  }'
```

### Return Book
```bash
curl -X POST http://localhost:8080/borrowings/1/return
```

### View User Borrowings
```bash
curl http://localhost:8080/users/1/borrowings
```

## API Endpoints

### Users
- `POST /users` - Create user
- `GET /users` - List all users
- `GET /users/<user_id>` - Get user details

### Books
- `POST /books` - Add book
- `GET /books` - List all books
- `GET /books/<book_id>` - Get book details
- `PATCH /books/<book_id>/status` - Update book status

### Borrowings
- `POST /borrowings` - Borrow book
- `GET /users/<user_id>/borrowings` - Get user's borrowings
- `POST /borrowings/<borrow_id>/return` - Return book

## Docker Compose Services

All services run in containers within the `library_network`:

### Databases
- `user_db` - User service database (port 5432)
- `book_db` - Book service database (port 5432)
- `borrowing_db` - Borrowing service database (port 5432)

### Microservices
- `user_service` - User microservice (port 50051, gRPC)
- `book_service` - Book microservice (port 50053, gRPC)
- `borrowing_service` - Borrowing microservice (port 50055, gRPC)

### API Gateway
- `gateway_service` - HTTP gateway (port 8080, REST)

### Frontend
- `frontend` - Nginx serving React app (port 3000)

## Stopping and Restarting

### Stop All Services
```bash
docker-compose down
```

### Stop and Remove Data
```bash
docker-compose down -v
```

### View Logs
```bash
docker-compose logs -f
```

### View Specific Service Logs
```bash
docker-compose logs -f user_service
docker-compose logs -f gateway_service
docker-compose logs -f frontend
```

### Restart a Service
```bash
docker-compose restart user_service
```

## Database Access

### Access PostgreSQL directly
```bash
# User database
docker-compose exec user_db psql -U user_service_user -d user_service_db

# Book database
docker-compose exec book_db psql -U book_service_user -d book_service_db

# Borrowing database
docker-compose exec borrowing_db psql -U borrowing_service_user -d borrowing_service_db
```

### Example SQL queries
```sql
-- View all users
SELECT * FROM users;

-- View all books
SELECT * FROM books;

-- View all borrowings
SELECT * FROM borrowings;
```

## Performance Testing

### Run Load Tests
```bash
python tests/load_test.py
```

This runs three test scenarios:
- **Low Load**: 5 concurrent workers, 20 requests each
- **Medium Load**: 10 concurrent workers, 50 requests each
- **High Load**: 25 concurrent workers, 100 requests each

Results include:
- Throughput (requests per second)
- Latency (average, min, max, P95)
- Success/failure rates

### Manual API Testing with curl
```bash
# Health check
curl http://localhost:8080/health

# Test throughput
for i in {1..100}; do
  curl -X GET http://localhost:8080/books > /dev/null
done
```

## Troubleshooting

### Services won't start
```bash
# Check if ports are available
lsof -i :8080
lsof -i :50051
lsof -i :3000

# Clean up Docker
docker system prune -a --volumes
docker-compose up --build
```

### Frontend can't connect to gateway
1. Verify gateway is running: `curl http://localhost:8000/health`
2. Check browser console (F12) for network errors
3. Verify frontend API base URL is set to `http://localhost:8000`

### Database connection errors
```bash
# Check logs
docker-compose logs user_service
docker-compose logs book_service
docker-compose logs borrowing_service

# Verify database is running
docker-compose logs user_db
```

### Port already in use
```bash
# Kill process using port
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9

# Or restart Docker
docker-compose restart
```

## Architecture Advantages

- **Scalability**: Each service can be scaled independently
- **Fault Isolation**: Service failures don't cascade
- **Technology Flexibility**: Different services can use different technologies
- **Parallel Development**: Teams can work on different services independently
- **Performance**: gRPC provides low-latency inter-service communication
- **Accessibility**: HTTP gateway provides REST API for external clients

## Communication Models

### Internal (gRPC)
- Binary protocol using Protocol Buffers
- HTTP/2 multiplexing
- Low latency (~2-3ms)
- Type-safe contracts via .proto files
- Used for microservice-to-microservice communication

### External (HTTP/REST)
- JSON format
- Universal compatibility
- Easier debugging
- Accessible from any HTTP client
- Used by frontend and external clients

## Development

### Adding New Features

1. **Add API endpoint** to gateway service (gateway_service/src/gateway_server.py)
2. **Implement service logic** in respective microservice
3. **Test with curl** before updating frontend

### Rebuilding Services
```bash
# Rebuild all
docker-compose up --build

# Rebuild specific service
docker-compose up --build user_service
```

### Viewing Real-time Logs
```bash
docker-compose logs -f gateway_service
```

## Production Considerations

- Use environment variables for configuration
- Implement proper error handling and logging
- Add authentication and authorization
- Implement service discovery
- Add monitoring and alerting
- Use load balancing for horizontal scaling
- Implement circuit breakers for fault tolerance
- Add API rate limiting
- Enable CORS properly for security

## Next Steps

1. Test different load scenarios
2. Monitor service performance
3. Compare with layered architecture
4. Implement additional features
5. Deploy to cloud infrastructure
6. Set up monitoring and logging
7. Implement CI/CD pipeline

## File Structure

```
arch2_microservices/
├── docker-compose.yml          # Orchestrates all services
├── user_service/               # User microservice
│   ├── Dockerfile.user
│   └── src/
├── book_service/               # Book microservice
│   ├── Dockerfile.book
│   └── src/
├── borrowing_service/          # Borrowing microservice
│   ├── Dockerfile.borrowing
│   └── src/
├── gateway_service/            # HTTP gateway
│   ├── Dockerfile.gateway
│   └── src/
├── frontend/                   # React frontend
│   └── index.html
├── protos/                     # gRPC protocol definitions
│   ├── user.proto
│   ├── book.proto
│   └── borrowing.proto
└── tests/                      # Performance tests
    └── load_test.py
```

## Need Help?

- Check Docker logs: `docker-compose logs`
- Verify services are healthy: `docker-compose ps`
- Test gateway health: `curl http://localhost:8080/health`
- Review gateway logs: `docker-compose logs gateway_service`
- Check individual service logs: `docker-compose logs user_service`
