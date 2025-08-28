# ==========================================================
# 🌐 AutoDocOrganizer – Flask Backend
# Zuständig für Upload, Archivierung, Suche und Download
# ==========================================================

import os
from flask import Flask, request, jsonify, send_file, render_template

from ocr import run_ocr
from translate import translate_text
from explain import explain_text
from extract_institution import extract_institution
from fileops import move_to_archive, ARCHIVE_DIR
from indexer import update_index, read_index

# Flask-App initialisieren
app = Flask(__name__, static_folder="static", template_folder="templates")

# ==========================================================
# 📂 Projektpfade
# ==========================================================
ARCHIVE_ROOT = ARCHIVE_DIR
INDEX_FILE = os.path.join(ARCHIVE_ROOT, "index.csv")

# Falls noch nicht vorhanden → Hauptordner erstellen
os.makedirs(ARCHIVE_ROOT, exist_ok=True)


# ==========================================================
# 🌐 Hauptseite (Frontend laden)
# ==========================================================
@app.route("/")
def index():
    return render_template("index.html")


# ==========================================================
# 📤 Upload von Dateien
# ==========================================================
@app.route("/upload", methods=["POST"])
def upload_files():
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "Keine Dateien hochgeladen"}), 400

    saved_files = []
    for file in files:
        # 📌 Erst im TEMP-Ordner (Desktop/AutoDocOrganizer/ScansInbox)
        inbox_dir = os.path.join(os.path.expanduser("~"), "Desktop", "AutoDocOrganizer", "ScansInbox")
        os.makedirs(inbox_dir, exist_ok=True)
        temp_path = os.path.join(inbox_dir, file.filename)
        file.save(temp_path)

        # 📝 OCR → Text extrahieren
        text = run_ocr(temp_path)

        # 🏢 Institution erkennen (Fallback = _Unklar)
        institution = extract_institution(text) or "_Unklar"

        # 📦 Datei direkt ins Archiv verschieben
        final_path = move_to_archive(temp_path, institution)

        # 📝 Index aktualisieren (Jahr wird intern automatisch gesetzt)
        update_index(final_path, institution)

        saved_files.append(final_path)

    return jsonify({"status": "ok", "files": saved_files})


# ==========================================================
# 📂 Verzeichnisinhalt auflisten (nur innerhalb Archive)
# ==========================================================
@app.route("/list")
def list_files():
    subpath = request.args.get("path", "").strip("/")
    abs_path = os.path.normpath(os.path.join(ARCHIVE_ROOT, subpath))

    # Sicherheit: Nur innerhalb Archive erlaubt
    if not abs_path.startswith(ARCHIVE_ROOT):
        return jsonify({"error": "Ungültiger Pfad"}), 400

    if not os.path.exists(abs_path):
        return jsonify({"error": f"Pfad nicht gefunden: {abs_path}"}), 404

    items = []
    for entry in sorted(os.listdir(abs_path), key=str.lower):
        full = os.path.join(abs_path, entry)
        items.append({
            "name": entry,
            "is_dir": os.path.isdir(full)
        })

    return jsonify(items)


# ==========================================================
# 🔍 Suche im Index (Archiv durchsuchen)
# ==========================================================
@app.route("/search")
def search():
    query = request.args.get("query", "").lower()
    results = []

    for row in read_index():
        if (query in row["Datei"].lower()
            or query in row["Institution"].lower()
            or query in row["Jahr"].lower()):
            results.append({
                "filename": row["Datei"],
                "year": row["Jahr"],
                "institution": row["Institution"],
                "path": row["Pfad"]
            })

    return jsonify(results)


# ==========================================================
# 🗑️ Originale löschen (nach Drag&Drop-Upload)
# ==========================================================
@app.route("/delete_originals", methods=["POST"])
def delete_originals():
    data = request.get_json()
    filenames = data.get("filenames", [])

    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    for fname in filenames:
        try:
            os.remove(os.path.join(desktop, fname))
        except Exception as e:
            print(f"⚠️ Konnte Datei nicht löschen: {fname} – {e}")

    return jsonify({"status": "ok"})


