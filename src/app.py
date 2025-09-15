# ==========================================================
# 📂 AutoDocOrganizer – Flask Backend
# ==========================================================
import os
from datetime import datetime
from urllib.parse import unquote   # ✅ wichtig für URL-Decodierung
from flask import Flask, request, jsonify, send_file, render_template

# 🔄 Eigene Module
from src.ocr import run_ocr
from src.extract_institution import extract_institution
from src.indexer import update_index
from src.translate import translate_text
from src.explain import explain_text

# ----------------------------------------------------------
# ⚙️ Flask-App initialisieren
# ----------------------------------------------------------
app = Flask(__name__)

# Projektverzeichnis (statisch)
ARCHIVE_DIR = "/home/ubuntu/autoDocOrganizer/Archive"
os.makedirs(ARCHIVE_DIR, exist_ok=True)


# ==========================================================
# 📥 Upload von Dateien
# ==========================================================
@app.route("/upload", methods=["POST"])
def upload_files():
    """Dateien hochladen und ins Archiv verschieben"""
    # 🛡️ Prüfen, ob Dateien im Request sind
    uploaded_files = []
    if "files" in request.files:
        uploaded_files = request.files.getlist("files")
    elif "file-upload" in request.files:
        uploaded_files = request.files.getlist("file-upload")

    if not uploaded_files:
        return jsonify({"error": "Keine Dateien hochgeladen"}), 400

    saved = []

    for file in uploaded_files:
        if file.filename == "":
            continue

        # 🔹 Temporär speichern
        tmp_path = os.path.join(ARCHIVE_DIR, file.filename)
        file.save(tmp_path)

        # 🔹 OCR + Institution extrahieren
        text = run_ocr(tmp_path)
        institution = extract_institution(text) or "_Unklar"
        year = datetime.now().year

        # 🔹 Zielordner vorbereiten
        target_dir = os.path.join(ARCHIVE_DIR, str(year), institution)
        os.makedirs(target_dir, exist_ok=True)

        # 🔹 Datei verschieben
        final_path = os.path.join(target_dir, file.filename)
        os.replace(tmp_path, final_path)

        # 🔹 Index aktualisieren
        update_index(final_path, institution, year)

        saved.append(final_path)
        print(f"📦 Verschoben nach: {final_path}")

    return jsonify({"status": "ok", "saved": saved})


# ==========================================================
# 📂 Dateien & Ordner auflisten
# ==========================================================
@app.route("/list")
def list_files():
    """Listet Inhalte eines Ordners im Archiv"""
    rel_path = (request.args.get("path", "") or "").strip().strip("/\\")
    if rel_path == "Archive":
        rel_path = ""
    elif rel_path.startswith("Archive/"):
        rel_path = rel_path[len("Archive/"):]

    base = os.path.abspath(ARCHIVE_DIR)
    abs_path = os.path.abspath(os.path.join(base, rel_path))

    if not abs_path.startswith(base):
        return jsonify({"error": "Ungültiger Pfad"}), 400
    if not os.path.isdir(abs_path):
        return jsonify({"error": f"Ordner nicht gefunden: {rel_path or '/'}"}), 404

    entries = []
    names = sorted(os.listdir(abs_path), key=str.casefold)

    for name in names:
        full = os.path.join(abs_path, name)
        if os.path.isdir(full):
            entries.append({
                "name": name,
                "path": os.path.relpath(full, base).replace("\\", "/"),
                "is_dir": True,
            })

    for name in names:
        full = os.path.join(abs_path, name)
        if os.path.isfile(full):
            entries.append({
                "name": name,
                "path": os.path.relpath(full, base).replace("\\", "/"),
                "is_dir": False,
            })

    return jsonify(entries)


# ==========================================================
# 📥 Datei herunterladen
# ==========================================================
@app.route("/download")
def download_file():
    rel_path = unquote(request.args.get("file", ""))
    if not rel_path:
        return jsonify({"error": "Keine Datei angegeben"}), 400

    abs_path = os.path.abspath(os.path.join(ARCHIVE_DIR, rel_path))
    if not abs_path.startswith(os.path.abspath(ARCHIVE_DIR)):
        return jsonify({"error": "Ungültiger Pfad"}), 400
    if not os.path.isfile(abs_path):
        return jsonify({"error": f"Datei nicht gefunden: {rel_path}"}), 404

    return send_file(abs_path, as_attachment=False)


