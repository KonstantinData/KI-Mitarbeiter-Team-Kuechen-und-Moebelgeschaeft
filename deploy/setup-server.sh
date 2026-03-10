#!/bin/bash
# Hetzner Server Bootstrap Script
# Ausführen als root auf einem frischen Ubuntu 24.04 Server

set -e

echo "=== KI-Mitarbeiter-Team Server Setup ==="

# System aktualisieren
apt-get update && apt-get upgrade -y

# Basis-Pakete
apt-get install -y curl wget git build-essential

# Python 3.12
apt-get install -y python3.12 python3.12-venv python3-pip

# Node.js 20 (via NodeSource)
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# pnpm
npm install -g pnpm

# PostgreSQL 16
apt-get install -y postgresql-16 postgresql-client-16

# pgvector Extension
apt-get install -y postgresql-16-pgvector

# Caddy
apt-get install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | \
  gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | \
  tee /etc/apt/sources.list.d/caddy-stable.list
apt-get update && apt-get install -y caddy

# PostgreSQL Setup
sudo -u postgres psql << 'SQL'
CREATE USER ki_team WITH PASSWORD 'SICHERES-PASSWORT-HIER-SETZEN';
CREATE DATABASE ki_mitarbeiter OWNER ki_team;
\c ki_mitarbeiter
CREATE EXTENSION IF NOT EXISTS vector;
SQL

echo "=== Server Setup abgeschlossen ==="
echo "Nächste Schritte:"
echo "  1. Repo clonen: git clone ..."
echo "  2. setup.sh ausführen"
echo "  3. .env befüllen"
echo "  4. Systemd Service aktivieren: systemctl enable kitchenflow-api"
echo "  5. Caddy starten: systemctl start caddy"
