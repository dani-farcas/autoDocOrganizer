# ==========================================================
# OCR-Modul für AutoDocOrganizer
# Nutzt Tesseract für Bilder + Poppler (pdf2image) für PDFs
# ==========================================================

import os
from typing import Optional
from PIL import Image
import pytesseract
from pdf2image import convert_from_path

# 🟢 Tesseract-Executable suchen (Standard: Windows)
DEFAULT_TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSERACT_CMD = os.getenv("TESSERACT_CMD", DEFAULT_TESSERACT)

if os.path.exists(TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
else:
    print(f"⚠️  Achtung: Tesseract nicht gefunden unter {TESSERACT_CMD}. "
          f"Bitte Umgebungsvariable TESSERACT_CMD setzen!")

def run_ocr(filepath: str, lang: str = "deu+eng") -> Optional[str]:
    """
    Führt OCR auf einer Datei (PDF oder Bild) aus.
    
    :param filepath: Pfad zur Datei (PDF oder Bild)
    :param lang: Sprachpakete für Tesseract (Standard: Deutsch + Englisch)
    :return: Extrahierter Text oder None bei Fehler
    """
    if not os.path.exists(filepath):
        print(f"❌ Datei nicht gefunden: {filepath}")
        return None

    text = ""

    try:
        if filepath.lower().endswith(".pdf"):
            # 📄 PDF → Seiten in Bilder konvertieren → OCR
            pages = convert_from_path(filepath)
            for page in pages:
                text += pytesseract.image_to_string(page, lang=lang) + "\n"

        else:
            # 🖼️ Direktes Bild → OCR
            img = Image.open(filepath)
            text = pytesseract.image_to_string(img, lang=lang)

        return text.strip()

    except Exception as e:
        print(f"❌ Fehler bei OCR ({filepath}): {e}")
        return None


# 🟢 Alias für Kompatibilität mit app.py
extract_text_from_file = run_ocr


# 🧪 Testmodus: Direktes Ausführen
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        f = sys.argv[1]
        print("📄 OCR-Ergebnis:\n")
        print(run_ocr(f))
    else:
        print("⚠️ Bitte Datei angeben, z.B.: python src/ocr.py ScansInbox/test.pdf")
