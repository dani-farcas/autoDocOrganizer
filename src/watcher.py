# ==========================================================
# 📂 Watcher für AutoDocOrganizer
# Überwacht ScansInbox und verschiebt neue Dateien direkt ins Archiv
# ==========================================================

import os
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from ocr import run_ocr
from extract_institution import extract_institution   # ⚡ Institutionserkennung
from fileops import move_to_archive
from indexer import update_index                      # 📒 Index aktualisieren

# 📌 Basisordner
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCANS_INBOX = os.path.join(BASE_DIR, os.getenv("SCANS_INBOX", "ScansInbox"))


class ScanHandler(FileSystemEventHandler):
    """Reagiert auf neue Dateien im ScansInbox-Ordner"""

    def on_created(self, event):
        if event.is_directory:
            return

        filepath = event.src_path
        print(f"📂 Neue Datei erkannt: {filepath}")

        try:
            # 1️⃣ OCR durchführen
            text = run_ocr(filepath)

            # 2️⃣ Institution erkennen (Fallback = "_Unklar")
            if not text or not text.strip():
                print("⚠️ Kein Text erkannt – wird als '_Unklar' archiviert")
                institution = "_Unklar"
            else:
                institution = extract_institution(text) or "_Unklar"

            # 3️⃣ Jahr bestimmen (Fallback = aktuelles Jahr)
            year = str(datetime.now().year)

            # 4️⃣ Datei direkt ins Archiv verschieben
            new_path = move_to_archive(filepath, institution, year)

            # 5️⃣ Index aktualisieren
            update_index(new_path, year, institution)

            print(f"✅ Verarbeitet: {new_path} ({institution})")

        except Exception as e:
            print(f"❌ Fehler beim Verarbeiten von {filepath}: {e}")


def start_watcher():
    """Startet den Watchdog-Observer für ScansInbox"""
    event_handler = ScanHandler()
    observer = Observer()
    observer.schedule(event_handler, SCANS_INBOX, recursive=False)
    observer.start()
    print(f"👀 Warte auf neue Dateien in {SCANS_INBOX} ...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    start_watcher()
