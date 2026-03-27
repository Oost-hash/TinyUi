# TinyUi

[![Release](https://img.shields.io/badge/released-0.3.0-green)](https://github.com/Oost-hash/TinyUi/releases/tag/v0.3.0)
[![License](https://img.shields.io/badge/license-GPLv3-green)](LICENSE)
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-%E2%9D%A4-%23db61a2?logo=github)](https://github.com/sponsors/oost-hash)

---

## Table of Contents

- [Development](#latest-update)
- [What is TinyUi?](#what-is-tinyui)
- [Supported platforms](#supported-platforms)
- [Help Wanted: Logo](#help-wanted-tinyui-logo)
- [Credits](#credits)
- [AI use](#ai-use)
- [License](#license)

---

## What is TinyUi?

TinyUi is a modular overlay platform for sim racing.

The goal is simple: connect to supported games, install or build plugins, and
show live telemetry as overlays without turning game integration, runtime
logic, and UI into one monolithic app.

The architecture is split into four hard layers:

- **tinycore** — the host runtime. Session ownership, capability binding, subprocess consumer hosting, config persistence, and inspection.
- **plugins** — where game-specific and runtime-facing plugin code lives. Plugins split into explicit provider and consumer roles.
- **tinywidgets** — the widget runtime and overlay rendering layer. Turns plugin-fed data into on-screen widget behavior.
- **tinyui** — the overlay UI, built in QML. Talks to tinycore, knows nothing about games.

TinyUi is still early, but the direction is clear: build a clean
plugin platform, make the runtime fast and understandable, and then layer a
better day-to-day overlay experience on top.

---

## Development

For the latest release overview and current direction, see [docs/ROADMAP.md](docs/ROADMAP.md). It is a live document, gets updated most often, and the next update is still being planned there.

Legend: `[ ]` planned, `[x]` completed.

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
