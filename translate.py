# ==========================================================
# 🌍 Übersetzungsmodul – AutoDocOrganizer
# Unterstützt DeepL (empfohlen) und Fallback auf OpenAI
# ==========================================================

import os
import requests
from dotenv import load_dotenv

# 🔑 Keys aus .env laden
load_dotenv()
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # optional als Fallback

# ==========================================================
# 🌍 Text übersetzen
# ==========================================================
def translate_text(text: str, target_lang: str = "EN") -> str:
    """
    Übersetzt Text in die gewünschte Sprache.
    Standard: Englisch (EN).
    """

    if not text.strip():
        return "⚠️ Kein Text zum Übersetzen gefunden."

    # -----------------------------
    # 1️⃣ DeepL – bevorzugt
    # -----------------------------
    if DEEPL_API_KEY:
        try:
            url = "https://api-free.deepl.com/v2/translate"
            resp = requests.post(
                url,
                data={"text": text, "target_lang": target_lang},
                headers={"Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}"},
                timeout=30,
            )
            resp.raise_for_status()
            result = resp.json()
            return result["translations"][0]["text"]
        except Exception as e:
            return f"❌ DeepL Fehler: {str(e)}"

    # -----------------------------
    # 2️⃣ OpenAI Fallback (falls vorhanden)
    # -----------------------------
    if OPENAI_API_KEY:
        try:
            import openai
            openai.api_key = OPENAI_API_KEY
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"Übersetze den Text ins {target_lang}."},
                    {"role": "user", "content": text},
                ],
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return f"❌ OpenAI Fehler: {str(e)}"

    return "❌ Kein Übersetzungsdienst verfügbar – bitte API-Key in .env eintragen."
