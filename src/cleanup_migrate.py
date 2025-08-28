# ==========================================================
# 🧹 Cleanup & Migration Script (fix)
# Ziel: Verschiebt alte nummerierte Ordner (0001, 0002, ...)
# direkt ins aktuelle Jahr (immer datetime.now().year)
# ==========================================================

import os
import shutil
import re
from fileops import ARCHIVE_DIR, move_to_archive


def migrate_numbered_folders():
    """
    Findet alte nummerierte Ordner (0001, 0002, ...)
    und verschiebt deren Dateien ins Archiv unter:
    Archive/<aktuelles Jahr>/_Unklar/<Dateien>
    """
    for entry in os.listdir(ARCHIVE_DIR):
        path = os.path.join(ARCHIVE_DIR, entry)

        # 🎯 Nur Ordner mit führender Null (0001, 0002, ...)
        if os.path.isdir(path) and re.match(r"^0\d{3}$", entry):
            print(f"⚠️ Nummerierter Ordner gefunden: {path}")

            for root, _, files in os.walk(path):
                for fname in files:
                    old_file = os.path.join(root, fname)
                    print(f"   ➡️ migriere {old_file}")

                    # 📦 Verschiebe direkt nach <aktuelles Jahr>/_Unklar
                    new_path = move_to_archive(old_file, "_Unklar")
                    print(f"   ✅ verschoben nach {new_path}")

            # 🗑️ Am Ende alten Ordner löschen
            shutil.rmtree(path)
            print(f"🗑️ Ordner gelöscht: {path}")


if __name__ == "__main__":
    migrate_numbered_folders()