# ==========================================================
# 🗑️ Dateien / Ordner löschen
# ==========================================================
@app.route("/delete", methods=["POST"])
def delete_files():
    """Löscht Dateien oder leere Ordner"""
    data = request.get_json()
    filenames = data.get("filenames", [])

    deleted, errors = [], []
    for rel_path in filenames:
        abs_path = os.path.abspath(os.path.join(ARCHIVE_DIR, rel_path))
        if not abs_path.startswith(os.path.abspath(ARCHIVE_DIR)):
            errors.append({rel_path: "Ungültiger Pfad"})
            continue

        if os.path.exists(abs_path):
            try:
                if os.path.isfile(abs_path):
                    os.remove(abs_path)
                elif os.path.isdir(abs_path):
                    os.rmdir(abs_path)
                deleted.append(rel_path)
            except Exception as e:
                errors.append({rel_path: str(e)})
        else:
            errors.append({rel_path: "Nicht gefunden"})

    return jsonify({"status": "ok", "deleted": deleted, "errors": errors})


# ==========================================================
# ✏️ Dateien / Ordner umbenennen
# ==========================================================
@app.route("/rename", methods=["POST"])
def rename_entry():
    """Benennt Datei oder Ordner um"""
    data = request.get_json()
    old = data.get("old")
    new = data.get("new")

    if not old or not new:
        return jsonify({"error": "Alte und neue Namen erforderlich"}), 400

    old_path = os.path.abspath(os.path.join(ARCHIVE_DIR, old))
    new_path = os.path.abspath(os.path.join(ARCHIVE_DIR, new))

    if not old_path.startswith(ARCHIVE_DIR) or not new_path.startswith(ARCHIVE_DIR):
        return jsonify({"error": "Ungültiger Pfad"}), 400
    if not os.path.exists(old_path):
        return jsonify({"error": "Eintrag nicht gefunden"}), 404

    try:
        os.rename(old_path, new_path)
        return jsonify({"status": "ok", "old": old, "new": new})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================================
# 🌍 Datei übersetzen
# ==========================================================
@app.route("/translate")
def translate_file():
    """OCR → Übersetzen in gewünschte Sprache"""
    rel_path = unquote(request.args.get("file", ""))
    lang = request.args.get("lang", "EN")

    if not rel_path:
        return jsonify({"error": "Keine Datei angegeben"}), 400

    abs_path = os.path.abspath(os.path.join(ARCHIVE_DIR, rel_path))
    print(f"🔎 Translate request: rel_path={rel_path}, abs_path={abs_path}")

    if not abs_path.startswith(ARCHIVE_DIR):
        return jsonify({"error": "Ungültiger Pfad"}), 400
    if not os.path.isfile(abs_path):
        return jsonify({"error": f"Datei nicht gefunden: {rel_path}"}), 404

    text = run_ocr(abs_path)
    print(f"📄 OCR length: {len(text)}")

    if not text.strip():
        return jsonify({"error": "⚠ Kein Text zum Übersetzen gefunden."}), 400

    translated = translate_text(text, lang)
    return translated, 200, {"Content-Type": "text/plain; charset=utf-8"}


# ==========================================================
# 📖 Datei erklären
# ==========================================================
@app.route("/explain")
def explain_file():
    """OCR → Erklärung in gewünschter Sprache"""
    rel_path = unquote(request.args.get("file", ""))
    lang = request.args.get("lang", "DE")

    if not rel_path:
        return jsonify({"error": "Keine Datei angegeben"}), 400

    abs_path = os.path.abspath(os.path.join(ARCHIVE_DIR, rel_path))
    if not abs_path.startswith(ARCHIVE_DIR):
        return jsonify({"error": "Ungültiger Pfad"}), 400
    if not os.path.isfile(abs_path):
        return jsonify({"error": f"Datei nicht gefunden: {rel_path}"}), 404

    text = run_ocr(abs_path)
    if not text.strip():
        return jsonify({"error": "⚠ Kein Text zum Erklären gefunden."}), 400

    explained = explain_text(text, lang)
    return explained, 200, {"Content-Type": "text/plain; charset=utf-8"}


# ==========================================================
# 🌐 Index-Seite
# ==========================================================
@app.route("/")
def index():
    return render_template("index.html")
