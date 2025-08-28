# ==========================================================
# Indexverwaltung für AutoDocOrganizer
# Hält eine CSV-Liste aller archivierten Dateien fest
# ==========================================================

import os
import csv
from datetime import datetime

# 📌 Ziel: Desktop/AutoDocOrganizer/index.csv
USER_HOME = os.path.expanduser("~")
DESKTOP_DIR = os.path.join(USER_HOME, "Desktop")
ARCHIVE_DIR = os.path.join(DESKTOP_DIR, "AutoDocOrganizer")
INDEX_FILE = os.path.join(ARCHIVE_DIR, "index.csv")

# Sicherstellen, dass Basisordner existiert
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

    # Falls Datei nicht existiert → Exception
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ Datei nicht gefunden für Index: {file_path}")

    # CSV-Header
    header = ["Datei", "Jahr", "Institution", "Pfad", "Eingetragen am"]

    # Zeile für Index
    row = [
        os.path.basename(file_path),
        year,
        institution,
        file_path,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
