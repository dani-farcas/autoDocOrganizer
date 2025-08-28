# ==========================================================
# 🌐 AutoDocOrganizer – Flask Backend
# Zuständig für Upload, Archivierung, Suche und Download
# ==========================================================

import os
import shutil
import csv
from flask import Flask, request, jsonify, send_file, render_template

from ocr import run_ocr
from translate import translate_text
from explain import explain_text
from extract_institution import extract_institution
from fileops import move_to_archive
from indexer import update_index

# Flask-App initialisieren
app = Flask(__name__, static_folder="static", template_folder="templates")

# ==========================================================
# 📂 Projektpfade
# ==========================================================
USER_HOME = os.path.expanduser("~")
DESKTOP_DIR = os.path.join(USER_HOME, "Desktop")
DESKTOP_TARGET = os.path.join(DESKTOP_DIR, "AutoDocOrganizer")
INDEX_FILE = os.path.join(DESKTOP_TARGET, "index.csv")

# Falls noch nicht vorhanden → Hauptordner erstellen
os.makedirs(DESKTOP_TARGET, exist_ok=True)


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
        # Temporär speichern im Desktop/AutoDocOrganizer
        temp_path = os.path.join(DESKTOP_TARGET, file.filename)
        file.save(temp_path)

        # 📝 OCR → Text extrahieren
        text = run_ocr(temp_path)

        # 🏢 Institution erkennen
        institution = extract_institution(text)

        # 📅 Jahr erkennen (Fallback = aktuelles Jahr)
        year = str(os.path.basename(os.path.dirname(temp_path)))
        if not year.isdigit():
            year = str(os.path.basename(os.path.dirname(DESKTOP_TARGET)))

        # Falls Text doch ein Jahr enthält → überschreiben
        for token in text.split():
            if token.isdigit() and len(token) == 4:
                year = token
                break

        # 📦 Datei verschieben ins strukturierte Archiv
        final_path = move_to_archive(temp_path, institution)

        # 📝 Index aktualisieren
        update_index(final_path, year, institution)

        saved_files.append(final_path)

    return jsonify({"status": "ok", "files": saved_files})


# ==========================================================
# 🔍 Suche im Index (Archiv durchsuchen)
# ==========================================================
@app.route("/search")
def search():
    query = request.args.get("query", "").lower()
    results = []

    if not os.path.exists(INDEX_FILE):
        return jsonify([])

    with open(INDEX_FILE, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
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
# 📥 Datei herunterladen
# ==========================================================
@app.route("/download")
def download_file():
    file_path = request.args.get("file")
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "Datei nicht gefunden"}), 404
    return send_file(file_path, as_attachment=False)


# 📥 Forciertes Herunterladen (Speichern unter)
@app.route("/force_download")
def force_download():
    file_path = request.args.get("file")
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "Datei nicht gefunden"}), 404
    return send_file(file_path, as_attachment=True)


# ==========================================================
# 🚀 Start der App
# ==========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
