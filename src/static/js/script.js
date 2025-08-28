// =========================================================
// 📂 AutoDocOrganizer – Frontend-Skripte
// Enthält: Upload mit Loader & Banner, Drag&Drop,
// Navigation, Kontextmenüs, Übersetzen & Erklären
// =========================================================

let currentPath = "Archive";
let contextMenu;

// 🌍 Unterstützte Sprachen
const supportedLanguages = [
  { code: "EN-US", name: "Englisch (US)" },
  { code: "EN-GB", name: "Englisch (UK)" },
  { code: "DE", name: "Deutsch" },
  { code: "FR", name: "Französisch" },
  { code: "IT", name: "Italienisch" },
  { code: "ES", name: "Spanisch" },
  { code: "PT-PT", name: "Portugiesisch (Portugal)" },
  { code: "PT-BR", name: "Portugiesisch (Brasilien)" },
  { code: "NL", name: "Niederländisch" },
  { code: "PL", name: "Polnisch" },
  { code: "RU", name: "Russisch" },
  { code: "RO", name: "Rumänisch" },
  { code: "JA", name: "Japanisch" },
  { code: "ZH", name: "Chinesisch" }
];

// =========================================================
// 📢 Banner mit Close-Button
// =========================================================
function showBanner(message, type = "success") {
  const banner = document.getElementById("banner");
  const bannerText = document.getElementById("banner-text");
  const closeBtn = document.getElementById("banner-close");

  bannerText.textContent = message;
  banner.className = "banner " + type;
  banner.style.display = "flex";

  closeBtn.onclick = () => {
    banner.style.display = "none";
  };

  // Automatisch nach 3 Sekunden schließen
  setTimeout(() => {
    if (banner.style.display === "flex") {
      banner.style.display = "none";
    }
  }, 3000);
}

// =========================================================
// 📤 Upload-Formular mit Loader & Banner
// =========================================================
document.addEventListener("DOMContentLoaded", () => {
  const uploadForm = document.getElementById("upload-form");
  if (uploadForm) {
    uploadForm.addEventListener("submit", async function (e) {
      e.preventDefault();

      const loader = document.getElementById("upload-loader");
      loader.style.display = "inline-block";

      const formData = new FormData(this);

      try {
        const res = await fetch("/upload", { method: "POST", body: formData });

        if (res.ok) {
          showBanner("✅ Upload erfolgreich!", "success");
          loadFolder();
        } else {
          showBanner("❌ Fehler beim Upload", "error");
        }
      } catch (err) {
        showBanner("⚠️ Netzwerkfehler: " + err.message, "error");
      } finally {
        loader.style.display = "none";
      }
    });
  }
});

// =========================================================
// 📂 Drag & Drop Upload mit Bestätigung zum Löschen
// =========================================================
const dropZone = document.getElementById("drop-zone");

if (dropZone) {
  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
  });

  dropZone.addEventListener("drop", async (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");

    const files = e.dataTransfer.files;
    if (files.length === 0) return;

    const formData = new FormData();
    for (let file of files) {
      formData.append("files", file);
    }

    const loader = document.getElementById("upload-loader");
    loader.style.display = "inline-block";

    try {
      const res = await fetch("/upload", { method: "POST", body: formData });

      if (res.ok) {
        // 👉 Benutzer fragen ob Original gelöscht werden soll
        const confirmDelete = confirm("✅ Upload erfolgreich!\n\nMöchten Sie die Original-Dateien vom Desktop löschen?");
        if (confirmDelete) {
          await fetch("/delete_originals", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ filenames: Array.from(files).map(f => f.name) })
          });
          showBanner("🗑️ Originale gelöscht", "success");
        } else {
          showBanner("✅ Dateien behalten", "success");
        }
        loadFolder();
      } else {
        showBanner("❌ Fehler beim Upload", "error");
      }
    } catch (err) {
      showBanner("⚠️ Netzwerkfehler: " + err.message, "error");
    } finally {
      loader.style.display = "none";
    }
  });
}

// =========================================================
// 📌 Breadcrumb Navigation
// =========================================================
function renderBreadcrumb(path) {
  const parts = path.split(/[\\/]/).filter(Boolean);
  let breadcrumb = "";
  let partial = "";
  parts.forEach((part, i) => {
    partial += (i === 0 ? part : "/" + part);
    breadcrumb += `<span onclick="loadFolder('${partial}')">${part}</span>`;
    if (i < parts.length - 1) breadcrumb += " / ";
  });
  document.getElementById("breadcrumb").innerHTML = breadcrumb;
}

