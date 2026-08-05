#!/bin/bash
# ═══════════════════════════════════════════════════════
# HiddenYatra — VPS Deployment Script
# Run on a fresh Ubuntu 22.04+ VPS
# Usage: sudo bash deploy/deploy.sh
# ═══════════════════════════════════════════════════════

set -euo pipefail

APP_DIR="/var/www/hiddenyatra"
APP_USER="www-data"
DOMAIN="${DOMAIN:-hiddenyatra.com}"

echo "═══════════════════════════════════════════"
echo "  HiddenYatra — Production Deployment"
echo "═══════════════════════════════════════════"

# ── 1. System Updates ──
echo "[1/10] Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq

# ── 2. Install Dependencies ──
echo "[2/10] Installing dependencies..."
apt-get install -y -qq \
    python3 python3-pip python3-venv \
    mysql-server \
    nginx \
    certbot python3-certbot-nginx \
    ufw \
    curl \
    git

# ── 3. Firewall ──
echo "[3/10] Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
echo "  ✓ Firewall: SSH, HTTP, HTTPS only"

# ── 4. MySQL Setup ──
echo "[4/10] Configuring MySQL..."
systemctl enable mysql
systemctl start mysql

# Generate a random password for the app user
DB_APP_PASS=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")

mysql -u root <<EOSQL
CREATE DATABASE IF NOT EXISTS hiddenyatra
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'hiddenyatra_app'@'localhost'
    IDENTIFIED BY '${DB_APP_PASS}';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, DROP, REFERENCES
    ON hiddenyatra.*
    TO 'hiddenyatra_app'@'localhost';

FLUSH PRIVILEGES;
EOSQL

echo "  ✓ MySQL database and user created"
echo "  ℹ DB password: ${DB_APP_PASS}"
echo "    (Save this — it won't be shown again)"

# ── 5. Application Setup ──
echo "[5/10] Setting up application..."
mkdir -p "$APP_DIR"

# Copy project files (assumes script is run from project root)
if [ -f "app.py" ]; then
    cp -r . "$APP_DIR/"
else
    echo "  ERROR: Run this script from the project root directory"
    exit 1
fi

cd "$APP_DIR"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install --quiet -r requirements.txt

# Create upload directories
mkdir -p static/uploads/{places,submissions,auth,hero,districts}
chown -R $APP_USER:$APP_USER static/uploads
chmod -R 755 static/uploads

# ── 6. Environment Variables ──
echo "[6/10] Creating production .env..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
ADMIN_PASS=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")

cat > .env <<EOF
# HiddenYatra Production Environment
# Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

FLASK_ENV=production
SECRET_KEY=${SECRET_KEY}
ADMIN_PASSWORD=${ADMIN_PASS}

# MySQL
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=hiddenyatra
DB_USER=hiddenyatra_app
DB_PASSWORD=${DB_APP_PASS}
DB_POOL_SIZE=5
DB_POOL_MAX=20

# Gunicorn
GUNICORN_WORKERS=4
GUNICORN_THREADS=2
GUNICORN_LOG_LEVEL=info
FORWARDED_ALLOW_IPS=127.0.0.1

# SMTP (configure for OTP emails)
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=your_email@gmail.com
# SMTP_PASS=your_app_password
# SMTP_FROM=your_email@gmail.com
EOF

chmod 600 .env
echo "  ✓ .env created with generated secrets"
echo "  ℹ Admin password: ${ADMIN_PASS}"
echo "    (Save this — it won't be shown again)"

# ── 7. Database Schema ──
echo "[7/10] Loading database schema..."
mysql -u hiddenyatra_app -p"${DB_APP_PASS}" hiddenyatra < scripts/migrations/mysql_schema.sql 2>/dev/null || true

# Add composite indexes (may fail with IF NOT EXISTS syntax)
mysql -u hiddenyatra_app -p"${DB_APP_PASS}" hiddenyatra -e "
    CREATE INDEX idx_places_slug_deleted ON places (slug, deleted_at);
    CREATE INDEX idx_places_lat_lng ON places (latitude, longitude);
    CREATE INDEX idx_reviews_place_created ON reviews (place_id, created_at DESC);
" 2>/dev/null || true

# Seed data
PYTHONIOENCODING=utf-8 python scripts/seed/seed_bihar_complete.py 2>/dev/null && echo "  ✓ Data seeded" || echo "  ℹ Seed skipped (data may already exist)"

# ── 8. Set Permissions ──
echo "[8/10] Setting permissions..."
chown -R $APP_USER:$APP_USER "$APP_DIR"
chmod -R 755 "$APP_DIR"
chmod 600 "$APP_DIR/.env"

# ── 9. systemd Service ──
echo "[9/10] Installing systemd service..."
cp deploy/hiddenyatra.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable hiddenyatra
systemctl start hiddenyatra

sleep 3
if systemctl is-active --quiet hiddenyatra; then
    echo "  ✓ HiddenYatra service running"
else
    echo "  ✗ Service failed to start!"
    journalctl -u hiddenyatra --no-pager -n 20
    exit 1
fi

# ── 10. Nginx ──
echo "[10/10] Configuring Nginx..."

# Create initial HTTP-only config for certbot
cat > /etc/nginx/conf.d/hiddenyatra.conf <<NGINX
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN} www.${DOMAIN};

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location /static/ {
        alias ${APP_DIR}/static/;
        expires 7d;
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        client_max_body_size 16M;
    }
}
NGINX

# Remove default Nginx site
rm -f /etc/nginx/sites-enabled/default

nginx -t && systemctl reload nginx
echo "  ✓ Nginx configured (HTTP)"

# ── SSL (requires DNS to be pointed at this server) ──
echo ""
echo "═══════════════════════════════════════════"
echo "  DEPLOYMENT COMPLETE!"
echo "═══════════════════════════════════════════"
echo ""
echo "  Application: http://${DOMAIN}"
echo "  Health:      http://${DOMAIN}/health"
echo ""
echo "  Next steps:"
echo "  1. Point DNS A record for ${DOMAIN} to this server's IP"
echo "  2. Run: sudo certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}"
echo "  3. Then replace nginx config with deploy/nginx.conf"
echo "  4. Set up backup cron:"
echo "     sudo cp deploy/backup.sh /opt/scripts/"
echo "     sudo chmod +x /opt/scripts/backup.sh"
echo "     echo '0 2 * * * /opt/scripts/backup.sh' | sudo crontab -"
echo ""
echo "  Credentials (SAVE THESE):"
echo "  ─────────────────────────"
echo "  Admin Password:  ${ADMIN_PASS}"
echo "  DB App Password: ${DB_APP_PASS}"
echo "  Secret Key:      ${SECRET_KEY}"
echo ""
echo "  Commands:"
echo "  ─────────"
echo "  Status:  sudo systemctl status hiddenyatra"
echo "  Logs:    sudo journalctl -u hiddenyatra -f"
echo "  Restart: sudo systemctl restart hiddenyatra"
echo "  Backup:  sudo /opt/scripts/backup.sh"
echo ""
