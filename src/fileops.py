# ==========================================================
# Dateiverwaltung für AutoDocOrganizer
# Verschiebt erkannte Dokumente ins Archiv (Desktop/<Jahr>/<Institution>)
# ==========================================================

import os
import shutil
from datetime import datetime

# Basisverzeichnis = Desktop/AutoDocOrganizer
USER_HOME = os.path.expanduser("~")
DESKTOP_DIR = os.path.join(USER_HOME, "Desktop")
ARCHIVE_DIR = os.path.join(DESKTOP_DIR, "AutoDocOrganizer")


def move_to_archive(filepath: str, institution: str = "Unklar") -> str:
    """
    Verschiebt eine Datei ins Archiv unter Desktop/AutoDocOrganizer/<Jahr>/<Institution>/
    
    :param filepath: Ursprünglicher Pfad (z.B. ScansInbox/xyz.pdf)
    :param institution: erkannte Institution (Standard: Unklar)
    :return: Neuer Zielpfad im Archiv
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ Datei nicht gefunden: {filepath}")

    # 🛡️ Fallback, falls Institution leer oder None
    if not institution or not str(institution).strip():
        institution = "Unklar"

    # Jahr aus aktuellem Datum bestimmen
    year = str(datetime.now().year)

    # Zielordner bestimmen: Desktop/AutoDocOrganizer/<Jahr>/<Institution>
    target_dir = os.path.join(ARCHIVE_DIR, year, institution)
    os.makedirs(target_dir, exist_ok=True)

    # Zieldateipfad
    filename = os.path.basename(filepath)
    target_path = os.path.join(target_dir, filename)

    # Falls Datei schon existiert → eindeutigen Namen erzeugen
    counter = 1
    base, ext = os.path.splitext(filename)
    while os.path.exists(target_path):
        target_path = os.path.join(target_dir, f"{base}_{counter}{ext}")
        counter += 1

    # Datei verschieben
    shutil.move(filepath, target_path)

    print(f"📦 Verschoben nach: {target_path}")
    return target_path


# 🧪 Testmodus: Direktes Ausführen
if __name__ == "__main__":
    test_file = os.path.join(USER_HOME, "ScansInbox", "test.pdf")
    try:
        new_path = move_to_archive(test_file, "Finanzamt")
        print(f"✅ Datei verschoben: {new_path}")
    except Exception as e:
        print(e)