// =========================================================
// 📂 Hilfsfunktionen für Pfade
// =========================================================
function normalizeToArchivePath(p) {
  if (!p) return "Archive";
  let s = String(p).replace(/\\/g, "/");
  const i = s.indexOf("Archive");
  if (i >= 0) s = s.substring(i);
  if (!s.startsWith("Archive")) s = "Archive/" + s.replace(/^\/+/, "");
  return s;
}

function dirname(p) {
  p = normalizeToArchivePath(p);
  const idx = p.lastIndexOf("/");
  return idx > 0 ? p.slice(0, idx) : p;
}

// =========================================================
// 📂 Ordner & Dateien laden
// =========================================================
async function loadFolder(path = "Archive") {
  currentPath = normalizeToArchivePath(path);
  const res = await fetch(`/list?path=${encodeURIComponent(currentPath)}`);
  const items = await res.json();

  renderBreadcrumb(currentPath);

  const ul = document.getElementById("file-list");
  ul.innerHTML = "";

  items.forEach(item => {
    let rel = normalizeToArchivePath(item.path);
    const li = document.createElement("li");
    li.textContent = (item.type === "folder" ? "📂 " : "📄 ") + item.name;

    if (item.type === "folder") {
      li.ondblclick = () => loadFolder(rel);
      li.oncontextmenu = (e) => {
        e.preventDefault();
        showFolderMenu(e.pageX, e.pageY, rel);
      };
    } else {
      li.ondblclick = () => openFile(rel);
      li.oncontextmenu = (e) => {
        e.preventDefault();
        showFileMenu(e.pageX, e.pageY, rel);
      };
    }
    ul.appendChild(li);
  });
}

// =========================================================
// 📄 Datei öffnen / herunterladen
// =========================================================
function openFile(path) {
  const rel = normalizeToArchivePath(path);
  window.open(`/download?file=${encodeURIComponent(rel)}`, "_blank");
}

function downloadFile(path) {
  const rel = normalizeToArchivePath(path);
  window.location.href = `/force_download?file=${encodeURIComponent(rel)}`;
}

// =========================================================
// ✏️ Datei / Ordner umbenennen
// =========================================================
async function renameFile(path) {
  const rel = normalizeToArchivePath(path);
  const newName = prompt("Neuer Dateiname:", rel.split("/").pop());
  if (!newName) return;
  const body = { old: rel, new: normalizeToArchivePath(dirname(rel) + "/" + newName) };
  const res = await fetch("/rename", { 
    method: "POST", 
    headers: {"Content-Type": "application/json"}, 
    body: JSON.stringify(body) 
  });
  if (res.ok) loadFolder(dirname(rel)); else showBanner("❌ Fehler beim Umbenennen", "error");
}

async function renameFolder(path) {
  const newName = prompt("Neuer Ordnername:", path.split("/").pop());
  if (!newName) return;
  const res = await fetch("/rename_folder", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ old: path, new: newName })
  });
  if (res.ok) loadFolder(dirname(path)); else showBanner("❌ Fehler beim Umbenennen des Ordners", "error");
}

// =========================================================
// ❌ Datei / Ordner löschen
// =========================================================
async function deleteFile(path) {
  const rel = normalizeToArchivePath(path);
  if (!confirm("Datei wirklich löschen?")) return;
  const res = await fetch("/delete", { 
    method: "POST", 
    headers: {"Content-Type": "application/json"}, 
    body: JSON.stringify({ file: rel }) 
  });
  if (res.ok) loadFolder(currentPath); else showBanner("❌ Fehler beim Löschen", "error");
}

async function deleteFolder(path) {
  if (!confirm("Ordner wirklich löschen (inkl. aller Dateien)?")) return;
  const res = await fetch("/delete_folder", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ folder: path })
  });
  if (res.ok) loadFolder(dirname(path)); else showBanner("❌ Fehler beim Löschen des Ordners", "error");
}

