# Changelog

All notable changes to TinyUI are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.2.0] — 2026-03-24

### Added
- Introduced `tinywidgets` package — self-contained widget system with its own QML engine, separated from `tinycore`
- Introduced `tinycore/qt/` — shared Qt bootstrap (`create_application`, `create_engine`, `PollLoop`)
- Introduced `tinycore/poll/` — `Tickable` protocol, pure Python, no Qt dependency
- Introduced `src/app/` composition root — single place that wires all layers together
- First working overlay widget: `TextWidget` with live LMU telemetry, threshold colors, flash effect, and drag-to-position
- Each widget is an independent `Qt.Tool` window — transparent background is click-through by default
- Widget settings panel in the Widgets tab — edit label, position, flash target, and thresholds live
- Threshold colors editable via built-in color picker; add and remove thresholds at runtime
- Flash configured per threshold entry (with per-entry speed) — blinks when the value enters that band
- Threshold logic uses upper bounds — color applies while value is at or below that entry's number
- `plugin.toml` supports `[mock_connector]` section to declare a test data source per plugin
- `MockConnector` sweep configurable at runtime: min, max, and step
- Demo button in the widget settings header — switches between live and mock connector on the fly
- Demo settings (min, max, speed) slide in directly below the widget header when demo is active

### Changed
- Entry point changed from `tinyui.main:main` to `app.main:main`
- `tinyui.main` refactored into `launch(core, lifecycle)` — boot sequence moved to composition root
- Central logger moved from `tinyui.log` to `tinycore.log` — now shared across all layers
- `WidgetRegistry` and `WidgetSpec` moved from `tinycore`/`PluginContext` to `tinywidgets`
- Window chrome dimensions moved from inline literals to `Theme` constants
- `NumberStepper` and `ThemedComboBox` extracted as shared QML components reused across settings and widget panel
- Widget settings panel layout aligned with the SettingsDialog style (same row heights, label/control columns)

### Fixed
- Editor buttons in the status bar now open the settings panel instead of logging to console
- Title bar left zone now syncs when the dropdown menu opens, preventing drag zone overlap with menu items
- Menu dismiss area now covers the tab bar so switching tabs while a menu is open works correctly
- Widget windows now close automatically when the main window closes

### Removed
- Removed `plugins/demo2` and `plugins/tinypedal` placeholders
- Removed `TyreDemoViewModel` — connector lifecycle managed by the plugin system
- Removed `DemoTab` from the UI
- Removed placeholder settings that had no working implementation (`language`, demo overlay settings)

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
