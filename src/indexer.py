# ==========================================================
# 📝 Indexverwaltung für AutoDocOrganizer
# Speichert Metadaten aller archivierten Dateien in index.csv
# Logik: Jahr = immer aktuelles Jahr (datetime.now().year)
# ==========================================================

import csv
import os
from datetime import datetime
from fileops import INDEX_FILE


def update_index(filepath: str, institution: str):
    """
    Fügt einen Eintrag in index.csv hinzu oder aktualisiert ihn.
    Jahr wird immer automatisch aus Systemzeit ermittelt.
    """
    fieldnames = ["Datei", "Jahr", "Institution", "Pfad"]

    rows = []
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Prüfen ob Header korrekt ist, sonst Index zurücksetzen
            if reader.fieldnames != fieldnames:
                print("⚠️ Index-Datei beschädigt, wird neu erstellt...")
                rows = []
            else:
                rows = list(reader)

    filename = os.path.basename(filepath)

    # 📅 Immer aktuelles Jahr verwenden
    year = str(datetime.now().year)

    new_row = {
        "Datei": filename,
        "Jahr": year,
        "Institution": institution if institution else "_Unklar",
        "Pfad": filepath
    }

    # Alte Einträge mit gleichem Dateinamen + Pfad entfernen
    rows = [row for row in rows if not (row.get("Datei") == filename and row.get("Pfad") == filepath)]

    # Neuen Eintrag hinzufügen
    rows.append(new_row)

    # Datei neu schreiben
    with open(INDEX_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"📝 Index aktualisiert: {new_row}")


def read_index():
    """
    Liest alle Einträge aus index.csv.
    Returns:
        list[dict]: Liste aller Index-Einträge
    """
    fieldnames = ["Datei", "Jahr", "Institution", "Pfad"]

    if not os.path.exists(INDEX_FILE):
        return []

    with open(INDEX_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Prüfen ob Header korrekt ist
        if reader.fieldnames != fieldnames:
            print("⚠️ Ungültiges Index-Format, leere Liste zurückgegeben")
            return []

        return list(reader)
