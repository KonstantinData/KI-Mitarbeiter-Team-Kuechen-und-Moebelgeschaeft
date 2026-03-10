"""
Studio-Wissensdaten: Mein Küchenexperte
========================================

Diese Datei enthält alle Informationen, die Lisa über dieses Studio wissen muss.
Alle Felder können direkt bearbeitet werden — kein technisches Wissen nötig.

Für ein neues Studio: Diese Datei kopieren, umbenennen (z.B. studio_mueller.py)
und alle Felder anpassen.
"""

STUDIO_KNOWLEDGE: dict = {
    # ─── Kontaktdaten ──────────────────────────────────────────────────────────
    "name": "Mein Küchenexperte",
    "adresse": "Musterstraße 1, 12345 Musterstadt",  # ← Bitte anpassen
    "telefon": "+49 123 456789",                     # ← Bitte anpassen
    "email": "info@mein-kuechenexperte.de",
    "website": "https://www.mein-kuechenexperte.de",

    # ─── Öffnungszeiten ────────────────────────────────────────────────────────
    "oeffnungszeiten": (
        "Montag–Freitag: 09:00–18:00 Uhr\n"
        "Samstag:        10:00–16:00 Uhr\n"
        "Sonntag:        geschlossen"
    ),

    # ─── Anfahrt & Parken ──────────────────────────────────────────────────────
    "anfahrt": (
        "Parkplätze direkt vor dem Haus vorhanden. "
        "Mit öffentlichen Verkehrsmitteln: Bus-Linie X, Haltestelle 'Musterstraße'."
    ),  # ← Bitte anpassen

    # ─── Sortiment & Marken ────────────────────────────────────────────────────
    "marken": [
        "Nobilia",
        "Nolte",
        "Häcker",
        "Schüller",
        # Weitere Marken hier eintragen
    ],

    "stilrichtungen": [
        "Modern / grifflos",
        "Landhaus / klassisch",
        "Minimalistisch / puristisch",
        "Industriestil",
        # Weitere Stilrichtungen hier eintragen
    ],

    "preisbereich": (
        "Einstieg ab ca. 8.000 EUR (einfach ausgestattet). "
        "Typische Familienküche: 15.000–30.000 EUR inkl. Geräte und Montage. "
        "Premiumküchen und Maßanfertigungen: ab 40.000 EUR."
    ),

    # ─── Berater ───────────────────────────────────────────────────────────────
    "berater": [
        {
            "name": "Herr Müller",                          # ← Bitte anpassen
            "spezialisierung": "Moderne Küchen, Premiumsegment",
            "kalender_id": None,  # Google Calendar ID — wird später eingetragen
        },
        # Weitere Berater hier eintragen:
        # {
        #     "name": "Frau Schmidt",
        #     "spezialisierung": "Landhausküchen, Maßanfertigung",
        #     "kalender_id": None,
        # },
    ],

    # ─── Beratungstermin ───────────────────────────────────────────────────────
    "beratungstermin_dauer_minuten": 90,
    "beratungstermin_info": (
        "Beim Beratungsgespräch planen wir Ihre Küche direkt in 3D. "
        "Bitte bringen Sie wenn möglich Maße Ihres Raums und Fotos mit."
    ),

    # ─── Häufige Fragen (FAQ) ──────────────────────────────────────────────────
    "faq": [
        {
            "frage": "Wie lange dauert es von der Planung bis zur Lieferung?",
            "antwort": (
                "Von der finalen Planung bis zur Montage rechnen wir in der Regel "
                "8–12 Wochen. Bei Sonderwünschen oder Maßanfertigungen kann es "
                "etwas länger dauern."
            ),
        },
        {
            "frage": "Was kostet eine Küche?",
            "antwort": (
                "Das hängt stark von Größe, Ausstattung und Hersteller ab. "
                "Einstiegsküchen gibt es ab ca. 8.000 EUR, eine gut ausgestattete "
                "Familienküche liegt meist zwischen 15.000 und 30.000 EUR. "
                "Beim Beratungsgespräch erstellen wir eine genaue Kalkulation."
            ),
        },
        {
            "frage": "Liefern und montieren Sie auch?",
            "antwort": (
                "Ja, wir übernehmen Anlieferung und komplette Montage — "
                "inklusive Anschluss der Elektrogeräte und Wasseranschlüsse."
            ),
        },
        {
            "frage": "Kann ich in Raten zahlen?",
            "antwort": (
                "Ja, wir bieten Finanzierungsmöglichkeiten an. "
                "Details besprechen wir gerne beim Beratungsgespräch."
            ),
        },
        {
            "frage": "Nehmt ihr auch die alte Küche ab?",
            "antwort": (
                "Ja, Demontage und Entsorgung der alten Küche sind "
                "auf Anfrage möglich."
            ),
        },
        {
            "frage": "Kann ich Referenzküchen besichtigen?",
            "antwort": (
                "Ja, nach Absprache können Referenzobjekte besichtigt werden. "
                "Sprechen Sie uns beim Beratungstermin darauf an."
            ),
        },
        # Weitere FAQs hier eintragen
    ],

    # ─── Aktuelle Aktionen ─────────────────────────────────────────────────────
    "aktuelle_aktionen": [
        # Beispiel: "10 % Rabatt auf alle Nobilia-Küchen bis 31. März 2026"
        # Einfach Zeile einkommentieren und Text anpassen:
    ],

    # ─── Besonderheiten ────────────────────────────────────────────────────────
    "besonderheiten": (
        "- 3D-Planung direkt im Beratungsgespräch\n"
        "- Küchen auch für Gewerbe (Ferienwohnungen, Büros)\n"
        "- Referenzobjekte nach Absprache besichtigbar"
    ),

    # ─── Lisa-Verhalten ────────────────────────────────────────────────────────
    # Darf Lisa konkrete Preise nennen?
    # False = nur Richtwerte nennen, konkretes Angebot nur beim Termin
    "preise_nennen": False,
}


def get_studio_context_text() -> str:
    """
    Gibt alle Studio-Informationen als formatierten Text zurück.
    Wird direkt in den System-Prompt von Lisa eingefügt.
    """
    s = STUDIO_KNOWLEDGE

    marken = ", ".join(s["marken"]) if s["marken"] else "auf Anfrage"
    stile = ", ".join(s["stilrichtungen"]) if s["stilrichtungen"] else ""
    berater_namen = (
        ", ".join(b["name"] for b in s["berater"]) if s["berater"] else "auf Anfrage"
    )
    aktionen = (
        "\n".join(f"- {a}" for a in s["aktuelle_aktionen"])
        if s["aktuelle_aktionen"]
        else "Aktuell keine besonderen Aktionen."
    )
    faq_text = "\n\n".join(
        f"F: {f['frage']}\nA: {f['antwort']}" for f in s["faq"]
    )

    return f"""## Dein Studio: {s["name"]}

**Adresse:** {s["adresse"]}
**Telefon:** {s["telefon"]}
**E-Mail:** {s["email"]}

**Öffnungszeiten:**
{s["oeffnungszeiten"]}

**Anfahrt:** {s["anfahrt"]}

**Marken & Hersteller:** {marken}
**Stilrichtungen:** {stile}

**Preisbereich:** {s["preisbereich"]}

**Berater:** {berater_namen}
**Beratungstermin:** {s["beratungstermin_dauer_minuten"]} Minuten — {s["beratungstermin_info"]}

**Aktuelle Aktionen:**
{aktionen}

**Häufige Fragen:**
{faq_text}

**Besonderheiten:**
{s["besonderheiten"]}"""
