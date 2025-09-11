# ==========================================================
# 📂 Dateiverwaltung für AutoDocOrganizer
# Verschiebt erkannte Dokumente ins Projektarchiv:
#   Archive/<Jahr>/<Institution>/
# ==========================================================

import os
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # src/
PROJECT_ROOT = os.path.dirname(BASE_DIR)               # AutoDocOrganizer/
ARCHIVE_DIR = os.path.join(PROJECT_ROOT, "Archive")

os.makedirs(ARCHIVE_DIR, exist_ok=True)

def move_to_archive(filepath: str, institution: str = "Unklar") -> str:
    """Verschiebt eine Datei ins Archiv: Archive/<Jahr>/<Institution>/"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ Datei nicht gefunden: {filepath}")

    if not institution or not str(institution).strip():
        institution = "Unklar"

    safe_institution = "".join(c for c in institution if c.isalnum() or c in (" ", "_", "-")).strip()
    if not safe_institution:
        safe_institution = "Unklar"

    year = str(datetime.now().year)

    target_dir = os.path.join(ARCHIVE_DIR, year, safe_institution)
    os.makedirs(target_dir, exist_ok=True)

    filename = os.path.basename(filepath)
    target_path = os.path.join(target_dir, filename)

    counter = 1
    base, ext = os.path.splitext(filename)
    while os.path.exists(target_path):
        target_path = os.path.join(target_dir, f"{base}_{counter}{ext}")
        counter += 1

    shutil.move(filepath, target_path)
    print(f"📦 Verschoben nach: {target_path}")
    return target_path
