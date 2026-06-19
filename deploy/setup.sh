#!/usr/bin/env bash
# VPS setup script for mia-snow-bot
# Tested on Ubuntu 22.04 LTS
# Run as root or a sudo user: bash setup.sh

set -euo pipefail

APP_USER="miabot"
APP_DIR="/home/${APP_USER}/mia-snow-bot"
PYTHON_VERSION="3.11"

echo "==> Installing system packages"
apt-get update -qq
apt-get install -y -qq \
    python3 python3-pip python3-venv \
    postgresql postgresql-contrib \
    nginx certbot python3-certbot-nginx \
    git curl ufw

echo "==> Creating app user"
id -u "$APP_USER" &>/dev/null || useradd -m -s /bin/bash "$APP_USER"

echo "==> Setting up PostgreSQL"
systemctl enable --now postgresql

# Create DB user and database (idempotent)
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='miabot'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER miabot WITH PASSWORD 'CHANGE_ME_STRONG_PASSWORD';"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='miasnow'" | grep -q 1 || \
    sudo -u postgres createdb -O miabot miasnow

echo "==> Cloning / updating repository"
if [ -d "$APP_DIR/.git" ]; then
    sudo -u "$APP_USER" git -C "$APP_DIR" pull
else
    sudo -u "$APP_USER" git clone https://github.com/publicitystunt25-crypto/mia-snow-bot.git "$APP_DIR"
fi

echo "==> Setting up Python virtual environment"
sudo -u "$APP_USER" python3 -m venv "$APP_DIR/.venv"
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install -q --upgrade pip
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install -q -r "$APP_DIR/requirements.txt"

echo "==> Installing systemd service"
cp "$APP_DIR/deploy/mia-snow-bot.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable mia-snow-bot

echo "==> Configuring firewall"
ufw --force enable
ufw allow OpenSSH
ufw allow 'Nginx Full'

echo ""
echo "============================================================"
echo "  Setup complete. Next steps:"
echo ""
echo "  1. Copy .env.example to /home/${APP_USER}/mia-snow-bot/.env"
echo "     and fill in your real values."
echo ""
echo "  2. Edit /etc/systemd/system/mia-snow-bot.service and"
echo "     confirm the EnvironmentFile path points to your .env."
echo ""
echo "  3. Restore your database backup:"
echo "     pg_restore -U miabot -d miasnow /path/to/backup.dump"
echo ""
echo "  4. Install your Nginx config:"
echo "     cp $APP_DIR/deploy/nginx.conf /etc/nginx/sites-available/mia-snow-bot"
echo "     ln -s /etc/nginx/sites-available/mia-snow-bot /etc/nginx/sites-enabled/"
echo "     nano /etc/nginx/sites-available/mia-snow-bot  # set your domain"
echo "     nginx -t && systemctl reload nginx"
echo ""
echo "  5. Get a TLS certificate:"
echo "     certbot --nginx -d yourdomain.com"
echo ""
echo "  6. Start the bot:"
echo "     systemctl start mia-snow-bot"
echo "     journalctl -u mia-snow-bot -f"
echo "============================================================"
