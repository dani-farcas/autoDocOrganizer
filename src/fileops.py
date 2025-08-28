# ==========================================================
# 📂 Dateiverwaltung für AutoDocOrganizer
# Ziel: Desktop/AutoDocOrganizer/Archive/<Jahr>/<Institution>/<Datei>
# Logik: Immer aktuelles Jahr (Systemzeit), Dateiname bleibt unverändert
# ==========================================================

import os
import shutil
from datetime import datetime

# 📌 Basisverzeichnis = Desktop/AutoDocOrganizer/Archive
USER_HOME = os.path.expanduser("~")
DESKTOP_DIR = os.path.join(USER_HOME, "Desktop")
ARCHIVE_DIR = os.path.join(DESKTOP_DIR, "AutoDocOrganizer", "Archive")
INDEX_FILE = os.path.join(ARCHIVE_DIR, "index.csv")

# Stelle sicher, dass Hauptordner existiert
os.makedirs(ARCHIVE_DIR, exist_ok=True)


def move_to_archive(filepath: str, institution: str = "_Unklar") -> str:
    """
    Verschiebt eine Datei ins Archiv unter:
    Desktop/AutoDocOrganizer/Archive/<aktuelles Jahr>/<Institution>/<Datei>

    Args:
        filepath (str): Ursprünglicher Pfad zur Datei
        institution (str): Name der Institution (Standard = "_Unklar")

    Returns:
        str: Neuer Zielpfad im Archiv
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ Datei nicht gefunden: {filepath}")

    # Institution fallback
    if not institution or not str(institution).strip():
        institution = "_Unklar"

    # 📅 Immer aktuelles Jahr verwenden
    year = str(datetime.now().year)

    # Zielordner bauen
    target_dir = os.path.join(ARCHIVE_DIR, year, institution)
    os.makedirs(target_dir, exist_ok=True)

    # Ursprünglichen Dateinamen bestimmen
    filename = os.path.basename(filepath)
    base, ext = os.path.splitext(filename)
    target_path = os.path.join(target_dir, filename)

    # ⚡ Kollisionen auflösen → Datei (1).pdf, Datei (2).pdf
    counter = 1
    while os.path.exists(target_path):
        target_path = os.path.join(target_dir, f"{base} ({counter}){ext}")
        counter += 1

    # 🚚 Datei verschieben oder kopieren (falls blockiert)
    try:
        shutil.move(filepath, target_path)
        print(f"📦 Verschoben nach: {target_path}")
    except PermissionError:
        temp_target = target_path + ".part"
        shutil.copy2(filepath, temp_target)
        try:
            os.remove(filepath)
            os.rename(temp_target, target_path)
            print(f"⚠️ Datei blockiert, Kopie erstellt und umbenannt → {target_path}")
        except PermissionError:
            print(f"⚠️ Datei blockiert, nur Kopie gespeichert → {temp_target}")
            target_path = temp_target

    return target_path
