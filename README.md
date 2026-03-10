# KI-Mitarbeiter-Team für Küchen- und Möbelgeschäfte

Ein vollständiges System aus KI-gestützten virtuellen Mitarbeitern, das Küchen- und Möbelgeschäfte dabei unterstützt, Kundenanfragen rund um die Uhr zu bearbeiten — vom ersten Chat-Kontakt bis zur Terminbuchung.

---

## Was ist das hier?

Dieses Projekt ist die technische Grundlage für ein Team aus KI-Agenten, die im Hintergrund wie echte Mitarbeiter arbeiten: Sie begrüßen Interessenten auf der Website, führen Beratungsgespräche, qualifizieren Leads, buchen Termine und koordinieren Nachfass-Aktionen — automatisch, 24/7, in natürlicher Sprache.

Das System ist als **fertige Plattform** konzipiert: Ein Küchenstudio kauft Zugang, richtet sein Studio ein, und die KI-Mitarbeiter gehen direkt an die Arbeit. Mehrere Studios können das System gleichzeitig nutzen, ohne sich gegenseitig zu beeinflussen. Alle Mitarbeiter können dabei **parallel** mit verschiedenen Besuchern gleichzeitig arbeiten.

---

## Wie funktioniert die Integration?

Das System ist **kein Ersatz** für die bestehende Website — es wird unsichtbar dort hineinintegriert:

```html
<!-- Eine einzige Zeile in der bestehenden Website -->
<script
  src="https://widget.mein-kuechenexperte.de/loader.iife.js"
  data-studio="mein-kuechenexperte"
></script>
```

Das war es. Der Chat-Button erscheint, und die KI-Mitarbeiter sind einsatzbereit.

---

## Die KI-Mitarbeiter (geplant)

Ein einziges Chat-Fenster für den Besucher — im Hintergrund übernimmt automatisch der passende Mitarbeiter je nach Phase des Gesprächs.

| Name | Aufgabe | Wann aktiv |
| ---- | ------- | ---------- |
| **Lisa** | Erstkontakt, Begrüßung, Lead-Erfassung | Sobald jemand die Website besucht |
| **Max** | Beratung, Planung, Angebote | Wenn der Kunde konkrete Fragen hat |
| **Anna** | Auftragsabwicklung, Dokumente | Nach dem Kauf |
| **Tom** | Lieferung, Montage, Koordination | Kurz vor dem Liefertermin |
| **Sara** | Qualitätssicherung, Kundenbindung | Nach der Montage |

> **Aktueller Stand:** Das Fundament ist fertig gebaut. Die einzelnen Agenten werden in den nächsten Entwicklungsschritten hinzugefügt.

---

## Wie sieht das für den Endkunden aus?

Ein Besucher auf `www.mein-kuechenexperte.de` sieht einen Chat-Button in der Ecke. Er klickt, schreibt seine Frage — und Lisa antwortet sofort. Die Unterhaltung fühlt sich wie ein echtes Gespräch an. Im Hintergrund erfasst das System alle wichtigen Informationen, bewertet den Interessenten und plant den nächsten Schritt (z. B. einen Beratungstermin).

Das Küchenstudio sieht alles in einem Admin-Dashboard unter `app.mein-kuechenexperte.de`: welche Leads eingegangen sind, was besprochen wurde, welche Termine bevorstehen.

---

## Wo läuft was?

| Komponente | URL | Plattform |
| ---------- | --- | --------- |
| **Chat-Widget** (für Websitebesucher) | `widget.mein-kuechenexperte.de` | Cloudflare Pages |
| **Admin-Dashboard** (für Studiobetreiber) | `app.mein-kuechenexperte.de` | Cloudflare Pages |
| **Backend / KI** (unsichtbar im Hintergrund) | `api.mein-kuechenexperte.de` | Hetzner Cloud (EU) |
| **Hauptwebsite** (unverändert) | `www.mein-kuechenexperte.de` | bestehend |

---

## Was ist aktuell fertig gebaut?

### Infrastruktur & Backend

- Vollständiges **Datenbankschema** (Interessenten, Gespräche, Termine, Wissensbasis, Audit-Trail)
- **API-Server** mit allen nötigen Endpunkten (Authentifizierung, Chat, Studios, Leads, Termine u.v.m.)
- **Echtzeit-Chat** via WebSocket — Nachrichten werden in Millisekunden übertragen
- **Wissenssuche**: Das System kann in der Produktdatenbank eines Studios semantisch suchen und passende Informationen an die KI weitergeben
- **Gedächtnissystem**: Jeder Agent merkt sich, was in früheren Gesprächen mit einem Kunden besprochen wurde
- **Multi-Studio-Betrieb**: Beliebig viele Studios können das System parallel nutzen — vollständig voneinander getrennt

### KI-Kern

