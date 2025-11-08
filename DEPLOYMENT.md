# Production Deployment Guide

## Prerequisites

- Docker & Docker Compose
- MySQL 8.0+
- Redis (optional, for caching)
- SSL Certificate
- Domain name

## Environment Setup

### 1. Production Environment Variables
```bash
# Database
DB_HOST=your-mysql-host
DB_PORT=3306
DB_USER=dailyveg_user
DB_PASSWORD=secure_password_here
DB_NAME=dailyveg_prod

# JWT Keys (generate with: python -c "from jwcrypto import jwk; print(jwk.JWK(generate='oct', size=256).export())")
JWT_KEY={"k":"your-jwt-key","kty":"oct"}
ACCESS_JWT_KEY={"k":"your-access-key","kty":"oct"}
REFRESH_JWT_KEY={"k":"your-refresh-key","kty":"oct"}

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Admin
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=SecureAdminPassword123!

# Application
DEBUG=False
LOG_LEVEL=INFO
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

### 2. Docker Production Deployment

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=mysql
    env_file:
      - .env.production
    depends_on:
      - mysql
      - redis
    restart: unless-stopped
    
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - app
    restart: unless-stopped

volumes:
  mysql_data:
```

### 3. Nginx Configuration
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:8000;
    }
    
    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl;
        server_name yourdomain.com;
        
        ssl_certificate /etc/ssl/certs/cert.pem;
        ssl_certificate_key /etc/ssl/certs/key.pem;
        
        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## Deployment Steps

```bash
# 1. Clone repository
git clone <your-repo>
cd dailyveg-api

# 2. Setup environment
cp .env.example .env.production
# Edit .env.production with production values

# 3. Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# 4. Run migrations
docker-compose exec app poetry run alembic upgrade head

# 5. Create admin user
docker-compose exec app poetry run python app/seed_data.py
```

## Monitoring & Maintenance

### Health Checks
```bash
# Application health
curl https://yourdomain.com/health

# Detailed health
curl https://yourdomain.com/health/detailed
```

### Log Management
```bash
# View logs
docker-compose logs -f app

# Log rotation (add to crontab)
0 0 * * * docker-compose exec app find /app/logs -name "*.log" -mtime +7 -delete
```

### Backup Strategy
```bash
# Database backup
docker-compose exec mysql mysqldump -u root -p${DB_PASSWORD} ${DB_NAME} > backup_$(date +%Y%m%d).sql

# Automated backup (add to crontab)
0 2 * * * /path/to/backup-script.sh
```

## Performance Optimization

### 1. Database Optimization
- Enable query caching
- Add proper indexes
- Configure connection pooling
- Regular ANALYZE TABLE

### 2. Application Scaling
```bash
# Scale application instances
docker-compose up -d --scale app=3
```

### 3. Caching Strategy
- Redis for session storage
- Database query caching
- Static file caching with CDN

## Security Checklist

- [ ] SSL/TLS certificates configured
- [ ] Environment variables secured
- [ ] Database access restricted
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Security headers implemented
- [ ] Regular security updates
- [ ] Backup encryption enabled