# HiddenYatra — Deployment Guide

## Prerequisites

- Python 3.11+
- MySQL 8.x
- Git

## 1. Environment Setup

### Clone & Install

```bash
git clone <repo-url> HiddenYatra
cd HiddenYatra
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Required Environment Variables

Create a `.env` file (never commit to Git):

```env
# ── Required in Production ──
FLASK_ENV=production
SECRET_KEY=<random-64-char-hex>
ADMIN_PASSWORD=<strong-admin-password>

# ── Database ──
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=hiddenyatra
DB_USER=hiddenyatra_app
DB_PASSWORD=<db-password>
DB_POOL_SIZE=5
DB_POOL_MAX=20

# ── Email (for OTP) ──
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

Generate a secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 2. MySQL Setup

### Create Database & User

```sql
CREATE DATABASE hiddenyatra CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'hiddenyatra_app'@'localhost' IDENTIFIED BY '<strong-password>';
GRANT ALL PRIVILEGES ON hiddenyatra.* TO 'hiddenyatra_app'@'localhost';
FLUSH PRIVILEGES;
```

### Run Schema Migration

```bash
mysql -u hiddenyatra_app -p hiddenyatra < scripts/migrations/mysql_schema.sql
```

### Seed Data (Optional)

```bash
python scripts/seed/seed_bihar_complete.py
```

## 3. Production Server

### Option A: Gunicorn (Linux/Mac — Recommended)

```bash
pip install gunicorn

# Basic
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"

# Production with logging
gunicorn \
  --workers 4 \
  --threads 2 \
  --bind 0.0.0.0:5000 \
  --timeout 30 \
  --access-logfile /var/log/hiddenyatra/access.log \
  --error-logfile /var/log/hiddenyatra/error.log \
  --log-level info \
  "app:create_app()"
```

### Option B: Waitress (Windows)

```bash
pip install waitress

# Basic
waitress-serve --host=0.0.0.0 --port=5000 --call app:create_app

# With thread tuning
waitress-serve \
  --host=0.0.0.0 \
  --port=5000 \
  --threads=8 \
  --call app:create_app
```

### Option C: Systemd Service (Linux)

Create `/etc/systemd/system/hiddenyatra.service`:

```ini
[Unit]
Description=HiddenYatra Flask App
After=network.target mysql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/hiddenyatra
EnvironmentFile=/var/www/hiddenyatra/.env
ExecStart=/var/www/hiddenyatra/venv/bin/gunicorn \
  --workers 4 \
  --threads 2 \
  --bind 127.0.0.1:5000 \
  --timeout 30 \
  "app:create_app()"
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable hiddenyatra
sudo systemctl start hiddenyatra
```

## 4. Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name hiddenyatra.com www.hiddenyatra.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name hiddenyatra.com www.hiddenyatra.com;

    ssl_certificate /etc/letsencrypt/live/hiddenyatra.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/hiddenyatra.com/privkey.pem;

    # Security headers (app also sends these as backup)
    add_header X-Frame-Options SAMEORIGIN always;
    add_header X-Content-Type-Options nosniff always;

    # Static files — serve directly from Nginx for performance
    location /static/ {
        alias /var/www/hiddenyatra/static/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    # Upload files
    location /static/uploads/ {
        alias /var/www/hiddenyatra/static/uploads/;
        expires 1d;
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # File upload size
        client_max_body_size 16M;
    }
}
```

## 5. SSL (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d hiddenyatra.com -d www.hiddenyatra.com
```

Auto-renewal is configured automatically via systemd timer.

## 6. Backups

### MySQL Backup Script

Create `/opt/scripts/backup_hiddenyatra.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M)
BACKUP_DIR="/var/backups/hiddenyatra"
mkdir -p $BACKUP_DIR

# Database
mysqldump -u hiddenyatra_app -p'<password>' hiddenyatra | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Uploads
tar czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/www/hiddenyatra/static/uploads/

# Retain last 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### Cron Schedule

```bash
# Daily at 2 AM
0 2 * * * /opt/scripts/backup_hiddenyatra.sh >> /var/log/hiddenyatra/backup.log 2>&1
```

## 7. Monitoring

### Log Locations

| Log | Location |
|---|---|
| App logs | stdout/stderr (captured by systemd) |
| Access log | `/var/log/hiddenyatra/access.log` |
| Error log | `/var/log/hiddenyatra/error.log` |
| Nginx log | `/var/log/nginx/access.log` |

### Health Check

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/
# Should return 200
```

## 8. Production Checklist

- [ ] `FLASK_ENV=production` is set
- [ ] `SECRET_KEY` is a strong random value
- [ ] `ADMIN_PASSWORD` is changed from default
- [ ] MySQL user has limited privileges (no GRANT, DROP DATABASE)
- [ ] `.env` file is NOT in Git
- [ ] Upload directories exist with correct permissions
- [ ] Nginx is configured with SSL
- [ ] Backup script is running via cron
- [ ] Log rotation is configured
- [ ] Firewall allows only ports 80, 443, 22
