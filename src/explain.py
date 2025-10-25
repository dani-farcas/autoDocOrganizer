# 📁 explain.py
import os
import google.generativeai as genai

def explain_text(text: str, target_lang: str = "DE") -> str:
    """
    Erklärt den gegebenen Text in einfacher Sprache
    unter Nutzung von Google Gemini (neue API v1).
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "❌ Fehler: GEMINI_API_KEY fehlt in .env"

    try:
        # ✅ Neue API Version (ganz wichtig!)
        genai.configure(api_key=api_key)

        # ✅ Funktioniert nur mit API v1 Keys
        model = genai.GenerativeModel("models/gemini-flash-latest")

        if not text.strip():
            return "(Keine OCR-Erkennung / No text detected)"

        prompt = f"Erkläre den folgenden Text in klarer, einfacher Sprache auf {target_lang}:\n\n{text}"

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        return f"❌ KI-Fehler (Gemini): {e}"
