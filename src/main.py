# 📁 src/main.py
import os
from ocr import run_ocr
from extract_institution import extract_institution
from fileops import move_to_archive
from indexer import update_index
from translate import translate_text

SCANS_INBOX = "ScansInbox"

def process_file(file_path: str):
    """
    Führt den kompletten Workflow für eine Datei aus:
    OCR → Institution → Verschieben → Index → Übersetzung (Sprache pro Datei wählbar).
    """
    print(f"\n📂 Verarbeite Datei: {file_path}")

    # 1) OCR
    text = run_ocr(file_path)

    # 2) Institution erkennen
    institution = extract_institution(text)
    print(f"🏢 Erkannte Institution: {institution}")

    # 3) Datei verschieben
    new_path = move_to_archive(file_path, institution)
    print(f"📦 Verschoben nach: {new_path}")

    # 4) Index aktualisieren
    result = update_index(new_path, institution)
    print(result)

    # 5) Übersetzung – Benutzer wählt Sprache pro Datei
    if text.strip():
        print("\nVerfügbare Sprachen: EN-GB, EN-US, DE, FR, IT, ES, RO ...")
        target_lang = input("➡️ Bitte gewünschte Zielsprache eingeben (Enter = keine Übersetzung): ").strip()

        if target_lang:
            translated = translate_text(text, "DE", target_lang)
            if not translated.startswith("❌"):
                base, _ = os.path.splitext(new_path)
                translated_file = f"{base}_übersetzt_{target_lang}.txt"
                with open(translated_file, "w", encoding="utf-8") as f:
                    f.write(translated)
                print(f"🌍 Übersetzung gespeichert unter: {translated_file}")
            else:
                print(translated)  # Fehlermeldung
        else:
            print("⚠️ Keine Übersetzung gewählt.")
    else:
        print("⚠️ Kein Text für Übersetzung gefunden.")


def main():
    print("🚀 AutoDocOrganizer gestartet...")

    # Alle Dateien im ScansInbox verarbeiten
    for filename in os.listdir(SCANS_INBOX):
        file_path = os.path.join(SCANS_INBOX, filename)
        if os.path.isfile(file_path):
            process_file(file_path)

if __name__ == "__main__":
    main()
