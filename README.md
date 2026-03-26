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
- [Help Wanted: Logo](#help-wanted-tinyui-logo)
- [Credits](#credits)
- [AI use](#ai-use)
- [License](#license)

---

## What is TinyUi?

TinyUi is a modular overlay toolkit for sim racing. The goal is a platform where you can connect to any supported game, build or install plugins, and display live telemetry data as overlays on your screen — without any of those pieces being tangled up with each other.

It started as an attempt to extend [TinyPedal](https://github.com/TinyPedal/TinyPedal). When that turned out to be impossible without rewriting the core, that became the project.

The architecture is split into three hard layers:

- **tinycore** — the host runtime. Session ownership, capability binding, subprocess consumer hosting, config persistence, and inspection.
- **plugins** — where game-specific and runtime-facing plugin code lives. Plugins now split into explicit provider and consumer roles.
- **tinyui** — the overlay UI, built in QML. Talks to tinycore, knows nothing about games.

The shape is still evolving, but the direction is clear.

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

## Roadmap

### 0.1.0 — Foundation
This release laid down the base: the runtime, the UI shell, and the first working telemetry connector.

- [x] Plugin system — lifecycle, isolation, subprocess support
- [x] Data-driven config — TOML for plugin definitions, JSON for user data
- [x] QML overlay — windowing, theming, tab layout
- [x] First telemetry contract layer
- [x] LMU connector — first real game connector (Le Mans Ultimate / rFactor 2)

### 0.2.0 — Widget renderer
This release got live data onto the screen with the first usable widget workflow.

- [x] Widget system — define and render overlay widgets from plugin data
- [x] Layout engine — position, resize, and stack widgets on screen
- [x] Widget config — per-widget settings via the data-driven config system

### 0.3.0 — Runtime contracts and plugin split
This release is about defining the runtime properly: clear plugin roles, explicit requirements, and a host that binds providers and consumers through contracts instead of plugin-specific wiring.

- [x] Define the new plugin manifest shape around explicit roles and `requires`
- [x] Separate provider-side plugins from consumer-side plugins
- [x] Replace plugin-name-based connector lookup with capability-based binding
- [x] Define the session/runtime services that own activation, binding, and health state
- [x] Improve debugging around runtime state, active bindings, and provider health
- [x] Define the widget-facing data contract model
- [x] Move widget data flow away from direct connector traversal

### 0.4.0 — UI contracts, widget globals, and interaction
Once the runtime contracts are in place, the focus shifts to stable UI-facing data contracts and better day-to-day usability.

- [ ] Implement widget global settings
- [ ] Implement hotkey support
- [ ] Add clear indicators for runtime state such as hotkeys and game connection


### Later
These are on the radar, but not tied to a release yet:

- Processing / derived data layer
- Spotter?
- Custom widgets
- Grouping widgets
- Provider selection UI
- Game detection and source handoff inside provider families
- More connectors and capability coverage

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
