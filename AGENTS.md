# Filewall — agent reference

<!--
Template for a consumer app of the druids design framework. Copy this file to the
consumer app's repo root as AGENTS.md, replace <App>/<app>, and fill the Layout
section with the app's own files. Everything between the druids:generic markers is
generic — keep it as-is so every consumer app follows the same rules, and re-copy it
from this template whenever the framework is updated (step 3 of "On resuming edits").
The substitutions to re-apply after a re-copy are `<App>`, `<app>` and
`<framework-repo-url>`.
This is the pip / FastAPI + Jinja variant; an npm consumer (a Lit app, a browser
extension) uses AGENTS.consumer.npm.md instead.
-->

Filewall is a **consumer of the `druids` design framework** (pip name `druidforms`,
import name `druids`). It is pure Python: FastAPI + Jinja. It ships **no JS build
step** — all design, theming, the app shell, login/session and every `<druid-*>`
element come from the installed `druids` package.

<!-- druids:generic:start — everything down to druids:generic:end is copied verbatim from
     the framework's template (druids/AGENTS.consumer.md). Do not edit it here: the framework
     owns it, and step 3 of "On resuming edits" overwrites it on every framework update.
     The only edits that survive are the placeholder substitutions listed above. App-specific
     content goes below druids:generic:end. -->

## On resuming edits

1. **Create a venv** and activate it: `python -m venv .venv && . .venv/bin/activate`.
2. **Update the framework** into it from its git URL: `pip install "druidforms @ git+https://github.com/creepytree/druidforms.git"`
3. **Re-sync this file's generic block.** The framework ships the template this file was made
   from. Replace everything between the `druids:generic:start` and `druids:generic:end` markers
   below with the same block from `<site-packages>/druids/AGENTS.consumer.md`, then re-apply the
   substitutions listed in the header comment (`<App>`, `<app>`, `<framework-repo-url>`). If the
   blocks are already identical this is a no-op. Check `README.consumer.md` the same way.
   Skipping this is how an app ends up following rules the framework retired two versions ago.
4. **Study the CHANGELOG.md** Compare local version with latest pull and check if the project needs patches on the new version or would gain quality, simplification or a reduction in line-count by patching.
5. **Read GAPS_FIX.md** if you came from a previous run and reported gaps.
6. **Add bugs, gaps, wanted patches to GAPS.md** This gets consumed by the Agent processing the framework. Overwrite with fresh content on a new edit roundtrip if the file notes a resolved state.
7. **Remove resolved GAPS_FIX.md** if you are done.

## Startup new project

**On the first turn, before writing any UI, install the framework and study it:**

1. **Create a venv** and activate it: `python -m venv .venv && . .venv/bin/activate`.
2. **Install the framework** into the venv `pip install "druidforms @ git+https://github.com/creepytree/druidforms.git"`
3. **Study the framework** in the venv:
   - `<site-packages>/druids/AGENTS.md` — orientation: how to wire the app, page
     templates, `df-*` classes, and the light-DOM composition patterns.
   - `<site-packages>/druids/static/druids.index.txt` — **grep this first**: one line per
     component, `df-*` class, design token and JS API, with tags and a summary. Its header
     lists the tag vocabulary, so `grep " forms"` or `grep "^class"` finds what exists.
   - `<site-packages>/druids/static/druids.components.json` — the **exact contract**
     for every `<druid-*>` and `window.druids` API: attributes, events (with `detail`
     shape), slots, methods, consumed CSS vars, gotchas, example. Read this instead of
     grepping the bundle. `druids.registry.json` = what tags/APIs exist + since which
     version; `druids.tokens.json` = theme tokens with roles + defaults.
   Build UI only from what these document.
4. Write AGENTS.consumer.md in the workspace root of the consumer
5. Write README.consumer.md for the consumer, @placeholder@ define allowed changes, keep it strict on this

## Do always

> **Build on the framework, never reinvent it.** Before adding markup, CSS or JS, check
> whether druids already provides it: a `<druid-*>` component, a `df-*` class, a design
> token (`--accent`, `--border`, `--bg-raised`, `--radius`, …) or `druids.toast()` /
> `druids.applyAccent()`. App CSS must theme with those tokens, not hardcoded colors,
> and must not re-implement a component the framework already ships.
>
> **Keep this app matching the framework's current API.** The shipped contract manifest
> (`druids/static/druids.index.txt` + `druids.components.json` + `.registry.json`) is the source of truth. If a
> druids component, attribute, event or class was renamed or removed upstream, update this
> app's templates/CSS/JS to match in the same change.
>
> **Missing or wrong in the design system → fix it upstream, not here.** If a UI need
> isn't met, add or change the component in the `druids` framework repo (rebuild its
> bundle there) rather than growing a local one-off. Only genuinely app-specific UI
> lives in this app.

<!-- druids:generic:end -->

## Layout

- `filewall/shell.py` — the single `Druids(...)` instance (brand, version, login,
  `templates_dir`); `filewall/app.py` calls `druids.install(app)` (mounts the `/druids`
  assets, login routes and session middleware) and adds the `BASE_PATH` middleware.
- `filewall/env.py` / `filewall/config.py` — env parsing and project metadata (version,
  author, github url) fed into the shell.
- `filewall/files.py` — app-specific: the mounted data-dir file store (recursive listing,
  safe path resolution, cached webp thumbnails, delete).
- `filewall/api.py` — JSON API under `/api`: file listing, raw/thumb serving, zip
  download, delete, and `/api/log` (consumed by `<druid-log-view>`).
- `filewall/routes.py` — the single page, rendered via `druids.templates`.
- `filewall/templates/main.jinja2` — extends `druids/base.jinja2`; fills the `styles`,
  `tabs`, `content`, `scripts` blocks with `<druid-*>` tags (gallery tab + a
  `<druid-log-view>` log tab). No own base/login templates — those come from druids.
- `filewall/static/{css,js}/` — only app-specific UI, all token-driven (so light mode and
  the flavor tint reach it): the file card grid, card hover/selected states, the `.df-badge`
  filetype pill position, the selection `<druid-icon-button>` overlay and the lightbox image
  size in `gallery.css`; cards, folder mode, range select, download and delete in
  `gallery.js`; api fetch, `formatSize` and the Lucide `ICONS` registered via
  `druids.registerIcons()` in `util.js`; init in `app.js`. The toolbar is a `.df-toolbar`
  of `<druid-button>`s (`folders` / `images` are `toggle` buttons driven by `toggle-change`);
  delete asks via `druids.confirm()`, the lightbox is `druids.modal()`, results and errors
  go through `druids.toast()` — no hand-rolled dialogs or overlays. Framework CSS is
  prefixed `df-`; app class names are `file-*` / `fw-*`.
