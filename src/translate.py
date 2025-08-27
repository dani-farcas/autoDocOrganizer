# 📁 translate.py
import os
import deepl

LANGUAGE_MAP = {
    "EN": "EN-US",   # standardizează engleza la EN-US
    "PT": "PT-PT",   # DeepL cere explicit PT-PT sau PT-BR
}

def translate_text(text: str, target_lang: str) -> str:
    """
    Übersetzt den gegebenen Text automatisch nach target_lang.
    Die Ausgangssprache wird automatisch erkannt.
    """
    auth_key = os.getenv("DEEPL_API_KEY")
    if not auth_key:
        raise ValueError("❌ DeepL API Key fehlt in den Umgebungsvariablen!")

    # Normalizare coduri limbă
    target_lang = LANGUAGE_MAP.get(target_lang, target_lang)

    translator = deepl.Translator(auth_key)
    result = translator.translate_text(text, target_lang=target_lang)
    return result.text
