# LISA-TODO — Implementierungsplan

Basiert auf: `LISA-CheckIn-Agent.md`
Ziel: Stufe 1 + 2 als zusammenhängende Einheit — Lisa chattet UND handelt

---

## Phase 1: Vorbereitung & Struktur

- [x] `src/agents/lisa/` Verzeichnisstruktur anlegen
- [x] `src/agents/lisa/prompts/identity.py` — Identitätsblock (wer Lisa ist)
- [x] `src/agents/lisa/prompts/tonality.py` — Tonalitätsregeln (Sie, menschlich, zielorientiert)
- [x] `src/agents/lisa/prompts/rules.py` — Verhaltensregeln (was erlaubt/verboten ist)
- [x] `src/agents/lisa/studio_knowledge/mein_kuechenexperte.py` — Pilotstudio-Daten (editierbar)

## Phase 2: Tools

- [x] `src/agents/lisa/tools/extract_lead_data.py`
  - Wird von Lisa während des Gesprächs aufgerufen (bei JEDER neuen Info)
  - Erstellt/aktualisiert Lead in DB
  - Berechnet Lead-Score (Name +15, E-Mail +20, Telefon +15, Budget +20, Zeitrahmen +15, Stil +10, Raumgröße +5)
  - Verknüpft Conversation.lead_id mit dem Lead
  - Läuft unsichtbar im Hintergrund — Kunde merkt nichts
- [x] `src/agents/lisa/tools/book_appointment.py`
  - Stub: nimmt Terminwunsch entgegen, speichert als FollowUp
  - Google Calendar Integration folgt in einem späteren Schritt

## Phase 3: Agent

- [x] `src/agents/lisa/system_prompt.py` — baut den vollständigen System-Prompt aus Bausteinen
- [x] `src/agents/lisa/agent.py` — LisaAgent (erbt von BaseAgent)
  - `process_message()` — setzt Kontext für Tools, ruft dann super() auf
  - `get_tools()` — registriert Tools mit DB-Session-Injektion
  - `get_system_prompt()` — baut Prompt aus Bausteinen
  - `finalize_conversation()` — generiert Zusammenfassung bei Gesprächsende

## Phase 4: WebSocket-Integration

- [x] `src/api/websocket/chat_handler.py`
  - Echo-Modus ersetzt durch LisaAgent
  - DB-Commit nach jeder verarbeiteten Nachricht
  - `finalize_conversation()` bei WebSocketDisconnect aufrufen
  - Conversation wird nach Disconnect als "closed" markiert

---

## Nicht umgesetzt — externe Abhängigkeiten erforderlich

- [ ] **Google Calendar OAuth** — braucht Credentials + Studio-Einrichtung (`book_appointment` ist Stub)
- [ ] **E-Mail-Versand** (Terminbestätigungen) — braucht Resend API Key in `.env`
- [ ] **pgvector Wissensbasis befüllen** — braucht echte Studio-Inhalte; aktuell: Wissen steht direkt im System-Prompt
- [ ] **WhatsApp-Kanal** — Meta Business API, 2–4 Wochen Freischaltung (Stufe 2)
- [ ] **Multi-Studio-Onboarding** — Stufe 6, wenn Pilotphase abgeschlossen
- [ ] **Feedback-System** (Daumen hoch/runter) — Stufe 5

---

## Studio-Wissensdatei anpassen

Alle Studio-spezifischen Informationen stehen in:
```
src/agents/lisa/studio_knowledge/mein_kuechenexperte.py
```
Diese Datei kann ohne Python-Kenntnisse bearbeitet werden — alle Felder sind kommentiert.
Für jedes neue Studio wird eine neue Datei nach demselben Schema angelegt.
