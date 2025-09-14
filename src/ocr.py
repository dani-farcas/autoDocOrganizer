# ==========================================================
# 📂 OCR-Modul für AutoDocOrganizer
# Verantwortlich für Texterkennung aus PDF- und Bilddateien
# Nutzt: Tesseract (OCR) + Poppler (PDF → Bilder)
# ==========================================================

import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

# ----------------------------------------------------------
# 🔧 Pfad-Konfiguration
# ----------------------------------------------------------

# Poppler: Standard-Pfad unter Linux (z. B. /usr/bin)
# Falls eine Umgebungsvariable gesetzt ist → diese nutzen
POPPLER_PATH = os.getenv("POPPLER_PATH", "/usr/bin")

# Tesseract: Standard = "tesseract" im PATH
# Alternativ kann über Umgebungsvariable TESSERACT_CMD gesetzt werden
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "tesseract")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


# ----------------------------------------------------------
# 🧾 Hauptfunktion: OCR
# ----------------------------------------------------------
def run_ocr(filepath: str) -> str:
    """
    Führt OCR auf einer Datei aus.
    - Bei PDF: Umwandlung in Bilder mit Poppler → OCR mit Tesseract
    - Bei Bild: Direktes OCR mit Tesseract
    Rückgabe:
        Erkannter Text (Deutsch + Englisch kombiniert)
    """
    text = ""
    try:
        if filepath.lower().endswith(".pdf"):
            # 📑 PDF → Seiten in Bilder konvertieren
            images = convert_from_path(filepath, poppler_path=POPPLER_PATH)
            for img in images:
                text += pytesseract.image_to_string(img, lang="deu+eng") + "\n"
        else:
            # 🖼️ Normales Bild direkt verarbeiten
            img = Image.open(filepath)
            text = pytesseract.image_to_string(img, lang="deu+eng")
    except Exception as e:
        print(f"❌ Fehler bei OCR ({filepath}): {e}")
        return ""

    return text.strip()
