📄 README.md
# 📂 AutoDocOrganizer

AutoDocOrganizer ist eine Python-basierte Anwendung, die automatisch gescannte Dokumente verarbeitet, per OCR lesbar macht, die Institution des Absenders erkennt, und die Dateien in einer klaren Archivstruktur ablegt.  
Über ein Web-Frontend (Flask) können Dokumente hochgeladen, angezeigt, übersetzt und durch KI erklärt werden.

---

## 🎯 Ziele des Projekts
- **Automatisierte Dokumentenorganisation**: Eingehende Scans werden automatisch analysiert.
- **OCR-Verarbeitung**: PDFs und Bilder werden mit Tesseract + Poppler in durchsuchbaren Text umgewandelt.
- **Institutionserkennung**: Die Absender-Institution wird heuristisch aus dem Dokumenttext extrahiert.
- **Strukturierte Ablage**: Dokumente werden in `Archive/<Jahr>/<Institution>/` verschoben.
- **Indexierung**: Jedes Dokument wird in `Archive/index.csv` registriert (Datum, Institution, Dateiname, Textauszug).
- **Web-Interface**: Einfache Bedienung über Browser (Upload, Navigation, Translate, Explain).
- **KI-Integration**: Dokumente können in andere Sprachen übersetzt und inhaltlich erklärt werden.

---

## 📦 Projektstruktur


AutoDocOrganizer/
├─ config/ # Konfiguration (.env, Settings)
├─ src/ # Quellcode
│ ├─ web.py # Flask-Weboberfläche
│ ├─ ocr.py # OCR-Funktionalität (Tesseract, pdf2image)
│ ├─ extract_institution.py # Institutionserkennung
│ ├─ fileops.py # Dateioperationen (Verschieben ins Archiv)
│ ├─ indexer.py # Indexverwaltung (CSV)
│ ├─ translate_ai.py # Übersetzungen (DeepL API)
│ ├─ explain_ai.py # Erklärungen (OpenAI GPT oder Fallback)
│ └─ watcher.py # (optional) Ordnerüberwachung
├─ templates/
│ └─ index.html # Web-UI (Upload, Ordnernavigation, Buttons)
├─ ScansInbox/ # Eingangsscans (temporär)
├─ Archive/ # Archiv mit Jahres- und Institutionsordnern
└─ requirements.txt # Abhängigkeiten


---

## ⚙️ Installation

### Voraussetzungen
- Python 3.10+  
- Tesseract OCR (muss installiert sein, Pfad in `ocr.py` konfigurierbar)  
- Poppler (für `pdf2image`)  

### Python-Abhängigkeiten
```bash
pip install -r requirements.txt

.env Konfiguration

Im Hauptverzeichnis .env anlegen:

# DeepL API Key (für Übersetzungen)
DEEPL_API_KEY=xxxxxxxxxxxxxxxx

# OpenAI API Key (für KI-Erklärungen)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx

# OCR / Projektpfade
SCANS_INBOX=ScansInbox
ARCHIVE_FOLDER=Archive
DEFAULT_LANG=DE
TARGET_LANG=EN

🚀 Nutzung
Server starten
cd src
python web.py

Zugriff im Browser

Öffne: http://127.0.0.1:5000

Funktionen

Upload: Neue Dateien hochladen (ScansInbox/)

Archivierung: Automatische Ablage in Archive/<Jahr>/<Institution>

Ordnernavigation: Klickbare Ordneransicht im Browser

Translate: Übersetzt den Text (DeepL API)

Explain: Erstellt eine leicht verständliche Erklärung des Inhalts (OpenAI GPT oder Fallback)

📚 Beispielablauf

PDF in der Weboberfläche hochladen.

OCR liest den Inhalt aus.

Institutionserkennung bestimmt den Absender.

Datei wird verschoben in:

Archive/2025/Warenhandel Dick e.K/Rechnung_123.pdf


Indexeintrag in Archive/index.csv.

Im Browser → Datei auswählen → Translate (Übersetzung) oder Explain (KI-Erklärung).

🔮 Geplante Erweiterungen

Fallback-KI lokal: HuggingFace-Modelle nutzen, wenn OpenAI-Quota erschöpft ist.

Suchfunktion: Volltextsuche über alle archivierten Dokumente.

Searchable PDFs: OCR-Ergebnis direkt in das PDF einbetten (ocrmypdf).

DSGVO-Modus: Automatische Anonymisierung sensibler Daten.

Mobile Uploads: Direkter Upload über Smartphone-App.

Mehrsprachige Oberfläche: UI in Deutsch, Englisch, Französisch.

👨‍🏫 Projekthintergrund

Dieses Projekt entstand im Rahmen einer Studienarbeit / eines Kurses, mit den Zielen:

Anwendung von OCR-Technologien (Tesseract, Poppler).

Nutzung von Python & Flask für Prototyp-Webanwendungen.

Integration externer KI-APIs (DeepL, OpenAI).

Saubere Softwarearchitektur mit Modulen und Konfigurationen.

Dokumentation und Präsentation auf professionellem Niveau.

👨‍💻 Autor

Daniel Farcas

Hochschule: [Name einsetzen]

Kurs: [z. B. „Softwareprojekt Anwendungsentwicklung“]

Jahr: 2025