# 📥 Import-Modul für AutoDocOrganizer
# Ermöglicht es, bestehende Dateien vom PC zu importieren
# und direkt durch den Verarbeitungs-Workflow zu schicken.

import os
from ocr import run_ocr
from extract_institution import detect_institution
from fileops import archive_file
from indexer import update_index

def import_file(filepath: str):
    if not os.path.exists(filepath):
        print(f"❌ Datei nicht gefunden: {filepath}")
        return
    
    print(f"📥 Importierte Datei: {filepath}")
    text = run_ocr(filepath)
    inst = detect_institution(text)
    archive_path = archive_file(filepath, inst)
    update_index(archive_path, inst, text)
    print("✅ Import abgeschlossen.")

if __name__ == "__main__":
    # Beispiel: direkt testen
    testfile = input("Gib den Pfad zur Datei ein: ")
    import_file(testfile.strip('"'))
