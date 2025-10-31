# DailyVeg API Portal

## 🛠️ Installation

1. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Database Setup**
   ```bash
   # Run migrations
   alembic upgrade head
   
   # Seed initial data (optional)
   python app/seed_data.py
   ```

5. **Start Development Server**
   ```bash
   python dev.py
   # OR
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Deployment

1. **Using Docker Compose (Recommended)**
   ```bash
   docker-compose up -d
   ```

2. **Manual Docker Build**
   ```bash
   docker build -t dailyveg-api:latest .
   docker run -d -p 8000:8000 --env-file .env dailyveg-api:latest
   ```

## ⚙️ Configuration

### JWT Key Generation

```python
from jwcrypto import jwk
key = jwk.JWK(generate='oct', size=256)
print(key.export())  # Use this value for JWT_KEY
```

## 🔧 Database Management

### Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_health.py

# Run with verbose output
pytest -v
```

## 📊 API Documentation

Once the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Detailed Health**: http://localhost:8000/health/detailed

## 🔒 Security Features

- **Authentication**: JWT-based authentication with refresh tokens
- **Rate Limiting**: Configurable rate limits per endpoint
- **Input Validation**: Comprehensive request validation
- **SQL Injection Protection**: Parameterized queries
- **CORS Configuration**: Configurable cross-origin policies
- **Security Headers**: Automatic security header injection

## 📈 Monitoring & Logging

- **Structured Logging**: JSON-formatted logs with rotation
- **Health Checks**: Built-in health monitoring endpoints
- **Request Logging**: Automatic request/response logging
- **Error Tracking**: Comprehensive error handling and logging

## 🚀 Production Deployment

### Docker Production

```bash
# Build production image
docker build -t dailyveg-api:prod .

# Run with production settings
docker run -d \
  --name dailyveg-api \
  -p 8000:8000 \
  --env-file .env.prod \
  --restart unless-stopped \
  dailyveg-api:prod
```

### Performance Tuning

- Use multiple workers: `--workers 4`
- Configure database connection pooling
- Enable Redis for caching (optional)
- Set up reverse proxy (Nginx)
- Configure SSL/TLS certificates

## 🤝 Development

### Code Quality

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Project Structure

```
app/
├── alembic/           # Database migrations
├── libs/              # Utility libraries
├── middleware/        # Custom middleware
├── routers/           # API route handlers
│   └── admin/         # Admin routes
│       └── crud/      # CRUD operations
├── static/            # Static files
├── config.py          # Configuration
├── database.py        # Database setup
├── dependencies.py    # FastAPI dependencies
├── exceptions.py      # Custom exceptions
├── logging_config.py  # Logging configuration
├── main.py           # Application entry point
├── models.py         # Database models
└── security.py       # Security utilities
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the health check endpoints for system status

## 🔄 Changelog

### v1.0.0
- Initial professional release
- Complete security implementation
- Comprehensive logging and monitoring
- Docker containerization
- Full test coverage
- Production-ready configuration
