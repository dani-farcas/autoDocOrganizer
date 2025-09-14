# ==========================================================
# 🔎 OCR Modul – AutoDocOrganizer
# Unterstützt PDF (Poppler) und Bilder (Tesseract)
# ==========================================================

import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# Poppler-Path (für EC2 Ubuntu ist es /usr/bin)
POPPLER_PATH = "/usr/bin"

# ==========================================================
# 📄 OCR Funktion
# ==========================================================
def run_ocr(file_path: str) -> str:
    """
    Führt OCR auf einer Datei aus (PDF oder Bild).
    Gibt erkannten Text zurück.
    """

    if not os.path.exists(file_path):
        return "❌ Datei nicht gefunden."

    text = ""

    try:
        # 1️⃣ PDF-Dateien
        if file_path.lower().endswith(".pdf"):
            pages = convert_from_path(file_path, dpi=300, poppler_path=POPPLER_PATH)
            for page in pages:
                text += pytesseract.image_to_string(page, lang="deu+eng")

        # 2️⃣ Bild-Dateien
        elif file_path.lower().endswith((".png", ".jpg", ".jpeg", ".tif", ".bmp")):
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img, lang="deu+eng")

        else:
            return "⚠️ Dateityp wird nicht unterstützt."

    except Exception as e:
        return f"❌ Fehler bei OCR ({file_path}): {str(e)}"

    return text.strip()
