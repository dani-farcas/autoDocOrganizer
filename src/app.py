import os
import shutil
from flask import Flask, request, jsonify, send_file, abort, render_template, redirect, url_for

from ocr import run_ocr
from translate import translate_text
from explain import explain_text
from extract_institution import extract_institution
from fileops import move_to_archive
from indexer import update_index

app = Flask(__name__)  # templates/ wird automatisch unterhalb von src/ gefunden

# 🌱 Projektpfade
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # …/AutoDocOrganizer
ARCHIVE_DIR = os.path.join(BASE_DIR, "Archive")
SCANS_INBOX = os.path.join(BASE_DIR, "ScansInbox")
os.makedirs(SCANS_INBOX, exist_ok=True)


# 🔧 Pfad-Helfer
def _to_rel_archive_path(p: str) -> str:
    if not p:
        return "Archive"
    p = p.replace("\\", "/")
    if "Archive" in p:
        p = "Archive/" + p.split("Archive", 1)[1].lstrip("/")
    elif not p.startswith("Archive"):
        p = "Archive/" + p.lstrip("/")
    return p


def _to_abs_archive_path(p: str) -> str:
    rel = _to_rel_archive_path(p)
    return os.path.normpath(os.path.join(BASE_DIR, rel))


# 🏠 Startseite – index.html
@app.route("/")
@app.route("/index.html")
def index_page():
    return render_template("index.html")


# 🆕 Datei-Upload + Sofort-Verarbeitung
@app.route("/upload", methods=["POST"])
def upload_file():
    if "files" not in request.files:
        return "❌ Keine Datei hochgeladen", 400

    uploaded_files = request.files.getlist("files")

    for file in uploaded_files:
        if not file.filename:
            continue

        # 1) Temporär speichern
        temp_path = os.path.join(SCANS_INBOX, file.filename)
        file.save(temp_path)
        print(f"✅ Datei empfangen: {temp_path}")

        # 2) OCR
        text = run_ocr(temp_path)

        # 3) Institution
        institution = extract_institution(text)
        if not institution:
            institution = "Unklar"
        print(f"🏢 Erkannte Institution: {institution}")

        # 4) Verschieben
        new_path = move_to_archive(temp_path, institution)
        print(f"📦 Verschoben nach: {new_path}")

        # 5) Index
        update_index(new_path, institution, text)

    return redirect(url_for("index_page"))


# 📜 Ordner- und Dateiliste
@app.route("/list")
def list_files():
    req_path = request.args.get("path", "Archive")
    rel_path = _to_rel_archive_path(req_path)
    abs_path = _to_abs_archive_path(rel_path)

    if not abs_path.startswith(ARCHIVE_DIR):
        return abort(403, "Zugriff verweigert")
    if not os.path.exists(abs_path):
        return jsonify([])

    items = []
    for entry in os.scandir(abs_path):
        items.append({
            "name": entry.name,
            "path": os.path.join(rel_path, entry.name).replace("\\", "/"),
            "type": "folder" if entry.is_dir() else "file",
        })
    return jsonify(items)


# 📂 Datei im Browser öffnen
@app.route("/download")
def download_file():
    file_param = request.args.get("file")
    if not file_param:
        return abort(400, "Fehlender Parameter: file")

    abs_path = _to_abs_archive_path(file_param)
    if not abs_path.startswith(ARCHIVE_DIR):
        return abort(403, "Zugriff verweigert")
    if not os.path.isfile(abs_path):
        return abort(404, f"Datei nicht gefunden: {abs_path}")

    return send_file(abs_path)


# ⬇️ Erzwingen-Download
@app.route("/force_download")
def force_download():
    file_param = request.args.get("file")
    if not file_param:
        return abort(400, "Fehlender Parameter: file")

    abs_path = _to_abs_archive_path(file_param)
    if not abs_path.startswith(ARCHIVE_DIR):
        return abort(403, "Zugriff verweigert")
    if not os.path.isfile(abs_path):
        return abort(404, f"Datei nicht gefunden: {abs_path}")

    return send_file(abs_path, as_attachment=True)


# ✏️ Datei umbenennen
@app.route("/rename", methods=["POST"])
def rename_file():
    data = request.json or {}
    old = _to_abs_archive_path(data.get("old", ""))
    new = _to_abs_archive_path(data.get("new", ""))

    if not old.startswith(ARCHIVE_DIR) or not new.startswith(ARCHIVE_DIR):
        return abort(403, "Zugriff verweigert")
    if not os.path.exists(old):
        return abort(404, "Datei nicht gefunden")

    os.makedirs(os.path.dirname(new), exist_ok=True)
    os.rename(old, new)
    return jsonify({"status": "ok"})


# ✏️ Ordner umbenennen
@app.route("/rename_folder", methods=["POST"])
def rename_folder():
    data = request.json or {}
    old = _to_abs_archive_path(data.get("old", ""))
    new_name = data.get("new", "").strip()

    if not new_name:
        return abort(400, "Neuer Name fehlt")

    new_path = os.path.join(os.path.dirname(old), new_name)

    if not old.startswith(ARCHIVE_DIR) or not new_path.startswith(ARCHIVE_DIR):
        return abort(403, "Zugriff verweigert")
    if not os.path.isdir(old):
        return abort(404, "Ordner nicht gefunden")

    os.rename(old, new_path)
    return jsonify({"status": "ok"})


# ❌ Datei löschen
@app.route("/delete", methods=["POST"])
def delete_file():
    data = request.json or {}
    file_param = data.get("file", "")

    abs_path = _to_abs_archive_path(file_param)
    if not abs_path.startswith(ARCHIVE_DIR):
        return abort(403, "Zugriff verweigert")
    if not os.path.exists(abs_path):
        return abort(404, "Datei nicht gefunden")

    os.remove(abs_path)
    return jsonify({"status": "deleted"})


# ❌ Ordner löschen
@app.route("/delete_folder", methods=["POST"])
def delete_folder():
    data = request.json or {}
    folder = _to_abs_archive_path(data.get("folder", ""))

    if not folder.startswith(ARCHIVE_DIR):
        return abort(403, "Zugriff verweigert")
    if not os.path.isdir(folder):
        return abort(404, "Ordner nicht gefunden")

    shutil.rmtree(folder)
    return jsonify({"status": "deleted"})


# 🌍 Übersetzen
@app.route("/translate")
def translate_file():
    file_param = request.args.get("file")
    lang = request.args.get("lang", "EN")

    abs_path = _to_abs_archive_path(file_param or "")
    if not abs_path.startswith(ARCHIVE_DIR):
        return abort(403, "Zugriff verweigert")
    if not os.path.isfile(abs_path):
        return abort(404, "Datei nicht gefunden")

    text = run_ocr(abs_path)
    translated = translate_text(text, lang)
    return translated


# 📖 Erklären
@app.route("/explain")
def explain_file():
    file_param = request.args.get("file")
    lang = request.args.get("lang", "DE")

    abs_path = _to_abs_archive_path(file_param or "")
    if not abs_path.startswith(ARCHIVE_DIR):
        return abort(403, "Zugriff verweigert")
    if not os.path.isfile(abs_path):
        return abort(404, "Datei nicht gefunden")

    text = run_ocr(abs_path)
    explained = explain_text(text, lang)
    return explained


if __name__ == "__main__":
    # ⚠️ Auf dem Server KEIN debug=True verwenden
    # Host=0.0.0.0 macht die App von außen erreichbar
    app.run(host="0.0.0.0", port=5000)
