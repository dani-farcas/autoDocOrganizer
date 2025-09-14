# ==========================================================
# 📖 Erklärungsmodul – AutoDocOrganizer
# Nutzt Gemini API (Google Generative AI) für Erklärungen
# ==========================================================

import os
from dotenv import load_dotenv

# 🔑 Keys laden
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ==========================================================
# 📖 Text erklären
# ==========================================================
def explain_text(text: str, lang: str = "DE") -> str:
    """
    Erklärt den gegebenen Text mit Gemini.
    """

    if not text.strip():
        return "⚠️ Kein Text zum Erklären gefunden."

    if not GEMINI_API_KEY:
        return "❌ Fehler: GEMINI_API_KEY fehlt. Bitte in .env eintragen!"

    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)

        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"Erkläre den folgenden Text in klaren Worten auf {lang}:\n\n{text}"

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini Fehler: {str(e)}"
