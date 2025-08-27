# 📁 explain.py
import os
import google.generativeai as genai

def explain_text(text: str, target_lang: str = "DE") -> str:
    """
    Erklärt den gegebenen Text mit Google Gemini in einfacher Sprache
    in der gewünschten Zielsprache.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "❌ Fehler: GEMINI_API_KEY fehlt. Bitte in .env eintragen!"

    try:
        # Gemini initialisieren
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Prompt mit Zielsprache
        prompt = f"Erkläre den folgenden Text in einfacher Sprache auf {target_lang}:\n\n{text}"

        response = model.generate_content(prompt)

        return response.text.strip()

    except Exception as e:
        return f"❌ KI-Fehler (Gemini): {e}"
