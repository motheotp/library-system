# Library Management System

A comprehensive library management system demonstrating two different architectural patterns: **Layered Architecture** and **Microservices Architecture**.

This project showcases the same application built with two distinct approaches, allowing you to compare and understand the trade-offs between monolithic and distributed architectures.

## 🏗️ Architecture Implementations

### [Architecture 1: Layered (3-Tier)]
Traditional monolithic architecture with clear separation of concerns.

```
Frontend → Nginx Load Balancer → Backend Instances → PostgreSQL + Redis
```

**Best for**: Smaller teams, simpler deployments, lower operational complexity

---

### [Architecture 2: Microservices]
Distributed architecture with independent services communicating via gRPC.

```
Frontend → API Gateway → [User Service, Book Service, Borrowing Service] → Individual Databases
```

**Best for**: Large teams, independent scaling, service autonomy

---

## 🚀 Quick Start

### Prerequisites
- Docker (20.10+)
- Docker Compose (1.29+)
- 4-6GB available RAM
- Ports 3000 and 8080 available

### Choose Your Architecture

#### Option 1: Layered Architecture
```bash
cd arch1_layered
docker-compose -f docker-compose-layered.yml up -d --build

cd ../infrastructure
docker-compose -f docker-compose.infrastructure.yml up -d --build
```

#### Option 2: Microservices Architecture
```bash
cd arch2_microservices
docker-compose up -d --build
```

### Access the Application
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8080/api
- **Health Check**: http://localhost:8080/api/health

## 📊 Architecture Comparison

| Feature | Layered (Arch1) | Microservices (Arch2) |
|---------|----------------|----------------------|
| **Deployment Complexity** | Low ⭐ | High ⭐⭐⭐ |
| **Scalability** | Horizontal (entire app) | Independent per service |
| **Database** | Single shared DB | DB per service |
| **Communication** | Direct function calls | gRPC over network |
| **Team Collaboration** | Centralized | Distributed ownership |
| **Resource Usage** | ~2GB RAM | ~4-6GB RAM |
| **Development Speed** | Fast for small teams | Slower initially, faster at scale |
| **Debugging** | Easy ⭐ | Complex ⭐⭐⭐ |
| **Fault Isolation** | Low | High |
| **Technology Flexibility** | Limited | High |
| **Operational Overhead** | Low | High |
| **Best For** | Startups, MVPs, small apps | Large apps, multiple teams |

## 🎯 Features

Both architectures implement the same features:

- ✅ **User Management**: Registration, authentication, role-based access
- ✅ **Book Catalog**: Add, view, search, update books with metadata
- ✅ **Borrowing System**: Borrow/return books with inventory tracking
- ✅ **Admin Dashboard**: Statistics and system monitoring
- ✅ **Real-time Inventory**: Automatic updates when books are borrowed/returned
- ✅ **Security**: JWT-based authentication
- ✅ **Modern Frontend**: React with responsive design

## 📁 Project Structure

```
library-system/
├── README.md                          # This file
├── frontend/                          # Shared React frontend
│   ├── src/                          # React components
│   ├── Dockerfile                    # Production build (Arch2)
│   ├── Dockerfile.arch1              # Production build (Arch1)
│   ├── nginx.conf                    # Nginx config for Arch2
│   └── nginx-arch1.conf              # Nginx config for Arch1
│
├── arch1_layered/                    # Layered Architecture
│   ├── README.md                     # Arch1 documentation
│   ├── app.py                        # Flask application
│   ├── models.py                     # SQLAlchemy models
│   ├── routes.py                     # API routes
│   ├── services.py                   # Business logic
│   ├── docker-compose-layered.yml    # Service orchestration
│   ├── docker-compose-infra.yml      # Database & Redis
│   └── nginx.conf                    # Load balancer config
│
└── arch2_microservices/              # Microservices Architecture
    ├── README.md                     # Arch2 documentation
    ├── docker-compose.yml            # Service orchestration
    ├── protos/                       # gRPC protocol definitions
    │   ├── user.proto
    │   ├── book.proto
    │   └── borrowing.proto
    ├── gateway_service/              # API Gateway
    │   └── src/
    ├── user_service/                 # User microservice
    │   ├── src/
    │   └── Dockerfile.user
    ├── book_service/                 # Book microservice
    │   ├── src/
    │   └── Dockerfile.book
    └── borrowing_service/            # Borrowing microservice
        ├── src/
        └── Dockerfile.borrowing
```

