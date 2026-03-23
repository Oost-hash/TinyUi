# Changelog

All notable changes to TinyUI are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.1.0] — 2026-03-23 — Foundation

First public pre-release. The core architecture is in place and the LMU demo
shows live tyre data while driving. Not production-ready yet — see the roadmap
in the README for what comes next.

### Added
- **Plugin system** — data-driven plugin definitions via TOML, user config via JSON
- **QML overlay** — frameless, always-on-top window with custom Win32 chrome
  (DWM shadow, rounded corners, snap/resize), Linux/Wayland resize handles
- **Settings dialog** — per-plugin settings with toggle, stepper, dropdown,
  text input and color picker controls
- **Color picker** — HSV square + hue slider, callout window that floats above
  the trigger swatch and can draw outside the main window bounds
- **Telemetry ABCs** — `TelemetryReader` abstract base classes in `tinycore`
  for State, Tyre, Engine, Lap, Session and more
- **LMU connector** — reads Le Mans Ultimate shared memory via `pyLMUSharedMemory`
  submodule; detects game running via psutil, active session via `gamePhase`
- **Demo tab** — live FL/FR/RL/RR tyre cards showing surface temp, inner temp,
  pressure and wear while on track
- **Console window** (F12) — structured log viewer with per-level color coding
  and DEBUG/INFO/WARN/ERROR filter chips
- **Build pipeline** — PyInstaller `--onedir` build via `scripts/build.py`,
  GitHub Actions CI for Windows and Linux with manual dispatch and dry-run option

### Known limitations
- Connector is instantiated directly in the ViewModel, not via the plugin system
- Click zones on the main window need further polish
- Linux build is untested end-to-end
- macOS is not supported

[0.1.0]: https://github.com/Oost-hash/TinyUi/releases/tag/v0.1.0
