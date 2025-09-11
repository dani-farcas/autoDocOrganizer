# ==========================================================
# 🌐 AutoDocOrganizer – Flask Backend
# Zuständig für Upload, Archivierung, Suche, Download,
# Übersetzen und Erklären
# ==========================================================

import os
import csv
from datetime import datetime
from flask import Flask, request, jsonify, send_file, render_template

# 📚 Eigene Module
from ocr import run_ocr
from translate import translate_text
from explain import explain_text
from extract_institution import extract_institution
from fileops import move_to_archive
from indexer import update_index

# ==========================================================
# 🚀 Flask-App initialisieren
# ==========================================================
app = Flask(__name__, static_folder="static", template_folder="templates")

# ==========================================================
# 📂 Projektpfade definieren
# ==========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # src/
PROJECT_ROOT = os.path.dirname(BASE_DIR)               # AutoDocOrganizer/
ARCHIVE_DIR = os.path.join(PROJECT_ROOT, "Archive")    # Archiv im Projekt
INDEX_FILE = os.path.join(ARCHIVE_DIR, "index.csv")    # Index in Archive/

os.makedirs(ARCHIVE_DIR, exist_ok=True)


# ==========================================================
# 🌐 Hauptseite (Frontend)
# ==========================================================
@app.route("/")
def index():
    return render_template("index.html")


# ==========================================================
# 📂 Dateien und Ordner im Archiv auflisten
# ==========================================================
@app.route("/list")
def list_files():
    folder = request.args.get("path", ARCHIVE_DIR)

    if not os.path.exists(folder):
        return jsonify({"error": f"Ordner {folder} nicht gefunden"}), 404

    result = []
    for d in sorted(os.listdir(folder)):
        abs_path = os.path.join(folder, d)
        if os.path.isdir(abs_path):
            result.append({
                "type": "folder",
                "name": d,
                "path": os.path.relpath(abs_path, PROJECT_ROOT)
            })

    for f in sorted(os.listdir(folder)):
        abs_path = os.path.join(folder, f)
        if os.path.isfile(abs_path):
            result.append({
                "type": "file",
                "name": f,
                "path": os.path.relpath(abs_path, PROJECT_ROOT)
            })

    return jsonify(result)


# ==========================================================
# 🗑️ Dateien löschen
# ==========================================================
@app.route("/delete", methods=["POST"])
def delete_files():
    """
    Löscht eine oder mehrere Dateien aus dem Archiv
    Erwartet JSON: { "filenames": ["Archive/2025/Unklar/file.pdf"] }
    """
    data = request.get_json()
    filenames = data.get("filenames", [])

    deleted = []
    errors = []

    for rel_path in filenames:
        abs_path = os.path.join(PROJECT_ROOT, rel_path)
        if abs_path.startswith(ARCHIVE_DIR) and os.path.exists(abs_path):
            try:
                os.remove(abs_path)
                deleted.append(rel_path)
            except Exception as e:
                errors.append({rel_path: str(e)})
        else:
            errors.append({rel_path: "Datei nicht gefunden oder ungültig"})

    return jsonify({"status": "ok", "deleted": deleted, "errors": errors})


# ==========================================================
# 🗂️ Ordner löschen (nur wenn leer)
# ==========================================================
@app.route("/delete_folder", methods=["POST"])
def delete_folder():
    data = request.get_json()
    folder_path = data.get("path")

    if not folder_path:
        return jsonify({"error": "Kein Pfad angegeben"}), 400

    abs_path = os.path.join(PROJECT_ROOT, folder_path)
    if not abs_path.startswith(ARCHIVE_DIR):
        return jsonify({"error": "Ungültiger Pfad"}), 403

    if os.path.exists(abs_path) and os.path.isdir(abs_path):
        if not os.listdir(abs_path):
            os.rmdir(abs_path)
            return jsonify({"status": "ok", "deleted": folder_path}), 200
        else:
            return jsonify({"error": "Ordner ist nicht leer"}), 400
    else:
        return jsonify({"error": "Ordner nicht gefunden"}), 404


# ==========================================================
# 📥 Datei herunterladen
# ==========================================================
@app.route("/download")
def download_file():
    rel_path = request.args.get("file")
    if not rel_path:
        return jsonify({"error": "Datei nicht angegeben"}), 400

    abs_path = os.path.join(PROJECT_ROOT, rel_path)
    if not os.path.exists(abs_path):
        return jsonify({"error": f"Datei nicht gefunden: {rel_path}"}), 404

    return send_file(abs_path, as_attachment=False)


@app.route("/force_download")
def force_download():
    rel_path = request.args.get("file")
    if not rel_path:
        return jsonify({"error": "Datei nicht angegeben"}), 400

    abs_path = os.path.join(PROJECT_ROOT, rel_path)
    if not os.path.exists(abs_path):
        return jsonify({"error": f"Datei nicht gefunden: {rel_path}"}), 404

    return send_file(abs_path, as_attachment=True)


# ==========================================================
# 🌍 Datei übersetzen
# ==========================================================
@app.route("/translate")
def translate_file():
    rel_path = request.args.get("file")
    lang = request.args.get("lang", "EN")

    if not rel_path:
        return jsonify({"error": "Keine Datei angegeben"}), 400

    abs_path = os.path.join(PROJECT_ROOT, rel_path)
    if not os.path.exists(abs_path):
        return jsonify({"error": f"Datei nicht gefunden: {rel_path}"}), 404

    text = run_ocr(abs_path)
    translated = translate_text(text, lang)
    return translated


# ==========================================================
# 📖 Dokument erklären
# ==========================================================
@app.route("/explain")
def explain_file():
    rel_path = request.args.get("file")

    if not rel_path:
        return jsonify({"error": "Keine Datei angegeben"}), 400

    abs_path = os.path.join(PROJECT_ROOT, rel_path)
    if not os.path.exists(abs_path):
        return jsonify({"error": f"Datei nicht gefunden: {rel_path}"}), 404

    text = run_ocr(abs_path)
    explanation = explain_text(text)
    return explanation


# ==========================================================
# 🚀 Start der App
# ==========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
