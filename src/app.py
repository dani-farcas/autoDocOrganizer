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

# Archiv-Ordner erstellen, falls nicht vorhanden
os.makedirs(ARCHIVE_DIR, exist_ok=True)


# ==========================================================
# 🌐 Hauptseite (Frontend)
# ==========================================================
@app.route("/")
def index():
    """Lädt die Startseite (Frontend)"""
    return render_template("index.html")


# ==========================================================
# 📂 Dateien und Ordner im Archiv auflisten
# ==========================================================
@app.route("/list")
def list_files():
    """
    Gibt alle Dateien UND Ordner im Archiv zurück (für Explorer-Ansicht)
    """
    folder = request.args.get("path", ARCHIVE_DIR)

    if not os.path.exists(folder):
        return jsonify({"error": f"Ordner {folder} nicht gefunden"}), 404

    result = []

    # ➡️ Ordner zuerst
    for d in sorted(os.listdir(folder)):
        abs_path = os.path.join(folder, d)
        if os.path.isdir(abs_path):
            result.append({
                "type": "folder",
                "name": d,
                "path": os.path.relpath(abs_path, PROJECT_ROOT)
            })

    # ➡️ Dateien danach
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
# 📤 Upload von Dateien
# ==========================================================
@app.route("/upload", methods=["POST"])
def upload_files():
    """
    Nimmt hochgeladene Dateien entgegen, führt OCR durch,
    erkennt Institution & Jahr, verschiebt ins Archiv und
    aktualisiert den Index.
    """
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "Keine Dateien hochgeladen"}), 400

    saved_files = []
    for file in files:
        # Datei temporär im Archiv-Root speichern
        temp_path = os.path.join(ARCHIVE_DIR, file.filename)
        file.save(temp_path)

        # OCR ausführen
        text = run_ocr(temp_path)

        # Institution erkennen
        institution = extract_institution(text)

        # Jahr bestimmen (Standard = aktuelles Jahr)
        year = str(datetime.now().year)
        for token in text.split():
            if token.isdigit() and len(token) == 4:
                year = token
                break

        # Datei verschieben ins strukturierte Archiv
        final_path = move_to_archive(temp_path, institution)

        # Index aktualisieren
        update_index(final_path, year, institution)

        saved_files.append(os.path.relpath(final_path, PROJECT_ROOT))

    return jsonify({"status": "ok", "files": saved_files})


# ==========================================================
# 🔍 Suche im Index
# ==========================================================
@app.route("/search")
def search():
    """
    Durchsucht die Index-Datei nach Begriffen
    (Dateiname, Institution, Jahr)
    """
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
# 🗑️ Dateien löschen
# ==========================================================
@app.route("/delete", methods=["POST"])
def delete_files():
    """
    Löscht angegebene Dateien aus dem Archiv
    """
    data = request.get_json()
    filenames = data.get("filenames", [])

    for fname in filenames:
        abs_path = os.path.join(ARCHIVE_DIR, fname)
        try:
            if os.path.exists(abs_path):
                os.remove(abs_path)
        except Exception as e:
            print(f"⚠️ Konnte Datei nicht löschen: {fname} – {e}")

    return jsonify({"status": "ok"})


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
    """
    Übersetzt den OCR-Text einer Datei in die gewünschte Sprache.
    """
    rel_path = request.args.get("file")
    lang = request.args.get("lang", "EN")

    if not rel_path:
        return jsonify({"error": "Keine Datei angegeben"}), 400

    abs_path = os.path.join(PROJECT_ROOT, rel_path)
    if not os.path.exists(abs_path):
        return jsonify({"error": f"Datei nicht gefunden: {rel_path}"}), 404

    # OCR ausführen
    text = run_ocr(abs_path)

    # Übersetzen
    translated = translate_text(text, lang)

    return translated


# ==========================================================
# 📖 Dokument erklären
# ==========================================================
@app.route("/explain")
def explain_file():
    """
    Erklärt den OCR-Text einer Datei in einfacher Sprache.
    """
    rel_path = request.args.get("file")

    if not rel_path:
        return jsonify({"error": "Keine Datei angegeben"}), 400

    abs_path = os.path.join(PROJECT_ROOT, rel_path)
    if not os.path.exists(abs_path):
        return jsonify({"error": f"Datei nicht gefunden: {rel_path}"}), 404

    # OCR ausführen
    text = run_ocr(abs_path)

    # Erklärung erzeugen
    explanation = explain_text(text)

    return explanation


# ==========================================================
# 🚀 Start der App
# ==========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
