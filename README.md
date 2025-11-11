# 🚀 FastAPI Demo Project

> A modern, production-ready FastAPI application with JWT authentication, comprehensive testing, and streamlined development workflow.

## ✨ Features

🔐 **JWT Authentication** • 🛡️ **Rate Limiting** • 📊 **API Documentation** • 🧪 **Comprehensive Testing** • 🐳 **Docker Ready** • 📈 **Health Monitoring**

---

## 🎯 Quick Start

### 1️⃣ Setup Environment
```bash
# Install Poetry
pip install poetry

# Install dependencies
poetry install && poetry shell

# Configure environment
cp .env.example .env
```

### 2️⃣ Database & Server
```bash
# Setup database
poetry run alembic upgrade head

# Start development server
poetry run python dev.py
```

### 3️⃣ Explore APIs
- 🌐 **Swagger UI**: http://localhost:8000/docs
- ❤️ **Health Check**: http://localhost:8000/health

---

## 🧪 Testing Made Simple

```bash
# Run all tests (clean, minimal output)
poetry run pytest tests/ --tb=line --no-header -q --color=yes --disable-warnings

# Run specific test types
poetry run pytest tests/unit/ -q --color=yes        # Unit tests
poetry run pytest tests/integration/ -q --color=yes # Integration tests
poetry run pytest tests/e2e/ -q --color=yes         # End-to-end tests

# Run with coverage (clean output)
poetry run pytest tests/ -q --cov=app --cov-report=term-missing --disable-warnings

# Run tests with automatic cache cleanup
poetry run python test_and_clean.py

# Manual cache cleanup
poetry run python cleanup.py
```

**Current Tests (38 passing):**
- ✅ **Unit Tests**: Security functions, models, configuration
- ✅ **Integration Tests**: API endpoints, health checks
- ✅ **E2E Tests**: Complete workflows and user journeys

**Test Structure:**
```
tests/
├── unit/          # Fast, isolated tests
│   ├── test_security.py
│   └── test_models.py
├── integration/   # API endpoint tests  
│   ├── test_health_api.py
│   ├── test_countries_api.py
│   ├── test_states_api.py
│   └── test_cities_api.py
├── e2e/          # Full workflow tests
│   ├── test_basic_workflow.py
│   ├── test_countries_workflow.py
│   ├── test_states_workflow.py
│   ├── test_cities_workflow.py
│   └── test_complete_workflow.py
├── fixtures/     # Test data factory
└── conftest.py   # Test configuration
```

---

## 🔧 Essential Commands

### Development
```bash
poetry add package-name              # Add dependency
poetry run alembic revision -m "msg" # Create migration
poetry run alembic upgrade head      # Apply migrations
```

### JWT Keys Setup
```python
import json, secrets, base64

key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('=')
jwt_key = {"k": key, "kty": "oct"}
print(f'ACCESS_JWT_KEY={json.dumps(jwt_key)}')
```

---

## 🐳 Docker Deployment

```bash
# Quick start with Docker Compose
docker-compose up -d

# Manual build
docker build -t demo-project .
docker run -p 8000:8000 --env-file .env demo-project
```

## 📚 Resources

- 📖 [API Documentation](http://localhost:8000/docs) - Interactive Swagger UI
- 🏥 [Health Monitoring](http://localhost:8000/health) - System status
- 🐛 [Issues](https://github.com/your-repo/issues) - Bug reports & features

---

**Built with ❤️ using FastAPI, SQLAlchemy, and Poetry**