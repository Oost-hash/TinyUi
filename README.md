# TinyUi

[![Version](https://img.shields.io/badge/version-0.2.0-purple)](https://github.com/Oost-hash/TinyUi/releases/tag/v0.2.0)
[![Status](https://img.shields.io/badge/status-work%20in%20progress-orange)](#roadmap---will-be-moved-to-project)
[![License](https://img.shields.io/badge/license-GPLv3-green)](LICENSE)
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-%E2%9D%A4-%23db61a2?logo=github)](https://github.com/sponsors/oost-hash)

---

## Table of Contents

- [What is TinyUi?](#what-is-tinyui)
- [Supported platforms](#supported-platforms)
- [Roadmap](#roadmap---will-be-moved-to-project)
- [Architecture](#architecture)
- [Plugin model](#plugin-model)
- [Help Wanted: Logo](#help-wanted-tinyui-logo)
- [Credits](#credits)
- [AI use](#ai-use)
- [License](#license)

---

## What is TinyUi?

TinyUi is a modular overlay toolkit for sim racing. The goal is a platform where you can connect to any supported game, build or install plugins, and display live telemetry data as overlays on your screen — without any of those pieces being tangled up with each other.

It started as an attempt to extend [TinyPedal](https://github.com/TinyPedal/TinyPedal). When that turned out to be impossible without rewriting the core, that became the project.

The architecture is split into three hard layers:

- **tinycore** — a generic engine with no domain knowledge. Plugin lifecycle, config store, event bus, provider registry.
- **plugins** — where game-specific code lives. A plugin connects to a game, reads telemetry, and exposes it through the provider API. Plugins run in isolated subprocesses.
- **tinyui** — the overlay UI, built in QML. Talks to tinycore, knows nothing about games.

Nothing is set in stone yet. The design evolves as the project does.

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
| Le Mans Ultimate | LMU shared memory | ✅ Working |
| rFactor 2 | LMU shared memory | ✅ Should work (same API) |

---

## Roadmap - (will be moved to project)

### 0.1.0 — Foundation
The goal for 0.1 is a working foundation: the engine, the UI shell, and the first real game connector.

- [x] Plugin system — lifecycle, isolation, subprocess support
- [x] Data-driven config — TOML for plugin definitions, JSON for user data
- [x] QML overlay — windowing, theming, tab layout
- [x] Telemetry ABCs — abstract connector contract in tinycore
- [x] LMU connector — first real game connector (Le Mans Ultimate / rFactor 2)

### 0.2.0 — Widget renderer
Once the foundation is solid, the focus shifts to actually rendering data on screen.

- [x] Widget system — define and render overlay widgets from plugin data
- [x] Layout engine — position, resize, and stack widgets on screen
- [x] Widget config — per-widget settings via the data-driven config system

### 0.3.0 - Widget globals and hotkeys
In this update I want too introduce a new system and add globals too widgets

- [ ] implement widget global settings
- [ ] implement tinyHotkey
- [ ] add indicators: hotkey, game connection
- [ ] improve debugging

### Later
Ideas that are on the radar but not scheduled yet:

- Reimplement processing of data (modules, plugin layer?) 
- Spotter?

---

## Architecture

```mermaid
graph TB

    subgraph Core["tinycore — Core Engine"]
        direction TB
        store[Config Store]
        bus[Event Bus]
        pluginsys[Plugin System\nlifecycle · isolation · subprocess]
        providers[Provider Registry]
        telemetry[Telemetry ABCs\n🚧 in progress]
    end

    subgraph QML["tinyui — UI Platform  •  QML"]
        direction TB
        qmlviews[QML Views\ncomponents · layout · tabs]
        viewmodels[ViewModels]
        windowing[Windowing]
    end

    subgraph Plugins["Plugins"]
        direction TB
        tp[tinypedal\nloaders · models]
        demo[demo\nreference implementation]
        connector[LMU Connector\n🚧 in progress]
    end

    Plugins -->|register providers| Core
    QML -->|uses core services| Core
    demo --> connector
    connector -.->|implements| telemetry

    style Core fill:#2c3e50,color:#fff
    style QML fill:#2980b9,color:#fff
    style Plugins fill:#e67e22,color:#fff
```

---

## Plugin model

Plugins are self-contained packages. A minimal plugin needs:

- `plugin.py` — implements the `Plugin` protocol (`register`, `start`, `stop`)
- `editors.toml` — declarative config UI definition
- Default dicts — user config is auto-generated on first boot

The `demo` plugin is the reference implementation and stays in sync with the current plugin API.

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

Built on top of ideas and data models from [TinyPedal](https://github.com/TinyPedal/TinyPedal) by s-victor.

---

## AI use

This project was developed with AI assistance to move fast from idea to MVP as a one-person team. The code is curated and adjusted where needed — AI is a tool, not the author.

---

## License

GPLv3 — see [LICENSE](LICENSE).
