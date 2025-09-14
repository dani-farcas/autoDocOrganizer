// =========================================================
// 📂 AutoDocOrganizer – Frontend-Skripte
// =========================================================

let currentPath = "";   // Start = root (Archive)
let contextMenu;

// 🌍 Unterstützte Sprachen
const supportedLanguages = [
  { code: "EN-US", name: "Englisch (US)" },
  { code: "EN-GB", name: "Englisch (UK)" },
  { code: "DE", name: "Deutsch" },
  { code: "FR", name: "Französisch" },
  { code: "IT", name: "Italienisch" },
  { code: "ES", name: "Spanisch" },
  { code: "NL", name: "Niederländisch" },
  { code: "PL", name: "Polnisch" },
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

  closeBtn.onclick = () => { banner.style.display = "none"; };

  setTimeout(() => {
    if (banner.style.display === "flex") banner.style.display = "none";
  }, 3000);
}

// =========================================================
// 📤 Upload (Formular + Dateiliste)
// =========================================================
document.addEventListener("DOMContentLoaded", () => {
  const uploadForm = document.getElementById("upload-form");
  const fileInput = document.getElementById("file-upload");
  const importBtn = document.getElementById("import-btn");
  const fileList = document.getElementById("selected-files");

  if (fileInput && importBtn && fileList) {
    // 📝 Dateien anzeigen, wenn ausgewählt
    fileInput.addEventListener("change", () => {
      fileList.innerHTML = "";

      if (fileInput.files.length > 0) {
        Array.from(fileInput.files).forEach((file, idx) => {
          const li = document.createElement("li");

          // Dateiname + Größe
          const span = document.createElement("span");
          span.textContent = `${file.name} (${Math.round(file.size / 1024)} KB)`;

          // ❌ Entfernen-Button für einzelne Datei
          const removeBtn = document.createElement("button");
          removeBtn.textContent = "✖";
          removeBtn.onclick = () => {
            const dt = new DataTransfer();
            Array.from(fileInput.files)
              .filter((_, i) => i !== idx)
              .forEach(f => dt.items.add(f));
            fileInput.files = dt.files;
            fileInput.dispatchEvent(new Event("change"));
          };

          li.appendChild(span);
          li.appendChild(removeBtn);
          fileList.appendChild(li);
        });

        importBtn.disabled = false; // Button aktivieren
      } else {
        importBtn.disabled = true;
      }
    });

    // 📤 Upload auslösen
    if (uploadForm) {
      uploadForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        if (fileInput.files.length === 0) {
          showBanner("⚠️ Bitte zuerst Dateien auswählen!", "error");
          return;
        }

        const loader = document.getElementById("upload-loader");
        loader.style.display = "inline-block";

        try {
          const res = await fetch("/upload", { method: "POST", body: new FormData(this) });
          if (res.ok) {
            showBanner("✅ Upload erfolgreich!", "success");
            fileList.innerHTML = "";
            fileInput.value = "";
            importBtn.disabled = true;
            loadFolder(currentPath);
          } else showBanner("❌ Fehler beim Upload", "error");
        } catch (err) {
          showBanner("⚠️ Netzwerkfehler: " + err.message, "error");
        } finally { loader.style.display = "none"; }
      });
    }
  }
});

// =========================================================
// 📂 Drag & Drop Upload
// =========================================================
const dropZone = document.getElementById("drop-zone");
if (dropZone) {
  dropZone.addEventListener("dragover", e => { e.preventDefault(); dropZone.classList.add("dragover"); });
  dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
  dropZone.addEventListener("drop", async (e) => {
    e.preventDefault(); dropZone.classList.remove("dragover");
    const files = e.dataTransfer.files; if (files.length === 0) return;

    const formData = new FormData();
    for (let file of files) formData.append("files", file);

    const loader = document.getElementById("upload-loader");
    loader.style.display = "inline-block";

    try {
      const res = await fetch("/upload", { method: "POST", body: formData });
      if (res.ok) {
        const confirmDelete = confirm("✅ Upload erfolgreich!\n\nOriginal-Dateien löschen?");
        if (confirmDelete) {
          await fetch("/delete_originals", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ filenames: Array.from(files).map(f => f.name) })
          });
          showBanner("🗑️ Originale gelöscht", "success");
        } else showBanner("✅ Dateien behalten", "success");
        loadFolder(currentPath);
      } else showBanner("❌ Fehler beim Upload", "error");
    } catch (err) {
      showBanner("⚠️ Netzwerkfehler: " + err.message, "error");
    } finally { loader.style.display = "none"; }
  });
}

// =========================================================
// 📌 Breadcrumb Navigation
// =========================================================
function renderBreadcrumb(path) {
  const parts = path.split(/[\\/]/).filter(Boolean);
  let breadcrumb = `<span onclick="loadFolder('')">Archive</span>`;
  let partial = "";
  parts.forEach((part, i) => {
    partial += (i === 0 ? part : "/" + part);
    breadcrumb += " / ";
    breadcrumb += `<span onclick="loadFolder('${partial}')">${part}</span>`;
  });
  document.getElementById("breadcrumb").innerHTML = breadcrumb;
}

