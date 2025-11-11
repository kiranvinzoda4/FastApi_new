# Demo Project

## 🛠️ Installation

1. **Install Poetry** (if not already installed)
   ```bash
   pip install poetry
   ```

2. **Install dependencies and create virtual environment**
   ```bash
   poetry install
   ```

3. **Activate Poetry shell**
   ```bash
   poetry shell
   ```

3. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   # For production: Set DEBUG=False and update all values
   ```

4. **Database Setup**
   ```bash
   # Run migrations
   poetry run alembic upgrade head
   
   # Seed initial data (optional)
   poetry run python app/seed_data.py
   ```

5. **Start Development Server**
   ```bash
   poetry run python dev.py
   # OR
   poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Deployment

1. **Using Docker Compose (Recommended)**
   ```bash
   docker-compose up -d
   ```

2. **Manual Docker Build**
   ```bash
   docker build -t demo-project:latest .
   docker run -d -p 8000:8000 --env-file .env demo-project:latest
   ```

## ⚙️ Configuration

### Poetry Dependency Management

```bash
# Add new dependency
poetry add package-name

# Add development dependency
poetry add --group dev package-name

# Update dependencies
poetry update

# Show dependency tree
poetry show --tree

# Export requirements.txt (if needed)
poetry export -f requirements.txt --output requirements.txt
```

### JWT Key Generation

Generate JWT keys and add to your `.env` file:

```python
import json
import secrets
import base64

# Generate key
key_bytes = secrets.token_bytes(32)
key_b64 = base64.urlsafe_b64encode(key_bytes).decode('utf-8').rstrip('=')
jwt_key = {"k": key_b64, "kty": "oct"}

print(f'ACCESS_JWT_KEY={json.dumps(jwt_key)}')
print(f'REFRESH_JWT_KEY={json.dumps(jwt_key)}')
```

Run this twice to generate different keys for ACCESS_JWT_KEY and REFRESH_JWT_KEY.

## 🔧 Database Management

### Migrations

```bash
# Create new migration
poetry run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
poetry run alembic upgrade head

# Rollback migration
poetry run alembic downgrade -1

# View migration history
poetry run alembic history
```

## 🧪 Testing

### Quick Start
```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run with detailed coverage report
make test-coverage
```

### Detailed Testing Commands

#### Using Make (Recommended)
```bash
make test           # All tests with coverage
make test-unit      # Unit tests only
make test-integration # Integration tests only
make test-coverage  # Tests with HTML coverage report
```

#### Using Poetry Directly
```bash
# All tests with coverage
poetry run pytest tests/ -v --cov=app --cov-report=term-missing

# Unit tests only
poetry run pytest tests/unit/ -v

# Integration tests only
poetry run pytest tests/integration/ -v

# Specific test file
poetry run pytest tests/unit/test_security.py -v

# Specific test method
poetry run pytest tests/unit/test_security.py::TestSecurityUtils::test_hash_password -v

# Run tests with markers
poetry run pytest -m "unit" -v
poetry run pytest -m "integration" -v
```

#### Using Custom Test Runner
```bash
# Run test runner script
python tests/test_runner.py --type unit
python tests/test_runner.py --type integration
python tests/test_runner.py --type all --no-coverage
```

### Test Structure
```
tests/
├── fixtures/
│   └── test_data.py          # Test data factory
├── unit/
│   ├── test_security.py      # Security utilities tests
│   ├── test_utils.py         # Utility functions tests
│   ├── test_email_templates.py # Email template tests
│   └── test_models.py        # Database model tests
├── integration/
│   ├── test_auth_api.py      # Authentication API tests
│   └── test_health_api.py    # Health check API tests
└── conftest.py               # Test configuration & fixtures
```

### Coverage Requirements
- **Minimum Coverage**: 80%
- **Coverage Reports**: Terminal + HTML (htmlcov/)
- **Excluded Files**: Migrations, test files

### Test Configuration
- **Database**: SQLite (isolated for tests)
- **Fixtures**: Comprehensive test data factory
- **Mocking**: Database config mocked for fast execution
- **Markers**: `unit`, `integration`, `slow`, `auth`, `email`

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
docker build -t demo-project:prod .

# Run with production settings
docker run -d \
  --name demo-project \
  -p 8000:8000 \
  --env-file .env.prod \
  --restart unless-stopped \
  demo-project:prod
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
make format
# OR
poetry run black app/ tests/

# Lint code
make lint
# OR
poetry run flake8 app/
poetry run mypy app/

# Clean up generated files
make clean
```

### Development Workflow

```bash
# 1. Install dependencies
make install

# 2. Run tests
make test

# 3. Check code quality
make lint
make format

# 4. Start development server
make dev

# 5. Run migrations
make migrate

# 6. Seed test data
make seed
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

## 📚 Documentation

- **[Testing Guide](TESTING.md)** - Comprehensive testing documentation
- **[API Guide](API_GUIDE.md)** - Detailed API documentation with examples
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment instructions
- **[Architecture Guide](ARCHITECTURE.md)** - System architecture and design patterns
- **[Performance Guide](PERFORMANCE.md)** - Optimization and monitoring guidelines
- **[API Documentation](http://localhost:8000/docs)** - Swagger UI (when server is running)
- **[Health Checks](http://localhost:8000/health)** - System status endpoints

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the health check endpoints for system status

## 🔄 Migration from pip to Poetry

If you're migrating from the previous pip-based setup:

1. **Remove old virtual environment**
   ```bash
   # Deactivate if active
   deactivate
   
   # Remove old venv folder
   rmdir /s venv  # Windows
   rm -rf venv    # Linux/Mac
   ```

2. **Install Poetry and dependencies**
   ```bash
   pip install poetry
   poetry install
   ```

3. **Update your workflow**
   - Replace `pip install -r requirements.txt` with `poetry install`
   - Use `poetry run` prefix for all commands
   - Use `poetry shell` to activate the environment

## 🔄 Changelog

### v1.1.0
- Migrated to Poetry for dependency management
- Improved dependency resolution and lock file
- Updated Docker configuration for Poetry
- Enhanced development workflow

### v1.0.0
- Initial professional release
- Complete security implementation
- Comprehensive logging and monitoring
- Docker containerization
- Full test coverage
- Production-ready configuration
