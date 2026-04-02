# TinyUi

[![Release](https://img.shields.io/badge/released-0.4.0-green)](https://github.com/Oost-hash/TinyUi/releases/tag/v0.4.0)
[![License](https://img.shields.io/badge/license-GPLv3-green)](LICENSE)
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-%E2%9D%A4-%23db61a2?logo=github)](https://github.com/sponsors/oost-hash)

---

## Table of Contents

- [What is TinyUi?](#what-is-tinyui)
- [Architecture](#architecture)
- [Development](#development)
- [Supported platforms](#supported-platforms)
- [Help Wanted: Logo](#help-wanted-tinyui-logo)
- [Credits](#credits)
- [AI use](#ai-use)
- [License](#license)

---

## What is TinyUi?

TinyUi is a modular overlay platform for sim racing with a manifest-driven plugin system.

The goal is simple: connect to supported games, install or build plugins, and show live telemetry as overlays — without turning game integration, runtime logic, and UI into one monolithic app.

Everything declares itself via `manifest.toml`. The runtime reads these manifests, loads plugins in the right order, and gives each one a scoped context to work in. No hardcoded menus, no magic global state.

---

## Architecture

TinyUi is built around three concepts:

- **runtime** — The orchestrator. Reads manifests, manages settings persistence, handles plugin discovery and activation order. Lives in `src/runtime/`.

- **app_api** — The windowing and theming layer. Gives every plugin a chrome (titlebar, menu, statusbar) and handles QML surface loading. Lives in `src/app_api/`.

- **plugins** — Self-contained units that declare themselves via `manifest.toml`. Three types:
  - **host** (`tinyui`) — The application framework. Declares the main window, built-in dialogs, and the plugin panel.
  - **plugin** — UI plugins that add functionality. Can declare windows, settings, and menu items.
  - **connector** — Data providers with no UI. Export capabilities like telemetry for other plugins to consume.

Plugins never import runtime internals directly. They receive a `PluginContext` at activation with scoped settings access. Menu items, windows, and settings are declared in `manifest.toml`, not created in code.

---

## Development

For the latest release overview and current direction, see [docs/ROADMAP.md](docs/ROADMAP.md). It is a live document that gets updated as the project evolves.

---

## Supported platforms

| Platform | Status | Notes |
|----------|--------|-------|
| Windows 10 / 11 | ✅ Supported | Primary development and test platform |
| Linux | ⚠️ Builds, end-to-end untested | Overlay and widget behavior not verified — issues welcome |
| macOS | ❌ Not supported | No builds, no hardware to test on |

**Supported games:**

| Game | Connector | Status |
|------|-----------|--------|
| Le Mans Ultimate | LMU_RF2_Connector | ✅ Working |
| rFactor 2 | LMU_RF2_Connector | ✅ Should work (same API) |

---

## Help Wanted: TinyUi Logo

Looking for a community-contributed logo for **TinyUi**!

- Clean and recognizable at small sizes (32×32 up to 256×256)
- Fits the vibe of a lightweight overlay tool
- "Ui" or "TinyUi" in some form is a plus, not required

Open an issue with `[logo-proposal]` and share your design. All submissions welcome — rough concepts, SVGs, PNGs, anything. Contributors get credited. ⭐

Submitted logos are released under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

---

## Credits

TinyUi builds on lessons, ideas, and data model inspiration from
[TinyPedal](https://github.com/TinyPedal/TinyPedal) by s-victor.

TinyUi is not a fork of TinyPedal. It became its own project after it became
clear that the desired architecture required a different core.

---

## AI use

This project was developed with AI assistance to move fast from idea to MVP as a one-person team. The code is curated and adjusted where needed — AI is a tool, not the author.

---

## License

GPLv3 — see [LICENSE](LICENSE).
