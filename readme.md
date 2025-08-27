


🌍 Überblick

AutoDocOrganizer ist eine Web-Anwendung zur automatischen Verarbeitung von importierten Dokumenten (PDF oder Bilddateien).
Das System wurde als MVP (Minimum Viable Product) umgesetzt: Es ermöglicht bereits OCR, automatische Ablage, Übersetzung und Erklärung von Dokumenten.


🌐 Live-Demo

Die Anwendung ist auf unserem Testserver (AWS EC2, Ubuntu 24.04) dauerhaft eingerichtet und erreichbar unter:

👉 http://52.29.84.137/

(Der Server läuft unabhängig von VS Code; die Dienste nginx und autoDocOrganizer werden automatisch durch systemd gestartet.)


🎯 Funktionsumfang (MVP)

Import von Dokumenten: Upload im Webinterface oder Kopieren in ScansInbox/.

OCR (Texterkennung): Automatische Volltexterkennung aus PDFs/Bildern (Tesseract + Poppler).

Institutionserkennung: Ablage in Ordnern nach Jahr und Institution, sonst in _Unbekannt.

Indexierung: Zentrale Übersicht aller archivierten Dokumente.

Übersetzung: DeepL-Integration für Übersetzungen in wählbare Sprachen.

Erklärungen: Google Gemini-Integration für leicht verständliche Erklärungen.

Webzugriff: Bedienung über Browser dank Flask + Gunicorn + Nginx.

Kontextmenü (Rechtsklick): Auf jedes Dokument →

Translate → Sprache auswählen

Explain → Erklärung mit KI


🛠️ Architektur

AutoDocOrganizer/
├─ config/              # Einstellungen (.env, settings.yml)
├─ src/                 # Python-Code
│   ├─ main.py          # CLI-Modus (Batch-Verarbeitung)
│   ├─ app.py           # Flask-App (Webinterface)
│   ├─ ocr.py           # OCR mit Tesseract + Poppler
│   ├─ extract_institution.py
│   ├─ translate.py     # DeepL-Übersetzungen
│   ├─ explain.py       # Gemini-Erklärungen
│   ├─ fileops.py       # Dateimanagement
│   └─ indexer.py       # Indexverwaltung
├─ ScansInbox/          # Eingehende Dokumente
├─ Archive/             # Automatisch sortierte Ablage
└─ requirements.txt     # Python-Abhängigkeiten


## 🗂️ Systemarchitektur (UML)

### PNG-Version (garantiert sichtbar)
![UML Diagramm](https://raw.githubusercontent.com/dani-farcas/autoDocOrganizer/main/docs/architecture.png)

### SVG-Version (nur als Link)
[👉 UML Diagramm (SVG)](docs/architecture.svg)


🚀 Zukunft / Geplante Erweiterungen

Dies ist aktuell ein MVP. Für eine spätere Version sind folgende Erweiterungen vorgesehen:

🌐 Modernes UI: Benutzeroberfläche im Stil aktueller Web-Apps (Material Design / Microsoft 365).

📂 Drag & Drop Upload: Dokumente per Drag & Drop ins Browserfenster ziehen.

☁️ Cloud-Integration: Automatische Speicherung in OneDrive oder ähnlichen Cloud-Diensten, um nahtlos in bestehende Arbeitsumgebungen integriert zu werden.

📸 Scanner-Anbindung: Direkte Integration mit TWAIN/SANE für physische Scanner.

🔍 Suche & Filter: Volltextsuche in allen archivierten Dokumenten.

📱 Mobile App / Responsive Webdesign: Zugriff von Smartphone und Tablet.


✅ Vorteile

Automatische Ablage spart Zeit und verhindert Fehler.

Einfache Nutzung über Browser.

Sofortige Mehrsprachigkeit dank DeepL.

KI-Erklärungen erleichtern das Verständnis offizieller Schreiben.

Zukunftssicher durch geplante Erweiterungen (Cloud, modernes UI, Mobile).


📌 Fazit

AutoDocOrganizer ist ein voll funktionsfähiger Prototyp (MVP), der die Kernfunktionen bereits demonstriert.
Er eignet sich ideal als Grundlage für eine professionelle Weiterentwicklung in Richtung einer modernen Cloud-Lösung, die mit Microsoft 365 & OneDrive vergleichbar ist.