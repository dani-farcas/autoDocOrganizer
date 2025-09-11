# ==========================================================
# 🗂️ Indexverwaltung für AutoDocOrganizer
# Hält eine CSV-Liste aller archivierten Dateien fest:
#   Archive/index.csv
# ==========================================================

import os
import csv
from datetime import datetime

# 📌 Basis: Projekt/Archive/index.csv
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # src/
PROJECT_ROOT = os.path.dirname(BASE_DIR)               # AutoDocOrganizer/
ARCHIVE_DIR = os.path.join(PROJECT_ROOT, "Archive")
INDEX_FILE = os.path.join(ARCHIVE_DIR, "index.csv")

# Sicherstellen, dass Archiv-Ordner existiert
os.makedirs(ARCHIVE_DIR, exist_ok=True)


def update_index(file_path: str, year: str, institution: str):
    """
    Ergänzt die Index-Datei mit einer neuen Zeile.
    
    :param file_path: Vollständiger Pfad zur archivierten Datei
    :param year: Jahr (als String)
    :param institution: erkannte Institution
    """
    # Fallbacks
    if not year:
        year = str(datetime.now().year)
    if not institution or not str(institution).strip():
        institution = "Unklar"

    # Prüfen, ob Datei existiert
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ Datei nicht gefunden für Index: {file_path}")

    # CSV-Header
    header = ["Datei", "Jahr", "Institution", "Pfad", "Eingetragen am"]

    # Zeile für Index (Pfad relativ zum Archiv)
    row = [
        os.path.basename(file_path),         # Dateiname
        year,                                # Jahr
        institution,                         # Institution
        os.path.relpath(file_path, ARCHIVE_DIR),  # relativer Pfad
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Timestamp
    ]

    # Schreiben / Anhängen
    file_exists = os.path.exists(INDEX_FILE)
    with open(INDEX_FILE, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(row)

    print(f"📝 Index aktualisiert: {row}")


# 🧪 Testmodus
if __name__ == "__main__":
    test_file = os.path.join(ARCHIVE_DIR, "2025", "Finanzamt", "rechnung.pdf")
    try:
        update_index(test_file, "2025", "Finanzamt")
    except Exception as e:
        print(e)