// =========================================================
// 🔍 Archiv durchsuchen
// =========================================================
document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("search-input");

  if (searchInput) {
    searchInput.addEventListener("input", async () => {
      const query = searchInput.value.trim();

      if (query.length < 2) {
        // Wenn Eingabe zu kurz → normale Ordneransicht
        loadFolder();
        return;
      }

      try {
        const res = await fetch(`/search?query=${encodeURIComponent(query)}`);
        const results = await res.json();

        const ul = document.getElementById("file-list");
        ul.innerHTML = "";

        results.forEach(item => {
          const li = document.createElement("li");
          li.textContent = "📄 " + item.filename + ` (${item.institution}, ${item.year})`;
          li.onclick = () => window.open(`/download?file=${encodeURIComponent(item.path)}`, "_blank");
          ul.appendChild(li);
        });
      } catch (err) {
        showBanner("❌ Fehler bei der Suche", "error");
      }
    });
  }
});


// =========================================================
// 📑 Kontextmenüs
// =========================================================
function showFileMenu(x, y, path) {
  if (contextMenu) contextMenu.remove();
  contextMenu = document.createElement("div");
  contextMenu.className = "context-menu";
  contextMenu.style.top = y + "px";
  contextMenu.style.left = x + "px";
  contextMenu.innerHTML = `
    <button onclick="downloadFile('${path}')">⬇️ Download</button>
    <button onclick="renameFile('${path}')">✏️ Umbenennen</button>
    <button onclick="translateFile('${path}')">🌍 Übersetzen</button>
    <button onclick="explainFile('${path}')">📖 Erklären</button>
    <button onclick="deleteFile('${path}')">❌ Löschen</button>
  `;
  document.body.appendChild(contextMenu);
  document.addEventListener("click", () => { if (contextMenu) contextMenu.remove(); }, { once: true });
}

function showFolderMenu(x, y, path) {
  if (contextMenu) contextMenu.remove();
  contextMenu = document.createElement("div");
  contextMenu.className = "context-menu";
  contextMenu.style.top = y + "px";
  contextMenu.style.left = x + "px";
  contextMenu.innerHTML = `
    <button onclick="renameFolder('${path}')">✏️ Ordner umbenennen</button>
    <button onclick="deleteFolder('${path}')">❌ Ordner löschen</button>
  `;
  document.body.appendChild(contextMenu);
  document.addEventListener("click", () => { if (contextMenu) contextMenu.remove(); }, { once: true });
}

// =========================================================
// 🌍 Datei übersetzen / 📖 erklären (Modal)
// =========================================================
async function translateFile(path) {
  createModal(path, "Übersetzen", "/translate");
}

async function explainFile(path) {
  createModal(path, "Erklären", "/explain");
}

// Hilfsfunktion: Modal generieren
function createModal(path, actionLabel, endpoint) {
  const rel = normalizeToArchivePath(path);

  const select = document.createElement("select");
  supportedLanguages.forEach(lang => {
    const opt = document.createElement("option");
    opt.value = lang.code;
    opt.textContent = `${lang.name} (${lang.code})`;
    select.appendChild(opt);
  });

  const wrapper = document.createElement("div");
  wrapper.className = "modal-content";
  wrapper.innerHTML = "<b>Sprache auswählen:</b><br>";
  wrapper.appendChild(select);

  const outputArea = document.createElement("textarea");
  outputArea.className = "modal-output";
  wrapper.appendChild(outputArea);

  const btnDiv = document.createElement("div");
  btnDiv.className = "modal-buttons";

  const okBtn = document.createElement("button");
  okBtn.textContent = actionLabel;
  okBtn.onclick = async () => {
    const lang = select.value;
    outputArea.value = "⏳ " + actionLabel + "...";
    const res = await fetch(`${endpoint}?file=${encodeURIComponent(rel)}&lang=${encodeURIComponent(lang)}`);
    outputArea.value = await res.text();
  };

  const closeBtn = document.createElement("button");
  closeBtn.textContent = "Schließen";
  closeBtn.onclick = () => document.body.removeChild(modal);

  btnDiv.appendChild(okBtn);
  btnDiv.appendChild(closeBtn);
  wrapper.appendChild(btnDiv);

  const modal = document.createElement("div");
  modal.className = "modal";
  modal.appendChild(wrapper);

  document.body.appendChild(modal);
}

// =========================================================
// 🚀 Initial laden
// =========================================================
loadFolder();
