# Deployment Guide for RJW GLOBAL FX

This guide covers deployment options for the RJW GLOBAL FX trading platform.

## Table of Contents
1. [Development Setup](#development-setup)
2. [Production Deployment with Docker](#production-deployment-with-docker)
3. [Manual Production Deployment](#manual-production-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Security Considerations](#security-considerations)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 16+ (for frontend)
- PostgreSQL 13+ (recommended for production)
- Redis 6+ (for production)

### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd RJW_GLOBAL_FX/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Run development server
python app.py
```

## Production Deployment with Docker

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

### Deployment Steps

1. **Prepare Environment**
```bash
# Clone repository
git clone <repository-url>
cd RJW_GLOBAL_FX/backend

# Create production environment file
cp .env.example .env.production
```

2. **Configure Environment Variables**
Edit `.env.production` with your production settings:
```bash
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key
JWT_SECRET_KEY=your-very-secure-jwt-secret
DATABASE_URL=postgresql://forex_user:secure_password@db:5432/forex_db
REDIS_URL=redis://redis:6379/0
MAIL_SERVER=your-smtp-server
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-app-password
FORCE_HTTPS=true
```

3. **Deploy with Docker Compose**
```bash
# Build and start all services
docker-compose -f docker-compose.yml --env-file .env.production up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
```

4. **Initialize Database**
```bash
# Run database migrations
docker-compose exec backend python -c "
from app import create_app, db;
app = create_app();
app.app_context().push();
db.create_all()
"
```

5. **Verify Deployment**
- API: `http://your-domain.com/api/docs/swagger`
- Health Check: `http://your-domain.com/`
- Grafana: `http://your-domain.com:3000`
- Prometheus: `http://your-domain.com:9090`

## Manual Production Deployment

### System Requirements
- Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- 4GB+ RAM
- 20GB+ Storage
- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Nginx

### Installation Steps

1. **Install System Dependencies**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql redis-server nginx

# CentOS/RHEL
sudo dnf install -y python3.11 python3-pip postgresql-server redis nginx
```

2. **Setup Application User**
```bash
sudo useradd -m -s /bin/bash forexapp
sudo su - forexapp
```

3. **Deploy Application Code**
```bash
# Clone repository
git clone <repository-url> /home/forexapp/app
cd /home/forexapp/app

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

4. **Configure Database**
```bash
# Switch to postgres user
sudo su - postgres

# Create database and user
createdb forex_db
createuser --interactive forex_user
psql -c "ALTER USER forex_user PASSWORD 'secure_password';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE forex_db TO forex_user;"

# Exit postgres user
exit
```

5. **Configure Environment**
```bash
# Create production environment file
cp .env.example .env
nano .env

# Set production values
FLASK_ENV=production
DATABASE_URL=postgresql://forex_user:secure_password@localhost:5432/forex_db
# ... other settings
```

6. **Initialize Database**
```bash
source venv/bin/activate
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

7. **Setup Gunicorn Service**
```bash
sudo tee /etc/systemd/system/forex-api.service > /dev/null <<EOF
[Unit]
Description=RJW GLOBAL FX API
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=forexapp
Group=forexapp
WorkingDirectory=/home/forexapp/app
Environment=PATH=/home/forexapp/app/venv/bin
EnvironmentFile=/home/forexapp/app/.env
ExecStart=/home/forexapp/app/venv/bin/gunicorn -w 4 -b 127.0.0.1:4000 app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable forex-api
sudo systemctl start forex-api
```

8. **Configure Nginx**
```bash
sudo tee /etc/nginx/sites-available/forex-api > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=auth:10m rate=5r/s;

    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:4000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/auth/ {
        limit_req zone=auth burst=10 nodelay;
        proxy_pass http://127.0.0.1:4000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /socket.io/ {
        proxy_pass http://127.0.0.1:4000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/forex-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Environment Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `FLASK_ENV` | Environment | `production` |
| `SECRET_KEY` | Flask secret key | `random-64-char-string` |
| `JWT_SECRET_KEY` | JWT signing key | `random-64-char-string` |
| `DATABASE_URL` | Database connection | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |
| `MAIL_SERVER` | SMTP server | `smtp.gmail.com` |
| `MAIL_USERNAME` | Email username | `noreply@domain.com` |
| `MAIL_PASSWORD` | Email password | `app-specific-password` |
| `FRONTEND_URL` | Frontend URL | `https://your-domain.com` |

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PLATFORM_PROFIT_MARGIN` | `0.30` | Platform profit margin |
| `AUTO_TRADE_INTERVAL` | `5` | Trade simulation interval (seconds) |
| `FORCE_HTTPS` | `false` | Force HTTPS redirects |
| `EMAIL_VERIFICATION_EXPIRE_HOURS` | `24` | Email verification expiry |
| `PASSWORD_RESET_EXPIRE_HOURS` | `1` | Password reset expiry |

## Security Considerations

### 1. SSL/TLS Configuration
- Use valid SSL certificates (Let's Encrypt recommended)
- Configure strong cipher suites
- Enable HSTS headers

### 2. Database Security
- Use strong database passwords
- Restrict database access to application server only
- Enable database connection encryption
- Regular database backups

### 3. Application Security
- Use environment variables for secrets
- Enable rate limiting
- Configure security headers
- Regular security updates

### 4. Network Security
- Configure firewall rules
- Use VPN for admin access
- Monitor access logs
- Implement intrusion detection

### 5. Email Security
- Use app-specific passwords
- Configure SPF/DKIM/DMARC records
- Monitor email delivery

## Monitoring and Maintenance

### 1. Application Monitoring
```bash
# Check service status
sudo systemctl status forex-api

# View logs
sudo journalctl -u forex-api -f

# Check resource usage
htop
df -h
```

### 2. Database Maintenance
```bash
# Database backup
pg_dump forex_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Database vacuum (PostgreSQL)
psql -d forex_db -c "VACUUM ANALYZE;"

# Check database size
psql -d forex_db -c "SELECT pg_size_pretty(pg_database_size('forex_db'));"
```

### 3. Log Management
```bash
# Rotate logs
sudo logrotate -f /etc/logrotate.d/forex-api

# Monitor error logs
tail -f /home/forexapp/app/logs/errors.log

# Monitor security logs
tail -f /home/forexapp/app/logs/security.log
```

### 4. Performance Monitoring
- Use Grafana dashboards
- Monitor Prometheus metrics
- Set up alerting rules
- Regular performance audits

### 5. Backup Strategy
- Daily database backups
- Weekly full system backups
- Offsite backup storage
- Backup restoration testing

### 6. Updates and Maintenance
```bash
# Update application
cd /home/forexapp/app
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart forex-api

# Update system packages
sudo apt update && sudo apt upgrade  # Ubuntu/Debian
sudo dnf update                     # CentOS/RHEL
```

## Troubleshooting

### Common Issues

1. **Service Won't Start**
```bash
# Check logs
sudo journalctl -u forex-api -n 50

# Check configuration
python -c "from app import create_app; app = create_app(); print('Config OK')"
```

2. **Database Connection Issues**
```bash
# Test database connection
psql -h localhost -U forex_user -d forex_db

# Check database status
sudo systemctl status postgresql
```

3. **High Memory Usage**
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Restart service if needed
sudo systemctl restart forex-api
```

4. **SSL Certificate Issues**
```bash
# Test SSL configuration
openssl s_client -connect your-domain.com:443

# Check certificate expiry
openssl x509 -in /path/to/cert.pem -noout -dates
```

### Performance Optimization

1. **Database Optimization**
- Add appropriate indexes
- Optimize queries
- Configure connection pooling

2. **Application Optimization**
- Enable caching
- Optimize static file serving
- Configure load balancing

3. **System Optimization**
- Tune kernel parameters
- Optimize file system
- Configure swap space

## Support

For deployment issues:
1. Check application logs
2. Review system resources
3. Verify configuration
4. Consult documentation
5. Contact support team

## Security Updates

Regularly check for:
- Python package updates
- System security patches
- Database updates
- SSL certificate renewals
- Dependency vulnerabilities
