# Changelog

All notable changes to TinyUI are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.4.0] — 2026-03-28
This release rewrites the shape of TinyUi's core. The project no longer treats runtime behavior,
plugin participation, session state, capability binding, polling, and app boot as separate half-owned
systems. `tinycore.runtime` is now the live execution owner, and the surrounding packages are much more
honest about whether they describe static contracts, host wiring, or UI behavior.

The practical result is that TinyUi now boots through an explicit runtime composition, owns its process
graph and scheduling model in one place, exposes a real runtime inspector, and no longer carries the old
`app`, `session`, `capabilities`, and `poll` layers as first-class runtime architecture. This is the
release where the runtime stops feeling provisional and starts reading like the system the project was
actually trying to build.

### Added

#### tinycore
- Introduced a dedicated `tinycore.runtime` layer that owns boot orchestration, runtime unit registration, host workers, scheduling, Qt timer integration, subprocess supervision, activation flow, staged updates, and runtime diagnostics metadata
- Added a runtime-owned plugin participation layer under `tinycore.runtime.plugins` for plugin activation, participant registration, provider activity, provider refresh, subprocess-backed participation, export binding, and live participation facts
- Added a staged runtime update model with explicit `refresh` and `derive` phases, driven by one `RuntimeUpdateLoop`
- Added a runtime graph and runtime inspector that expose live units, parent/process relationships, scheduling metadata, activation state, staged update participants, and task visibility through devtools and diagnostics

#### tinydevtools
- Added a dedicated Runtime tab that shows the live runtime tree with state filters, sorting, resizable columns, copied overview output, and update-stage visibility

### Changed

#### tinycore
- Rebuilt the core around explicit host/runtime composition so boot no longer depends on an `App` container or a flat bag of registries
- Moved live plugin participation out of `tinycore.plugin` and into `tinycore.runtime.plugins`, leaving `tinycore.plugin` focused on manifests, specs, protocols, and plugin-facing context
- Collapsed the old session/capability model into runtime participation facts, exports, bindings, and provider controls so runtime-facing code no longer depends on `SessionRuntime` or a heavyweight capability subsystem
- Moved provider activity, provider refresh, and widget update driving under runtime-owned participation instead of treating them as widget or session behavior
- Renamed the live runtime language around activation, participants, exports, updates, and runtime ownership so the process graph, service API, and diagnostics read as one coherent model
- Reduced the public `tinycore` and `tinycore.runtime` surfaces so callers import through narrower owning modules instead of broad package re-exports
- Split diagnostics into explicit log and runtime surfaces under `tinycore.logging` and `tinycore.diagnostics`
- Tightened persistence and config ownership behind host services and plugin `ctx.config`, instead of leaking raw registries and loader internals into the runtime path

#### tinyui
- Moved TinyUi-specific host assembly and UI adapter wiring out of core and into `tinyui.boot` and `tinyui.ui_adapters`
- Retired the old `app` entry package in favor of the direct `tinyui_boot` bootloader path

#### tinywidgets
- Reframed widget updates as runtime-driven participation, with provider refresh in `refresh` and widget state derivation in `derive`
- Renamed widget-side update mechanics around `WidgetStateParticipant` and the runtime update loop so overlay behavior matches the new runtime language

### Fixed

#### tinycore
- Fixed boot and shutdown ordering so the runtime inspector attaches before state monitoring, the main UI reaches `running` before overlay workers start, and host worker shutdown no longer trips over child runtime state transitions
- Fixed runtime metadata and diagnostics visibility so scheduled work, activation state, provider activity, and staged updates describe the live system more honestly

#### tinyui
- Fixed settings save routing so QML enum and numeric values save through typed viewmodel paths instead of failing conversion during persistence

### Removed

#### tinycore
- Removed the `tinycore.app` package and the last compatibility route through `create_app`
- Removed the old `session`, `capabilities`, and `poll` runtime layers as architectural owners
- Removed the remaining runtime shims for plugin lifecycle/registry/runner paths after moving all live participation into `tinycore.runtime`

#### other
- TinyUi now boots through `tinyui_boot`

