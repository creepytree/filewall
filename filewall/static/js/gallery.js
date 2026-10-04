/* filewall - gallery: file cards, multi-select delete and image lightbox */

let galleryFiles = [];
let imagesOnly = true;
let folderMode = false;
let currentDir = "";
let lastIndex = null;
const selected = new Set();

const grid = document.getElementById("file-grid");
const fileCount = document.getElementById("file-count");
const folderBtn = document.getElementById("folder-toggle");
const filterBtn = document.getElementById("filter-toggle");
const selectAllBtn = document.getElementById("select-all");
const downloadBtn = document.getElementById("download-selected");
const deleteBtn = document.getElementById("delete-selected");

async function loadFiles() {
    galleryFiles = await api("/files");
    selected.clear();
    lastIndex = null;
    renderFiles();
}

function dirOf(path) {
    const slash = path.lastIndexOf("/");
    return slash === -1 ? "" : path.slice(0, slash);
}

function filteredFiles() {
    return imagesOnly ? galleryFiles.filter((file) => file.is_image) : galleryFiles;
}

/* files shown in the current view (filter + folder location) */
function visibleFiles() {
    const files = filteredFiles();
    return folderMode ? files.filter((file) => dirOf(file.path) === currentDir) : files;
}

/* direct subfolders of the current dir with their (filtered) item count */
function subFolders() {
    if (!folderMode) return [];
    const prefix = currentDir ? `${currentDir}/` : "";
    const folders = new Map();
    for (const file of filteredFiles()) {
        if (!file.path.startsWith(prefix)) continue;
        const rest = file.path.slice(prefix.length);
        const slash = rest.indexOf("/");
        if (slash === -1) continue;
        const name = rest.slice(0, slash);
        folders.set(name, (folders.get(name) || 0) + 1);
    }
    return [...folders.entries()].sort((a, b) => a[0].localeCompare(b[0]));
}

function enterDir(dir) {
    currentDir = dir;
    selected.clear();
    lastIndex = null;
    renderFiles();
}

function icon(name, size) {
    const el = document.createElement("druid-icon");
    el.setAttribute("name", name);
    el.setAttribute("size", size);
    return el;
}

function rawUrl(path) {
    return `${BASE_PATH}/api/files/raw?path=${encodeURIComponent(path)}`;
}

function thumbUrl(path) {
    return `${BASE_PATH}/api/files/thumb?path=${encodeURIComponent(path)}`;
}

function fileCard(file, index) {
    const card = document.createElement("div");
    card.className = "file-card";
    if (selected.has(file.path)) card.classList.add("selected");

    const thumb = document.createElement("div");
    thumb.className = "file-thumb";
    if (file.is_image) {
        thumb.classList.add("viewable");
        const img = document.createElement("img");
        img.src = thumbUrl(file.path);
        img.alt = file.name;
        img.loading = "lazy";
        img.decoding = "async";
        img.draggable = false;
        thumb.appendChild(img);
        thumb.title = "View image";
        thumb.addEventListener("click", () => openLightbox(file));
    } else {
        thumb.appendChild(icon("file", "42px"));
    }
    card.appendChild(thumb);

    // filetype badge top right
    const badge = document.createElement("span");
    badge.className = "df-badge file-badge";
    const dot = file.name.lastIndexOf(".");
    badge.textContent = dot > 0 ? file.name.slice(dot + 1).toUpperCase() : "FILE";
    card.appendChild(badge);

    const info = document.createElement("div");
    info.className = "file-info";
    const name = document.createElement("div");
    name.className = "file-name";
    // folder mode shows the plain name, flat mode the full path
    name.textContent = folderMode ? file.name : file.path;
    name.title = file.path;
    const meta = document.createElement("div");
    meta.className = "file-meta";
    meta.textContent = `${formatSize(file.size)} · ${file.modified}`;
    info.append(name, meta);
    card.appendChild(info);
    // bare infos only, non-image cards toggle selection on click
    if (!file.is_image) {
        info.style.cursor = "pointer";
        info.addEventListener("click", (event) => handleSelect(file, index, event.shiftKey));
    }

    const select = document.createElement("druid-icon-button");
    select.className = "file-select";
    select.setAttribute("icon", "check");
    select.setAttribute("label", "Select (shift-click for range)");
    select.setAttribute("circle", "");
    select.setAttribute("small", "");
    if (selected.has(file.path)) select.setAttribute("active", "");
    select.addEventListener("click", (event) => {
        event.stopPropagation();
        handleSelect(file, index, event.shiftKey);
    });
    card.appendChild(select);

    return card;
}

function folderCard(name, count, target) {
    const card = document.createElement("div");
    card.className = "file-card folder";

    const thumb = document.createElement("div");
    thumb.className = "file-thumb";
    thumb.appendChild(icon(name === ".." ? "folder-up" : "folder", "42px"));
    card.appendChild(thumb);

    const info = document.createElement("div");
    info.className = "file-info";
    const label = document.createElement("div");
    label.className = "file-name";
    label.textContent = name;
    const meta = document.createElement("div");
    meta.className = "file-meta";
    meta.textContent = count === null ? "up" : `${count} item${count === 1 ? "" : "s"}`;
    info.append(label, meta);
    card.appendChild(info);

    card.addEventListener("click", () => enterDir(target));
    return card;
}