# ==========================================================
# 🌍 Datei übersetzen
# ==========================================================
@app.route("/translate")
def translate_file():
    file_path = request.args.get("file")
    lang = request.args.get("lang", "EN-US")

    abs_path = os.path.join(ARCHIVE_ROOT, file_path)
    if not os.path.exists(abs_path):
        return "❌ Datei nicht gefunden", 404

    # 📝 OCR → Text extrahieren
    text = run_ocr(abs_path)

    # 🌍 Übersetzen
    translated = translate_text(text, lang)
    return translated


# ==========================================================
# 📖 Datei erklären
# ==========================================================
@app.route("/explain")
def explain_file():
    file_path = request.args.get("file")
    lang = request.args.get("lang", "DE")   # 🔑 Default = Deutsch

    abs_path = os.path.join(ARCHIVE_ROOT, file_path)
    if not os.path.exists(abs_path):
        return "❌ Datei nicht gefunden", 404

    # 📝 OCR → Text extrahieren
    text = run_ocr(abs_path)

    # 🤖 Erklärung generieren (Sprache auswählbar)
    explanation = explain_text(text, lang)
    return explanation


# ==========================================================
# 📥 Datei herunterladen
# ==========================================================
@app.route("/download")
def download_file():
    file_path = request.args.get("file")
    if not file_path:
        return jsonify({"error": "Kein Dateipfad angegeben"}), 400

    abs_path = os.path.normpath(os.path.join(ARCHIVE_ROOT, file_path))
    if not abs_path.startswith(ARCHIVE_ROOT) or not os.path.exists(abs_path):
        return jsonify({"error": "Datei nicht gefunden"}), 404

    if os.path.isdir(abs_path):
        return jsonify({"error": "Ordner können nicht heruntergeladen werden"}), 400

    return send_file(abs_path, as_attachment=False)


@app.route("/force_download")
def force_download():
    file_path = request.args.get("file")
    if not file_path:
        return jsonify({"error": "Kein Dateipfad angegeben"}), 400

    abs_path = os.path.normpath(os.path.join(ARCHIVE_ROOT, file_path))
    if not abs_path.startswith(ARCHIVE_ROOT) or not os.path.exists(abs_path):
        return jsonify({"error": "Datei nicht gefunden"}), 404

    if os.path.isdir(abs_path):
        return jsonify({"error": "Ordner können nicht heruntergeladen werden"}), 400

    return send_file(abs_path, as_attachment=True)


# ==========================================================
# ❌ Datei löschen
# ==========================================================
@app.route("/delete", methods=["POST"])
def delete_file():
    data = request.get_json()
    file_path = data.get("file")

    if not file_path:
        return jsonify({"error": "Kein Dateipfad angegeben"}), 400

    abs_path = os.path.normpath(os.path.join(ARCHIVE_ROOT, file_path))
    if not abs_path.startswith(ARCHIVE_ROOT) or not os.path.exists(abs_path):
        return jsonify({"error": "Datei nicht gefunden"}), 404

    if os.path.isdir(abs_path):
        return jsonify({"error": "Ordner angegeben statt Datei"}), 400

    try:
        os.remove(abs_path)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": f"Löschen fehlgeschlagen: {e}"}), 500


# ==========================================================
# ❌ Ordner löschen (rekursiv)
# ==========================================================
@app.route("/delete_folder", methods=["POST"])
def delete_folder():
    data = request.get_json()
    folder_path = data.get("folder")

    if not folder_path:
        return jsonify({"error": "Kein Ordnerpfad angegeben"}), 400

    abs_path = os.path.normpath(os.path.join(ARCHIVE_ROOT, folder_path))
    if not abs_path.startswith(ARCHIVE_ROOT) or not os.path.exists(abs_path):
        return jsonify({"error": "Ordner nicht gefunden"}), 404

    if not os.path.isdir(abs_path):
        return jsonify({"error": "Kein Ordner"}), 400

    try:
        import shutil
        shutil.rmtree(abs_path)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": f"Löschen fehlgeschlagen: {e}"}), 500


# ==========================================================
# 🚀 Start der App
# ==========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
