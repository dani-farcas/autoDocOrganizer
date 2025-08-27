import spacy

try:
    nlp = spacy.load("de_core_news_md")
except OSError:
    raise RuntimeError("❌ spaCy Modell nicht gefunden. Bitte installieren mit:\n"
                       "   python -m spacy download de_core_news_md")

# Schlüsselwörter für typische Firmen/Behörden
ORG_HINTS = [
    "gmbh", "ag", "kg", "se",
    "bank", "sparkasse", "versicherung", "kasse",
    "amt", "ministerium", "behörde",
    "universität", "hochschule", "institut",
    "rewe", "aldi", "lidl"
]

def extract_institution(text: str) -> str:
    """
    Erkennt Institutionen automatisch mit spaCy NER + Filterung.
    """
    if not text:
        return "Unklar"

    doc = nlp(text)
    orgs = [ent.text.strip() for ent in doc.ents if ent.label_ == "ORG"]

    if not orgs:
        return "Unklar"

    # 1) Bevorzugt ORGs mit Schlüsselwörtern
    for org in orgs:
        lower = org.lower()
        if any(hint in lower for hint in ORG_HINTS):
            return org

    # 2) Sonst die längste ORG nehmen (häufig Firmenname im Briefkopf)
    return max(orgs, key=len)