## 🔄 Switching Between Architectures

Both architectures use the same frontend and expose the same API, making it easy to switch:

### Stop Current Architecture
```bash
# If running Arch1
cd arch1_layered
docker-compose -f docker-compose-layered.yml down

cd ../infrastructure
docker-compose -f docker-compose.infrastructure.yml down

# If running Arch2
cd arch2_microservices
docker-compose down
```

### Start Different Architecture
```bash
# Start Arch1
cd arch1_layered
docker-compose -f docker-compose-layered.yml up -d --build

cd ../infrastructure
docker-compose -f docker-compose.infrastructure.yml up -d --build

# OR start Arch2
cd arch2_microservices
docker-compose up -d --build
```

The frontend at `localhost:3000` will automatically connect to whichever backend is running on port 8080!

## 🧪 Testing Both Architectures

### API Compatibility Test
Both architectures expose identical REST APIs:

```bash
# Test books endpoint (works with both)
curl http://localhost:8080/api/books

# Test health endpoint (works with both)
curl http://localhost:8080/api/health
```

### Performance Comparison
```bash
# Arch1 - Layered
cd arch1_layered
time docker-compose -f docker-compose-layered.yml up -d

# Arch2 - Microservices
cd arch2_microservices
time docker-compose up -d
```

### Resource Usage Comparison
```bash
# Check memory usage
docker stats --no-stream
```

## 📚 Learning Objectives

This dual-architecture approach helps you understand:

1. **Architectural Trade-offs**: When to use monolithic vs microservices
2. **Scalability Patterns**: Horizontal scaling vs service-based scaling
3. **Communication Patterns**: REST, gRPC, inter-service communication
4. **Database Strategies**: Shared DB vs database per service
5. **Deployment Strategies**: Simple vs complex orchestration
6. **Team Organization**: Centralized vs distributed ownership

## 🛠️ Technology Stack

### Frontend (Shared)
- React 18
- Vite
- React Router
- Axios
- Tailwind CSS (or your CSS framework)

### Backend - Arch1 (Layered)
- Python 3.11
- Flask
- SQLAlchemy
- PostgreSQL
- Redis
- Nginx

### Backend - Arch2 (Microservices)
- Python 3.11
- Flask (Gateway)
- gRPC
- Protocol Buffers
- SQLAlchemy
- PostgreSQL (per service)

## 🐛 Troubleshooting

### Port Conflicts
```bash
# Check what's using port 8080
lsof -i :8080

# Kill the process
kill -9 <PID>
```

### Database Issues
```bash
# Reset everything
docker-compose down -v
docker-compose up -d --build
```

### Services Not Starting
```bash
# Check logs
docker-compose logs -f

# Check specific service
docker-compose logs -f <service_name>
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 When to Use Each Architecture?

### Use Layered Architecture (Arch1) when:
- ✅ Building an MVP or prototype
- ✅ Small to medium-sized team
- ✅ Simple deployment requirements
- ✅ Tight coupling is acceptable
- ✅ Lower operational complexity is priority
- ✅ Budget constraints on infrastructure

### Use Microservices (Arch2) when:
- ✅ Large, complex application
- ✅ Multiple independent teams
- ✅ Need to scale specific features independently
- ✅ Different parts of the system have different technology needs
- ✅ High availability is critical
- ✅ Can handle operational complexity
- ✅ Have DevOps expertise and resources

## 🎓 Educational Value

This repository demonstrates:

- **Software Architecture Patterns**: Practical implementation of two major patterns
- **System Design**: Trade-offs in distributed vs monolithic systems
- **Docker & Containerization**: Multi-container orchestration
- **API Design**: RESTful APIs and gRPC
- **Database Design**: Shared DB vs database per service
- **DevOps Practices**: Infrastructure as code, service orchestration
- **Full-Stack Development**: React frontend, Python backend

## 📜 License

MIT License - feel free to use this for learning and educational purposes.

## 🙏 Acknowledgments

Built as an educational project to demonstrate architectural patterns in modern software development.

