# 🐳 HiddenYatra — Production Deployment Guide

## Production Overview

HiddenYatra is containerized using Docker and Docker Compose, served via Gunicorn WSGI workers and reverse-proxied with Nginx.

---

## 🚀 Docker Compose Deployment (Recommended)

### 1. Configure Production Environment
Copy `.env.production.example` to `.env`:
```bash
cp .env.production.example .env
```

Set strong passwords and production settings:
```ini
FLASK_ENV=production
SECRET_KEY=super_secure_64_character_random_string
ADMIN_PASSWORD=strong_admin_password
DB_PASSWORD=strong_mysql_root_password
```

### 2. Build & Launch Containers
```bash
docker-compose up -d --build
```

### 3. Verify Container Status
```bash
docker-compose ps
docker-compose logs -f web
```

---

## 🌐 Manual Gunicorn + Nginx Setup

### 1. Run Gunicorn WSGI Server
```bash
gunicorn -c gunicorn.conf.py wsgi:app
```

### 2. Nginx Reverse Proxy Configuration
```nginx
server {
    listen 80;
    server_name hiddenyatra.in www.hiddenyatra.in;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /d/HiddenYatra/static/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
```

---

## 🔒 Security Hardening

- SSL/TLS termination via Let's Encrypt Certbot (`sudo certbot --nginx`).
- Security Headers enabled in Flask (`Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`).
- Database credentials stored exclusively in environment variables.
