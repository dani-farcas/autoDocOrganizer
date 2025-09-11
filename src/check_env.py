# ==========================================================
# 🛠️ check_env.py – Umgebungs-Check für OCR
# Prüft ob Tesseract + Poppler korrekt installiert sind
# ==========================================================

import os
import shutil
import pytesseract
from pdf2image import convert_from_path

# ----------------------------------------------------------
# 🔎 Tesseract prüfen
# ----------------------------------------------------------
print("=== 🔍 Tesseract Check ===")
tesseract_cmd = os.getenv("TESSERACT_CMD", "tesseract")
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

if shutil.which(tesseract_cmd):
    print(f"✅ Tesseract gefunden: {shutil.which(tesseract_cmd)}")
else:
    print("❌ Tesseract NICHT gefunden!")
    print("   → Bitte Pfad in Umgebungsvariable TESSERACT_CMD setzen.")


# ----------------------------------------------------------
# 🔎 Poppler prüfen
# ----------------------------------------------------------
print("\n=== 🔍 Poppler Check ===")
poppler_path = os.getenv("POPPLER_PATH")

if poppler_path and os.path.exists(poppler_path):
    print(f"✅ Poppler gefunden über Umgebungsvariable: {poppler_path}")
else:
    # Fallback: ./src/poppler/Library/bin
    base_dir = os.path.dirname(os.path.abspath(__file__))
    fallback = os.path.join(base_dir, "poppler", "Library", "bin")

    if os.path.exists(fallback):
        print(f"⚠️ Poppler nicht in ENV, aber gefunden im Projekt: {fallback}")
    else:
        print("❌ Poppler NICHT gefunden!")
        print("   → Bitte POPPLER_PATH setzen oder Poppler im Projekt entpacken.")


# ----------------------------------------------------------
# 🧪 Test-Konvertierung einer PDF-Seite (optional)
# ----------------------------------------------------------
test_pdf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.pdf")
if os.path.exists(test_pdf):
    print("\n=== 🧪 Test OCR PDF ===")
    try:
        pages = convert_from_path(test_pdf, poppler_path=poppler_path or fallback)
        if pages:
            print("✅ PDF → Bild-Konvertierung erfolgreich!")
        else:
            print("❌ PDF konnte nicht konvertiert werden.")
    except Exception as e:
        print(f"⚠️ Fehler bei Poppler-Test: {e}")
else:
    print("\nℹ️ Kein test.pdf gefunden → OCR-Test übersprungen.")
