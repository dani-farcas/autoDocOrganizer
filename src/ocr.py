# ==========================================================
# 📄 ocr.py – OCR Modul für AutoDocOrganizer
# Zuständig für Texterkennung mit Tesseract + Poppler
# ==========================================================

import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

# ----------------------------------------------------------
# 🔧 Pfad-Konfiguration
# ----------------------------------------------------------
# Poppler: Erst aus Umgebungsvariable, sonst lokaler Fallback
POPPLER_PATH = os.getenv("POPPLER_PATH")
if not POPPLER_PATH:
    # Lokaler Fallback (z. B. entpackt unter ./poppler/Library/bin)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    POPPLER_PATH = os.path.join(BASE_DIR, "poppler", "Library", "bin")

# Tesseract: Standard = "tesseract" im PATH oder via Umgebungsvariable
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "tesseract")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


# ----------------------------------------------------------
# 🧾 OCR Hauptfunktion
# ----------------------------------------------------------
def run_ocr(filepath: str) -> str:
    """
    Führt OCR auf PDF- oder Bilddateien aus.
    - PDF → Bilder extrahieren mit Poppler
    - Bilder → direkt Tesseract OCR
    Rückgabe: erkannter Text (Deutsch + Englisch kombiniert)
    """
    text = ""
    try:
        if filepath.lower().endswith(".pdf"):
            # PDF in Bilder umwandeln
            images = convert_from_path(filepath, poppler_path=POPPLER_PATH)
            for img in images:
                text += pytesseract.image_to_string(img, lang="deu+eng") + "\n"
        else:
            # Normales Bild
            img = Image.open(filepath)
            text = pytesseract.image_to_string(img, lang="deu+eng")
    except Exception as e:
        print(f"❌ Fehler bei OCR ({filepath}): {e}")
        return ""

    return text.strip()