// =========================================================
// 📂 Ordner & Dateien laden
// =========================================================
async function loadFolder(path = "") {
  currentPath = path;
  const res = await fetch(`/list?path=${encodeURIComponent(currentPath)}`);

  if (!res.ok) {
    showBanner("❌ Fehler beim Laden des Verzeichnisses", "error");
    return;
  }

  const items = await res.json();
  renderBreadcrumb(currentPath);

  const ul = document.getElementById("file-list");
  ul.innerHTML = "";

  items.forEach(item => {
    const relPath = currentPath ? currentPath + "/" + item.name : item.name;
    const li = document.createElement("li");
    li.textContent = (item.is_dir ? "📂 " : "📄 ") + item.name;

    if (item.is_dir) {
      li.ondblclick = () => loadFolder(relPath);
      li.oncontextmenu = e => { e.preventDefault(); showFolderMenu(e.pageX, e.pageY, relPath); };
    } else {
      li.ondblclick = () => openFile(relPath);
      li.oncontextmenu = e => { e.preventDefault(); showFileMenu(e.pageX, e.pageY, relPath); };
    }
    ul.appendChild(li);
  });
}

// =========================================================
// 📄 Datei öffnen / herunterladen
// =========================================================
function openFile(path) { window.open(`/download?file=${encodeURIComponent(path)}`, "_blank"); }
function downloadFile(path) { window.location.href = `/force_download?file=${encodeURIComponent(path)}`; }

// =========================================================
// ✏️ Datei / Ordner umbenennen
// =========================================================
async function renameFile(path) {
  const newName = prompt("Neuer Dateiname:", path.split("/").pop()); if (!newName) return;
  const res = await fetch("/rename", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ old: path, new: (currentPath ? currentPath + "/" : "") + newName })
  });
  if (res.ok) loadFolder(currentPath); else showBanner("❌ Fehler beim Umbenennen", "error");
}

async function renameFolder(path) {
  const newName = prompt("Neuer Ordnername:", path.split("/").pop()); if (!newName) return;
  const res = await fetch("/rename_folder", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ old: path, new: (path.split("/").slice(0,-1).join("/") + "/" + newName) })
  });
  if (res.ok) loadFolder(currentPath); else showBanner("❌ Fehler beim Umbenennen des Ordners", "error");
}

// =========================================================
// ❌ Datei / Ordner löschen (Unified Endpoint `/delete`)
// =========================================================
async function deleteFile(path) {
  if (!confirm("Datei wirklich löschen?")) return;
  const res = await fetch("/delete", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ filenames: [path] })
  });
  if (res.ok) {
    showBanner("🗑️ Datei gelöscht", "success");
    loadFolder(currentPath);
  } else {
    showBanner("❌ Fehler beim Löschen der Datei", "error");
  }
}

async function deleteFolder(path) {
  if (!confirm("Ordner wirklich löschen (nur wenn leer)?")) return;
  const res = await fetch("/delete", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ filenames: [path] })
  });
  if (res.ok) {
    showBanner("🗑️ Ordner gelöscht", "success");
    loadFolder(currentPath);
  } else {
    showBanner("❌ Fehler beim Löschen des Ordners", "error");
  }
}

// =========================================================
// 🔍 Archiv durchsuchen
// =========================================================
document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("search-input");
  if (searchInput) {
    searchInput.addEventListener("input", async () => {
      const query = searchInput.value.trim();
      if (query.length < 2) { loadFolder(currentPath); return; }

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
      } catch { showBanner("❌ Fehler bei der Suche", "error"); }
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
  contextMenu.style.top = y + "px"; contextMenu.style.left = x + "px";
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
  contextMenu.style.top = y + "px"; contextMenu.style.left = x + "px";
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
async function translateFile(path) { createModal(path, "Übersetzen", "/translate"); }
async function explainFile(path) { createModal(path, "Erklären", "/explain"); }

function createModal(path, actionLabel, endpoint) {
  const select = document.createElement("select");
  supportedLanguages.forEach(lang => {
    const opt = document.createElement("option");
    opt.value = lang.code; opt.textContent = `${lang.name} (${lang.code})`;
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
    const res = await fetch(`${endpoint}?file=${encodeURIComponent(path)}&lang=${encodeURIComponent(lang)}`);
    outputArea.value = await res.text();
  };

  const closeBtn = document.createElement("button");
  closeBtn.textContent = "Schließen";
  closeBtn.onclick = () => document.body.removeChild(modal);

  btnDiv.appendChild(okBtn); btnDiv.appendChild(closeBtn); wrapper.appendChild(btnDiv);

  const modal = document.createElement("div");
  modal.className = "modal"; modal.appendChild(wrapper); document.body.appendChild(modal);
}

// =========================================================
// 🚀 Initial laden
// =========================================================
document.addEventListener("DOMContentLoaded", () => {
  loadFolder("");   // Root = Archive
});
