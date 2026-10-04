/* filewall - shared helpers: api fetch, icons, formatting */

const BASE_PATH = document.body.dataset.basePath || "";

const api = (path, options = {}) =>
    fetch(`${BASE_PATH}/api${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
    }).then(async (response) => {
        if (response.status === 401) {
            window.location.href = `${BASE_PATH}/login`;
            throw new Error("unauthenticated");
        }
        if (!response.ok) {
            const body = await response.json().catch(() => ({}));
            throw new Error(body.detail || `HTTP ${response.status}`);
        }
        return response.json();
    });

function formatSize(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    const units = ["KB", "MB", "GB", "TB"];
    let value = bytes;
    let unit = -1;
    while (value >= 1024 && unit < units.length - 1) {
        value /= 1024;
        unit += 1;
    }
    return `${value.toFixed(value >= 10 ? 0 : 1)} ${units[unit]}`;
}

/* ---------- icons (lucide.dev, MIT) ----------
   the framework ships no icons: filewall registers the few it uses and
   references them via <druid-icon name> / <druid-icon-button icon> */

const svg = (paths) =>
    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ` +
    `stroke-linecap="round" stroke-linejoin="round">${paths}</svg>`;

const ICONS = {
    check: svg('<path d="M20 6 9 17l-5-5"/>'),
    file: svg(
        '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/>'
    ),
    folder: svg(
        '<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/>'
    ),
    "folder-up": svg(
        '<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/><path d="M12 10v6"/><path d="m9 13 3-3 3 3"/>'
    ),
    refresh: svg(
        '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/>' +
            '<path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>'
    ),
};

// druids.js is a module: it runs after this classic script but before
// DOMContentLoaded, the registry notifies elements that already rendered
window.addEventListener("DOMContentLoaded", () => druids.registerIcons(ICONS));
