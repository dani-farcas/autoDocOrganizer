import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

POPPLER_PATH = r"C:\poppler\Library\bin"
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def run_ocr(filepath: str) -> str:
    text = ""
    try:
        if filepath.lower().endswith(".pdf"):
            images = convert_from_path(filepath, poppler_path=POPPLER_PATH)
            for img in images:
                img = img.convert("L")  # grayscale
                img = img.point(lambda x: 0 if x < 150 else 255, '1')  # binarizare pentru claritate
                text += pytesseract.image_to_string(img, lang="deu+eng+ron") + "\n"
        else:
            img = Image.open(filepath).convert("L")
            img = img.point(lambda x: 0 if x < 150 else 255, '1')
            text = pytesseract.image_to_string(img, lang="deu+eng+ron")
    except Exception as e:
        print(f"❌ Fehler bei OCR ({filepath}): {e}")
        return ""

    return text.strip()