function renderFiles() {
    const visible = visibleFiles();
    const folders = subFolders();
    grid.innerHTML = "";
    if (folderMode && currentDir) {
        grid.appendChild(folderCard("..", null, dirOf(currentDir)));
    }
    folders.forEach(([name, count]) => {
        grid.appendChild(folderCard(name, count, currentDir ? `${currentDir}/${name}` : name));
    });
    if (!visible.length && !folders.length) {
        const empty = document.createElement("div");
        empty.className = "df-empty file-empty";
        const title = document.createElement("div");
        title.className = "df-empty-title";
        title.textContent = imagesOnly ? "No image files" : "No files";
        empty.append(title, document.createTextNode("Nothing to show in the mounted folder."));
        grid.appendChild(empty);
    }
    visible.forEach((file, index) => grid.appendChild(fileCard(file, index)));
    updateToolbar();
}

function handleSelect(file, index, shift) {
    const visible = visibleFiles();
    // shift: select everything between the last clicked card and this one
    if (shift && lastIndex !== null && lastIndex !== index) {
        const [from, to] = [Math.min(lastIndex, index), Math.max(lastIndex, index)];
        for (let i = from; i <= to; i++) selected.add(visible[i].path);
    } else if (selected.has(file.path)) {
        selected.delete(file.path);
    } else {
        selected.add(file.path);
    }
    lastIndex = index;
    renderFiles();
}

function updateToolbar() {
    const total = visibleFiles().length;
    const kind = imagesOnly ? "image" : "file";
    const where = folderMode ? `/${currentDir} · ` : "";
    fileCount.textContent =
        where +
        (selected.size
            ? `${selected.size} of ${total} ${kind}${total === 1 ? "" : "s"} selected`
            : `${total} ${kind}${total === 1 ? "" : "s"}`);
    folderBtn.active = folderMode;
    deleteBtn.disabled = !selected.size;
    deleteBtn.textContent = selected.size ? `delete (${selected.size})` : "delete";
    downloadBtn.disabled = !selected.size;
    downloadBtn.textContent = selected.size ? `download (${selected.size})` : "download";
    selectAllBtn.textContent = total && selected.size === total ? "clear selection" : "select all";
    selectAllBtn.disabled = !total;
    filterBtn.textContent = imagesOnly ? "images" : "all files";
    filterBtn.active = imagesOnly;
}

folderBtn.addEventListener("toggle-change", (event) => {
    folderMode = event.detail.active;
    currentDir = "";
    selected.clear();
    lastIndex = null;
    renderFiles();
});

filterBtn.addEventListener("toggle-change", (event) => {
    imagesOnly = event.detail.active;
    selected.clear();
    lastIndex = null;
    renderFiles();
});

selectAllBtn.addEventListener("click", () => {
    const visible = visibleFiles();
    if (selected.size === visible.length) {
        selected.clear();
    } else {
        visible.forEach((file) => selected.add(file.path));
    }
    lastIndex = null;
    renderFiles();
});

downloadBtn.addEventListener("click", async () => {
    const paths = [...selected];
    if (!paths.length) return;
    // single file directly, multiple as zip
    if (paths.length === 1) {
        window.location.href = `${rawUrl(paths[0])}&download=true`;
        return;
    }
    const response = await fetch(`${BASE_PATH}/api/files/download`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ paths }),
    });
    if (!response.ok) {
        druids.toast(`Download failed (HTTP ${response.status})`, "danger");
        return;
    }
    const url = URL.createObjectURL(await response.blob());
    const link = document.createElement("a");
    link.href = url;
    link.download = "filewall.zip";
    link.click();
    URL.revokeObjectURL(url);
});

deleteBtn.addEventListener("click", async () => {
    const paths = [...selected];
    if (!paths.length) return;
    const label = `${paths.length} file${paths.length === 1 ? "" : "s"}`;
    if (!(await druids.confirm(`Delete ${label} from the mounted folder?`, { confirmLabel: "delete", danger: true }))) return;
    try {
        const { deleted, failed } = await api("/files/delete", { method: "POST", body: JSON.stringify({ paths }) });
        const plural = (n) => `${n} file${n === 1 ? "" : "s"}`;
        if (deleted.length) druids.toast(`Deleted ${plural(deleted.length)}`, "ok");
        if (failed.length) druids.toast(`Could not delete ${plural(failed.length)}`, "danger");
    } catch (error) {
        druids.toast(`Delete failed: ${error.message}`, "danger");
    }
    loadFiles();
});

document.getElementById("gallery-refresh").addEventListener("click", loadFiles);

/* ---------- lightbox ---------- */

// framework modal brings backdrop, esc and focus trap; the image sizing is app css
function openLightbox(file) {
    const content = document.createElement("figure");
    content.className = "file-lightbox";
    const img = document.createElement("img");
    img.src = rawUrl(file.path);
    img.alt = file.name;
    const caption = document.createElement("figcaption");
    caption.className = "df-muted";
    caption.textContent = `${formatSize(file.size)} · ${file.modified}`;
    content.append(img, caption);
    druids.modal({ title: file.path, content, actions: [{ label: "close" }] }).classList.add("file-lightbox-dialog");
}
