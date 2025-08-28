# 📥 Import-Modul für AutoDocOrganizer
# Ermöglicht es, bestehende Dateien vom PC zu importieren
# und direkt durch den Verarbeitungs-Workflow zu schicken.

import os
from datetime import datetime
from ocr import run_ocr
from extract_institution import extract_institution   # ⚡ vereinheitlicht
from fileops import move_to_archive
from indexer import update_index

def import_file(filepath: str):
    if not os.path.exists(filepath):
        print(f"❌ Datei nicht gefunden: {filepath}")
        return
    
    print(f"📥 Importierte Datei: {filepath}")
    text = run_ocr(filepath)

    # 🏢 Institution erkennen (Fallback = "_Unklar")
    inst = extract_institution(text) or "_Unklar"

    # 📅 Jahr bestimmen (Fallback = aktuelles Jahr)
    year = str(datetime.now().year)
    for token in text.split():
        if token.isdigit() and len(token) == 4:
            year = token
            break

    # 📦 Datei direkt ins strukturierte Archiv verschieben
    archive_path = move_to_archive(filepath, inst, year)

    # 📝 Index aktualisieren
    update_index(archive_path, year, inst)

    print(f"✅ Import abgeschlossen → {archive_path}")

if __name__ == "__main__":
    # Beispiel: direkt testen
    testfile = input("Gib den Pfad zur Datei ein: ")
    import_file(testfile.strip('"'))