## [0.3.0] — 2026-03-26
The main goal of this release was to stop treating the runtime like a loose pile of registries
and start shaping it into a real system. `SessionRuntime` is now the center of provider ownership,
consumer bindings, provider control, and runtime inspection. That gives TinyUI a much cleaner base
for future connectors, game detection, and widgets.

This release also moves the widget system forward in a practical way. Widgets now read through
explicit capability + field contracts, more demo widgets were added to cover the new contracts,
and the LMU provider owns both live and demo sources behind one provider identity. The result is
that the project feels like its taken the shape it was aiming for: clean runtime boundaries,
clear separation of concerns, data driven.

### Added widgets:
- Fuel
- Speed
- Place
- Track
- Time Left (displays in seconds)
- Track Temp

### Added

#### plugins
- LMU connector logs game state transitions with full session context: session type, track, driver, car, class, car count, track temperature, ambient temperature, and game version

#### tinycore
- Log output to terminal and Dev Tools console can now be controlled independently — set `console_level = "INFO"` (or `"DEBUG"`, `"WARNING"`) in `[tool.tinyui.debug]` to attach a terminal handler at that level; omit the key to suppress terminal output entirely
- Debug categories can be toggled at runtime from Dev Tools without restarting; `ALL_CATEGORIES` constant lists all available channels

#### tinyui
- Dev Tools State tab now has a source selector — choose a widget context or connector to inspect; widget context properties are read live via QMetaObject introspection

### Changed

#### app
- Windows builds now boot through a dedicated launcher and bundle the new runtime packages correctly, so the packaged app follows the same entry path as the source tree

#### plugins
- Established the new plugin baseline: `demo` now declares a consumer manifest without bundled connector code, and `lmu_connector` now owns the shared-memory submodules and provider-side connector split
- Folded mock telemetry into the LMU provider family so `lmu_connector` now owns both real and demo sources behind one provider identity
- Moved LMU provider inspection snapshots into `lmu_connector` so runtime inspection no longer carries telemetry-specific state field maps in `tinycore`
- Moved the telemetry reader contract out of `tinycore` and into `lmu_connector`, so provider-side game contracts now live with the plugin that owns them
- Renamed several LMU session, lap, and timing API methods to clearer exposed contract names such as `session_time_left`, `session_kind`, `current_lap`, and `gap_to_leader`

#### tinycore
- Reworked plugin manifest parsing around `plugin.consumer` and `plugin.provider`, and updated the app bootstrap to load consumer logic separately from host-side providers
- Added a capability registry that records provider exports, resolves consumer `requires`, and logs missing or successful bindings during app bootstrap
- Introduced a session runtime that owns active providers and per-consumer capability bindings instead of leaving binding state embedded in the registry layer
- Added session-level demo-mode passthrough methods so the UI can request provider-owned demo leases without rebinding capabilities
- Moved runtime inspection source and snapshot logic into a new runtime inspector service, leaving Dev Tools with a thin Qt adapter
- Moved Dev Tools log capture into a runtime-side log inspector so the console now listens through a thin Qt adapter instead of owning the logging handler
- Narrowed `PluginContext` by removing the leaked `ctx.config` store shuttle; scoped loaders now own config access directly
- Reshaped `App` into grouped `host` and `runtime` services so boot code and UI stop depending on one flat bag of registries
- Split runtime inspection away from direct Qt and `tinywidgets` imports; QObject inspection now lives in the Qt adapter and the field reader is supplied by the composition root
- Added a session-owned provider control service so widget settings no longer drive demo mode and provider tuning by reaching directly into provider objects
- Split the heavy boot flow out of `app/main.py` into bootstrap helpers so the entry point is back to being a thin composition handoff
- Trimmed the `tinycore` root exports to a small public entry surface and moved callers to clearer domain imports
- Marked weak-domain surfaces in code with redesign TODOs so editor schemas and the ceremonial event bus stay visible for later relocation/removal
- Moved editor declarations out of `tinycore` into a shared UI schema package so core no longer owns editor presentation contracts
- Split `SettingsSpec` from `SettingsRegistry` so declarative settings contracts now live in the shared UI schema package while persistence stays in `tinycore`
- Narrowed `PluginContext` further by wrapping editor registration in a scoped adapter and removing the dead subprocess widget-registration path
- Renamed the subprocess consumer descriptor to `ConsumerRuntimeSpec` and cleaned up stale plugin protocol language to match the new runtime model
- Made consumer `requires` manifest-owned all the way through plugin registration instead of reading them dynamically from plugin objects

