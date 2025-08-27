# ==========================================================
# Watcher für AutoDocOrganizer
# Überwacht ScansInbox und verschiebt neue Dateien ins Archiv
# ==========================================================

import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from ocr import extract_text_from_file
from extract_institution import detect_institution   # ⚡ Institutionserkennung
from fileops import move_to_archive
from indexer import update_index                     # 📒 Index aktualisieren

# Basisordner
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
            text = extract_text_from_file(filepath)
            if not text or not text.strip():
                print("⚠️ Kein Text erkannt – wird als 'Unklar' archiviert")
                institution = "Unklar"
            else:
                # 2️⃣ Institution erkennen
                institution = detect_institution(text) or "Unklar"

            # 3️⃣ Datei ins Archiv verschieben
            new_path = move_to_archive(filepath, institution)

            # 4️⃣ Index aktualisieren
            update_index(new_path, institution, text)

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