- Vorgefertigte **Agentenstruktur**: Jeder neue Agent folgt demselben 7-Schritte-Ablauf (Kontext laden → Anfrage verstehen → Wissen abrufen → Tools nutzen → Antworten → Speichern)
- Anbindung an **Anthropic Claude** (modernste Sprachmodell-Technologie) für natürliche Gespräche und komplexes Reasoning
- **Tool-System**: Agenten können eigenständig Aktionen ausführen (Termine prüfen, E-Mails senden, Daten speichern)
- **Vorlage für neue Agenten**: Ein neuer Mitarbeiter (z. B. Lisa) kann schnell durch Kopieren und Anpassen einer Vorlage erstellt werden

### Frontend

- **Chat-Widget**: Ein `<script>`-Tag reicht zur Integration in jede bestehende Website
- **Admin-Dashboard**: Weboberfläche für das Küchenstudio mit Login, Übersichten und Navigation
- Beide Frontends **live auf Cloudflare Pages** mit automatischem SSL und Custom Domains

### Deployment & Betrieb

- **Backend** läuft auf einem europäischen Server (Hetzner, DSGVO-konform)
- **Frontends** über Cloudflare Pages — schnell, weltweit, ausfallsicher
- Automatische Deployments: Jeder Code-Push löst einen neuen Build aus
- Konfigurations- und Deployment-Skripte für schnelle Einrichtung

---

## Projektstruktur (vereinfacht)

```text
KI-Mitarbeiter-Team/
│
├── src/
│   ├── core/          # Gemeinsamer Kern aller Agenten (LLM, Gedächtnis, Wissen, Tools)
│   ├── agents/        # Die einzelnen KI-Mitarbeiter (Lisa, Max, Anna, Tom, Sara)
│   ├── api/           # API-Server (Endpunkte, WebSocket, Authentifizierung)
│   └── db/            # Datenbankmodelle und Migrationen
│
├── frontends/
│   ├── widget/        # Chat-Widget → widget.mein-kuechenexperte.de
│   └── dashboard/     # Admin-Dashboard → app.mein-kuechenexperte.de
│
├── tests/             # Automatisierte Tests
└── deploy/            # Server-Konfiguration und Deployment-Skripte
```

---

## Technologie (für Interessierte)

| Bereich | Technologie | Warum |
| ------- | ----------- | ----- |
| Backend | Python + FastAPI | Schnell, asynchron, ideal für KI-Anwendungen |
| Datenbank | PostgreSQL + pgvector | Relationale Daten + KI-Suche in einem System |
| KI-Modell | Anthropic Claude | Bestes Modell für Gespräche und eigenständiges Handeln |
| Embeddings | OpenAI | Günstige, bewährte Vektorisierung für Wissenssuche |
| Chat | WebSocket | Echtzeit-Kommunikation ohne Seitenneuladung |
| Widget | React + Vite | Kleines Bundle, läuft isoliert auf jeder Website |
| Dashboard | React + Tailwind | Moderne, wartbare Admin-Oberfläche |
| Hosting Backend | Hetzner (EU) | DSGVO-konform, zuverlässig, kosteneffizient |
| Hosting Frontend | Cloudflare Pages | Globales CDN, automatische SSL-Zertifikate, kostenlos |

---

## Lokales Setup (für Entwickler)

```bash
# 1. Repository klonen
git clone https://github.com/KonstantinData/KI-Mitarbeiter-Team-Kuechen-und-Moebelgeschaeft.git
cd KI-Mitarbeiter-Team-Kuechen-und-Moebelgeschaeft

# 2. Einmalig einrichten (Python venv + alle Abhängigkeiten)
./setup.sh

# 3. Umgebungsvariablen konfigurieren
cp .env.example .env
# .env öffnen und API-Keys eintragen

# 4. Datenbank einrichten
source venv/bin/activate
make migrate

# 5. Backend starten
make dev
# → http://localhost:8000/health
# → http://localhost:8000/docs (API-Dokumentation)

# 6. Widget bauen (optional)
cd frontends/widget && pnpm install && pnpm build

# 7. Dashboard bauen (optional)
cd frontends/dashboard && pnpm install && pnpm build
```

**Benötigt:** Python 3.12+, Node.js 20+, pnpm, PostgreSQL 16 mit pgvector

---

## Projektstatus

| Bereich | Status |
| ------- | ------ |
| Datenbankschema | Fertig |
| API-Grundgerüst | Fertig (Endpunkte als Platzhalter) |
| WebSocket-Chat | Fertig (Echo-Modus, noch kein Agent dahinter) |
| Agenten-Kern (Basis) | Fertig |
| Agenten-Vorlage | Fertig |
| Chat-Widget | Fertig, live auf `widget.mein-kuechenexperte.de` |
| Admin-Dashboard | Fertig, live auf `app.mein-kuechenexperte.de` |
| Agent Lisa | In Planung |
| Agent Max | In Planung |
| Agent Anna, Tom, Sara | In Planung |
| Google Calendar Integration | Vorbereitet, noch nicht aktiviert |
| E-Mail-Versand | Vorbereitet, noch nicht aktiviert |

---

## Kontakt

Dieses Projekt wird entwickelt von **Konstantin** im Rahmen des Aufbaus von [mein-kuechenexperte.de](https://www.mein-kuechenexperte.de).

Fragen, Feedback oder Interesse an einer Zusammenarbeit? → GitHub Issues oder direkt per E-Mail.
