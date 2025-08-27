# ==========================================================
# Indexer für AutoDocOrganizer
# Schreibt Metadaten aller archivierten Dokumente in index.csv
# ==========================================================

import os
import csv
from datetime import datetime

# 📌 Basisordner für das Archiv
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ARCHIVE_DIR = os.path.join(BASE_DIR, "Archive")
INDEX_FILE = os.path.join(ARCHIVE_DIR, "index.csv")


def update_index(file_path: str, institution: str, text: str):
    """
    Aktualisiert den Index mit Informationen zum neuen Dokument.

    :param file_path: Absoluter Pfad zur archivierten Datei
    :param institution: erkannte Institution
    :param text: OCR-Text (komplett oder Auszug)
    """
    # ⚡ Relativen Pfad ab "Archive/" ermitteln
    rel_path = file_path.split("Archive", 1)[-1].lstrip(os.sep)
    rel_path = os.path.join("Archive", rel_path)

    # Nur Auszug der ersten 200 Zeichen speichern
    excerpt = (text[:200] + "...") if text and len(text) > 200 else (text or "")

    # Metadaten
    row = {
        "Datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Institution": institution,
        "Dateiname": os.path.basename(file_path),
        "Pfad": rel_path,
        "Textauszug": excerpt.replace("\n", " ").strip()
    }

    # Falls Datei neu → Header schreiben
    write_header = not os.path.exists(INDEX_FILE)

    with open(INDEX_FILE, mode="a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys(), delimiter=";")
        if write_header:
            writer.writeheader()
        writer.writerow(row)

    print(f"📝 Index aktualisiert für {row['Dateiname']} ({institution})")


# 🧪 Test
if __name__ == "__main__":
    dummy_path = os.path.join(ARCHIVE_DIR, "2025", "Unklar", "test.pdf")
    dummy_text = "Dies ist ein Beispieltext für OCR und Indexer. Enthält ein paar Worte über das Finanzamt."
    update_index(dummy_path, "Finanzamt", dummy_text)
