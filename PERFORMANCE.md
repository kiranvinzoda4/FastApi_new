# Performance Optimization Guide

## Database Optimization

### 1. Query Optimization
```python
# Bad: N+1 queries
users = db.query(User).all()
for user in users:
    orders = db.query(Order).filter(Order.user_id == user.id).all()

# Good: Eager loading
users = db.query(User).options(joinedload(User.orders)).all()
```

### 2. Indexing Strategy
```sql
-- Primary indexes
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_order_user_id ON orders(user_id);
CREATE INDEX idx_order_status ON orders(status);

-- Composite indexes
CREATE INDEX idx_order_user_status ON orders(user_id, status);
CREATE INDEX idx_order_date_status ON orders(created_at, status);
```

### 3. Connection Pooling
```python
# Optimized pool settings
engine = create_engine(
    database_url,
    pool_size=20,           # Base connections
    max_overflow=30,        # Additional connections
    pool_pre_ping=True,     # Validate connections
    pool_recycle=3600,      # Recycle every hour
)
```

## Application Performance

### 1. Async Operations
```python
# Use async for I/O operations
@router.post("/send-email")
async def send_email_async(email_data: EmailData):
    await email_service.send_async(email_data)
    return {"status": "sent"}
```

### 2. Caching Strategy
```python
# Redis caching
@lru_cache(maxsize=1000)
def get_user_permissions(user_id: str) -> List[str]:
    return db.query(Permission).filter_by(user_id=user_id).all()

# Response caching
@router.get("/users/{user_id}")
@cache(expire=300)  # 5 minutes
async def get_user(user_id: str):
    return user_service.get_by_id(user_id)
```

### 3. Request Optimization
```python
# Pagination for large datasets
@router.get("/orders")
def get_orders(skip: int = 0, limit: int = 100):
    return db.query(Order).offset(skip).limit(limit).all()

# Field selection
@router.get("/users")
def get_users(fields: List[str] = Query(None)):
    query = db.query(User)
    if fields:
        query = query.options(load_only(*fields))
    return query.all()
```

## Monitoring & Metrics

### 1. Performance Metrics
- **Response Time**: < 200ms for 95th percentile
- **Throughput**: > 1000 requests/second
- **Error Rate**: < 0.1%
- **Database Connections**: < 80% of pool

### 2. Key Performance Indicators
```python
# Custom metrics
from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests')
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')
ACTIVE_CONNECTIONS = Gauge('db_connections_active', 'Active DB connections')
```

### 3. Alerting Rules
```yaml
# prometheus/alert_rules.yml
groups:
  - name: dailyveg_alerts
    rules:
      - alert: HighResponseTime
        expr: http_request_duration_seconds{quantile="0.95"} > 0.5
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
      
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
```

## Load Testing

### 1. Locust Configuration
```python
# locustfile.py
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login and get token
        response = self.client.post("/admin/admin-login", json={
            "email": "test@example.com",
            "password": "password"
        })
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def get_users(self):
        self.client.get("/admin/users", headers=self.headers)
    
    @task(1)
    def create_user(self):
        self.client.post("/admin/users", json={
            "email": "new@example.com",
            "password": "password"
        }, headers=self.headers)
```

### 2. Load Test Commands
```bash
# Install locust
pip install locust

# Run load test
locust -f locustfile.py --host=http://localhost:8000

# Headless mode
locust -f locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10 --run-time 300s --headless
```

## Production Optimization

### 1. Server Configuration
```python
# Gunicorn with optimal settings
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 5
```

### 2. Resource Limits
```yaml
# docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### 3. Health Checks
```python
# Comprehensive health check
@router.get("/health/detailed")
async def detailed_health():
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "external_apis": await check_external_apis(),
        "disk_space": check_disk_space(),
        "memory_usage": check_memory_usage()
    }
    
    overall_status = "healthy" if all(checks.values()) else "unhealthy"
    
    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

## Best Practices

### 1. Code Optimization
- Use async/await for I/O operations
- Implement proper caching strategies
- Optimize database queries
- Use connection pooling
- Implement circuit breakers

### 2. Infrastructure
- Use CDN for static assets
- Implement load balancing
- Set up auto-scaling
- Monitor resource usage
- Regular performance testing

### 3. Monitoring
- Set up comprehensive logging
- Implement metrics collection
- Create performance dashboards
- Set up alerting rules
- Regular performance reviews