#### tinyui
- Reworked Dev Tools: the State tab now uses a source dropdown with collapsible inspection sections, and the Console `DEV` toggle now acts as a true all-categories on/off switch
- Moved Dev Tools into its own feature folders so its QML and viewmodels are separated from the rest of the main window structure
- Reworked widget editing flow so selecting a widget now previews that widget directly and automatically drives demo mode through the selected provider
- Replaced the old overlay action with a checkable `Show Overlay` menu item that fits the rest of the title-bar menu styling
- Dutch comments in `ColorPicker.qml` translated to English

#### tinywidgets
- Widget runners and Dev Tools polling now resolve data through session bindings, with optional widget `capability` fields and a single-binding fallback for current specs
- Replaced widget `source` paths with explicit `field` contracts read through host-side capability adapters; the demo widget now reads `telemetry.car.v1` + `fuel`
- Expanded the first capability field contracts for `telemetry.car.v1` and `telemetry.session.v1`, and added more demo widgets that read through those contracts
- Renamed the session widget field contract from `remaining` to `session_time_left` so UI-facing telemetry fields are more explicit
- Split global overlay visibility and per-widget preview into shared overlay state so the main UI and widget engine now follow the same visibility rules

### Fixed

#### app
- Fixed the packaged Windows build so the executable no longer crashes on startup from relative imports or misses the new runtime packages in the bundle
- Fixed frozen subprocess shutdown so closed plugin pipes no longer cascade into a second stderr crash when the packaged app exits

#### plugins
- Corrected LMU provider game detection so `active_game` now reports the real focused game (`lmu` or `none`) while demo/real source state is tracked separately
- Fixed LMU demo mode so it stops immediately when the last widget releases it instead of lingering after the settings panel closes

#### tinyui
- Fixed the global overlay toggle so it now reliably hides and shows the full overlay while still allowing the selected widget to appear as a preview during editing

#### tinywidgets
- Fixed the widget list enable switch so it no longer opens the settings pane on click and now persists each widget's enabled state correctly
- Fixed widget visibility and flash handling when no game is running so inactive providers no longer leave stale flashing values on screen

### Removed

#### tinycore
- Removed the old plugin-side `ctx.connector` registration surface and the leftover mock-connector widget tooling that no longer had a runtime path
- Removed the temporary provider-priority selection path so capabilities resolve to one explicit provider again
- Removed the old `ConnectorRegistry` path after moving provider ticking and provider lookup onto `SessionRuntime`
- Removed the unused type-keyed `ProviderRegistry` surface from `tinycore`; capability/session runtime is now the only active provider path
- Removed dead leftover surfaces: the empty `tinycore.telemetry` package and the old `tinycore/widget.py` tombstone
- Removed the ceremonial runtime event bus from `App` and `PluginContext`; startup and shutdown now use direct lifecycle flow

#### tinyui
- `tinyui/log.py` re-export shim — all layers import directly from `tinycore.log`

## [0.2.0] — 2026-03-24

The main goal of this release was to get a first widget on screen and figure out what a widget
actually needs end-to-end: telemetry source, threshold coloring, flash effects, persistence,
and a settings panel to control it all at runtime. That foundation is now in place.

A lot of internal structure was cleaned up along the way — the codebase is significantly more
layered than it was in 0.1.0, and adding new widget types or connectors should be straightforward
from here.

**What's next:** global widget settings (font, background, opacity and similar), translating those
into the widget renderer, and adding more effects and customization where it makes sense.

Honest note on Linux: the build runs in CI but the overlay widgets are untested on Linux.
If you're running this on Linux and something doesn't work, please open an issue. 
For now linux stays best effort because it subtracts from the goal of having the whole platform up and running.

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
