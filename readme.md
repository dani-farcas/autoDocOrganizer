# 📂 AutoDocOrganizer

AutoDocOrganizer ist eine Anwendung zur **automatischen Verarbeitung, Ordnung und Verständlichmachung von Dokumenten** (PDF oder Bilddateien).  
Das System wurde als **MVP (Minimum Viable Product)** entwickelt und läuft aktuell lokal auf dem eigenen Rechner.

---

## 🎥 Demo-Videos

| Beschreibung | Link |
|--------------|------|
| Web-Oberfläche in Aktion – Dokument hochladen, OCR, automatische Ablage | [🎬 Demo ansehen](https://drive.google.com/file/d/1-Rud-y9tuBTz8WtOv__TNxC5bNl1b2Te/view?usp=drive_link) |
| Entwicklungsumgebung (VS Code) + Ordnerstruktur + Verarbeitungsschritte | [🎬 Demo ansehen](https://drive.google.com/file/d/1L1S3q-jxF4449hh9z20240Lbme23POMp/view?usp=drive_link) |


---

## ⚙️ Funktionsumfang (MVP-Status)

| Modul | Beschreibung |
|--------|---------------|
| **Dokumentenimport** | Upload im Browser oder automatisches Einlesen aus `ScansInbox/` |
| **OCR (Texterkennung)** | PDF- und Bildanalyse mit *Tesseract* + *Poppler* |
| **Automatische Ablage** | Sortiert nach Jahr und vermuteter Institution; Unklare → `_Unbekannt/` |
| **Indexierung** | Zentrale Übersicht über alle archivierten Dokumente |
| **Übersetzungen (optional)** | DeepL zur Übersetzung in verschiedene Sprachen |
| **Erklärungen (optional)** | Google Gemini für leicht verständliche Zusammenfassungen |
| **Webinterface** | Zugriff und Bedienung im Browser über *Flask* |

---

## 🗂️ Projektstruktur

```text
AutoDocOrganizer/
+-- config/           # Einstellungen (.env, settings.yml)
+-- src/
|   +-- app.py        # Flask Web-App
|   +-- main.py       # CLI-Batch-Verarbeitung
|   +-- ocr.py        # Texterkennung
|   +-- extract_institution.py
|   +-- translate.py  # DeepL-Integration (optional)
|   +-- explain.py    # Gemini-Erklärungen (optional)
|   +-- fileops.py    # Dateiverarbeitung / Ablage
|   \-- indexer.py    # Indexverwaltung
+-- ScansInbox/       # Eingehende Dokumente
+-- Archive/          # Sortierte Ablage
\-- requirements.txt  # Python-Abhängigkeiten
🧩 Systemarchitektur (UML)
📸 PNG-Version (immer sichtbar)




 Systemlogik (Kurz verständlich)
Dokument wird hochgeladen oder in ScansInbox/ gelegt

OCR → Volltext wird extrahiert

System erkennt Institution anhand von Schlüsselwörtern

Ablage erfolgt in → Archive/<Jahr>/<Institution>/

Eintrag wird im Index gespeichert

Rechtsklick auf Dokument → Translate / Explain möglich

 Geplante Weiterentwicklung
Feature	Ziel
Modernes UI (Material / Fluent Design)	Nutzerfreundlicheres & attraktives Interface
Drag & Drop Upload	Schneller Import ohne Dateidialog
Cloud-Sync (OneDrive / Google Drive)	Gemeinsame Nutzung in Teams
Direkte Scanner-Integration (TWAIN/SANE)	Papier → digital → automatisch einsortiert
Volltextsuche & Filter	Dokumente blitzschnell auffindbar
Responsive / Mobile Ready	Bedienbar auf Tablet & Smartphone

 Vorteile
✅ Reduziert manuellen Sortieraufwand
✅ Übersichtliche zentrale Dokumentenablage
✅ Verständliche KI-Erklärungen bei Behördenbriefen
✅ Skalierbar für Teams & Büros (z. B. Verwaltung, Steuerkanzlei, Arztpraxis)

 Fazit
AutoDocOrganizer ist ein funktionsfähiger Prototyp, der zeigt,
wie dokumentenintensive Abläufe automatisiert, vereinheitlicht und verständlich gemacht werden können.

Er dient als stabile Basis für den Ausbau zu einer professionellen Cloud-Lösung
mit moderner UI und optionaler Team- / Mobile-Nutzung.