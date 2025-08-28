import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

# Citește din variabile de mediu (fallback = None)
POPPLER_PATH = os.getenv("POPPLER_PATH", None)
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "tesseract")

# Setează calea Tesseract (Windows/Linux)
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def run_ocr(filepath: str) -> str:
    """
    Führt OCR auf PDF- oder Bilddateien aus.
    Nutzt Poppler (für PDF) und Tesseract (für OCR).
    """
    text = ""
    try:
        if filepath.lower().endswith(".pdf"):
            images = convert_from_path(filepath, poppler_path=POPPLER_PATH)
            for img in images:
                text += pytesseract.image_to_string(img, lang="deu+eng") + "\n"
        else:
            img = Image.open(filepath)
            text = pytesseract.image_to_string(img, lang="deu+eng")
    except Exception as e:
        print(f"❌ Fehler bei OCR ({filepath}): {e}")
        return ""

    return text.strip()
