# ✅ Einfache Tests für AutoDocOrganizer

from extract_institution import detect_institution

def test_institution():
    assert detect_institution("Finanzamt Gießen") == "Finanzamt"
    assert detect_institution("Sparkasse Marburg") == "Sparkasse"
    assert detect_institution("Unbekanntes Dokument") == "_Unklar"

if __name__ == "__main__":
    test_institution()
    print("✅ Alle Tests bestanden.")
