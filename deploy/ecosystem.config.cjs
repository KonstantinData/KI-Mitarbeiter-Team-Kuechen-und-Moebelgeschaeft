/**
 * PM2 Konfiguration für die Frontend-Prozesse.
 * Das Python-Backend läuft als Systemd-Service, nicht via PM2.
 */

module.exports = {
  apps: [
    // Kein PM2 für Frontends nötig — diese werden als statische Dateien
    // von Caddy ausgeliefert. PM2 nur falls Node.js SSR eingesetzt wird.
  ],
};
