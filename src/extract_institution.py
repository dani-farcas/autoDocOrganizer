import spacy
import re
import json
import os

# 📂 Datei für dynamisch gesehene Institutionen
INSTITUTIONS_FILE = os.path.join(os.path.dirname(__file__), "..", "institutions_seen.json")

# 📌 Liste fester Institutionen (Whitelist)
KNOWN_INSTITUTIONS = [
    "Bundesagentur für Arbeit",
    "Jobcenter",
    "Finanzamt",
    "Deutsche Rentenversicherung",
    "AOK", "TK", "Barmer", "IKK", "Krankenkasse",
    "Sparkasse", "Volksbank", "Commerzbank", "Deutsche Bank"
]

# 🔑 Schlüsselwörter für typische ORGs
ORG_HINTS = [
    "gmbh", "ag", "kg", "se",
    "bank", "sparkasse", "versicherung", "kasse",
    "amt", "ministerium", "behörde",
    "universität", "hochschule", "institut",
    "rewe", "aldi", "lidl"
]

# 🧠 spaCy Modell laden
try:
    nlp = spacy.load("de_core_news_md")
except OSError:
    raise RuntimeError("❌ spaCy Modell nicht gefunden. Bitte installieren mit:\n"
                       "   python -m spacy download de_core_news_md")


# ============================================================
# 📥 Gesehene Institutionen laden/speichern
# ============================================================
def load_institutions():
    if os.path.exists(INSTITUTIONS_FILE):
        with open(INSTITUTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_institution(name: str):
    data = load_institutions()
    if name not in data:
        data.append(name)
        with open(INSTITUTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# ============================================================
# 🔎 Institution extrahieren
# ============================================================
def extract_institution(text: str) -> str:
    if not text:
        return "_Unklar"

    text_lower = text.lower()

    # 1️⃣ Bekannte Institutionen prüfen
    for inst in KNOWN_INSTITUTIONS:
        if inst.lower() in text_lower:
            return inst

    # 2️⃣ Bereits gesehene Institutionen
    for inst in load_institutions():
        if inst.lower() in text_lower:
            return inst

    # 3️⃣ Mit spaCy NER Institutionen erkennen
    doc = nlp(text)
    orgs = [ent.text.strip() for ent in doc.ents if ent.label_ == "ORG"]

    # 🔎 Nur sinnvolle ORGs behalten
    filtered = []
    for org in orgs:
        lower = org.lower()
        if len(org) < 3:  # zu kurz
            continue
        if re.match(r"^\d+$", org):  # nur Zahl (z.B. Telefonnummer)
            continue
        if any(hint in lower for hint in ORG_HINTS):
            return org  # sofort zurückgeben, wenn Match mit Schlüsselwort
        filtered.append(org)

    # 4️⃣ Wenn keine ORGs → Fallback
    if not filtered:
        save_institution("_Unklar")
        return "_Unklar"

    # 5️⃣ Längste ORG zurückgeben (Briefkopf etc.)
    candidate = max(filtered, key=len)
    save_institution(candidate)
    return candidate


# ============================================================
# 🧪 Testlauf
# ============================================================
if __name__ == "__main__":
    sample_text = """
    Informationen zur Arbeitsbescheinigung
    Bundesagentur für Arbeit
    Telefonnummer: 0800 45555 27
    """
    print("➡️ Erkannte Institution:", extract_institution(sample_text))
