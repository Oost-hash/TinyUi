# Unreleased

Add entries here before running a release.
The release script controls the version bump, category, and grouping.

Running a release:
  python scripts/release.py patch
  python scripts/release.py minor
  python scripts/release.py major

## Format

Use one line per change:
  - [tinycore] New provider registry API
  - [tinyui][fixed] Settings panel not opening from toolbar
  - [tinywidgets][removed] Legacy overlay shim

Tags:
  - no tag = Added
  - [changed]
  - [fixed]
  - [removed]

## Entries

- [plugins][changed] Established the new plugin baseline: `demo` now declares a consumer manifest without bundled connector code, and `lmu_connector` now owns the shared-memory submodules and provider-side connector split
- [tinycore][changed] Reworked plugin manifest parsing around `plugin.consumer` and `plugin.provider`, and updated the app bootstrap to load consumer logic separately from host-side providers
- [tinycore][changed] Added a capability registry that records provider exports, resolves consumer `requires`, and logs missing or successful bindings during app bootstrap
- [tinycore][changed] Introduced a session runtime that owns active providers and per-consumer capability bindings instead of leaving binding state embedded in the registry layer
- [tinywidgets][changed] Widget runners and Dev Tools polling now resolve data through session bindings, with optional widget `capability` fields and a single-binding fallback for current specs
- [tinywidgets][changed] Replaced widget `source` paths with explicit `field` contracts read through host-side capability adapters; the demo widget now reads `telemetry.car.v1` + `fuel`
- [tinywidgets][changed] Expanded the first capability field contracts for `telemetry.car.v1` and `telemetry.session.v1`, and added more demo widgets that read through those contracts
- [tinycore][removed] Removed the old plugin-side `ctx.connector` registration surface and the leftover mock-connector widget tooling that no longer had a runtime path
- [plugins][changed] Folded mock telemetry into the LMU provider family so `lmu_connector` now owns both real and demo sources behind one provider identity
- [tinycore][changed] Added session-level demo-mode passthrough methods so the UI can request provider-owned demo leases without rebinding capabilities
- [tinycore][removed] Removed the temporary provider-priority selection path so capabilities resolve to one explicit provider again
- [tinycore][changed] Moved runtime inspection source and snapshot logic into a new runtime inspector service, leaving Dev Tools with a thin Qt adapter
- [tinycore][changed] Moved Dev Tools log capture into a runtime-side log inspector so the console now listens through a thin Qt adapter instead of owning the logging handler
- [tinycore][removed] Removed the old `ConnectorRegistry` path after moving provider ticking and provider lookup onto `SessionRuntime`
- [tinycore][removed] Removed the unused type-keyed `ProviderRegistry` surface from `tinycore`; capability/session runtime is now the only active provider path
- [tinycore][changed] Narrowed `PluginContext` by removing the leaked `ctx.config` store shuttle; scoped loaders now own config access directly
- [tinycore][changed] Reshaped `App` into grouped `host` and `runtime` services so boot code and UI stop depending on one flat bag of registries
- [tinycore][changed] Split runtime inspection away from direct Qt and `tinywidgets` imports; QObject inspection now lives in the Qt adapter and the field reader is supplied by the composition root
- [plugins][changed] Moved LMU provider inspection snapshots into `lmu_connector` so runtime inspection no longer carries telemetry-specific state field maps in `tinycore`
- [tinycore][changed] Added a session-owned provider control service so widget settings no longer drive demo mode and provider tuning by reaching directly into provider objects
- [plugins][changed] Moved the telemetry reader contract out of `tinycore` and into `lmu_connector`, so provider-side game contracts now live with the plugin that owns them
- [tinycore][changed] Split the heavy boot flow out of `app/main.py` into bootstrap helpers so the entry point is back to being a thin composition handoff
- [tinycore][changed] Trimmed the `tinycore` root exports to a small public entry surface and moved callers to clearer domain imports
- [tinycore][removed] Removed dead leftover surfaces: the empty `tinycore.telemetry` package and the old `tinycore/widget.py` tombstone
- [tinycore][changed] Marked weak-domain surfaces in code with redesign TODOs so editor schemas and the ceremonial event bus stay visible for later relocation/removal
- [tinycore][removed] Removed the ceremonial runtime event bus from `App` and `PluginContext`; startup and shutdown now use direct lifecycle flow
- [tinycore][changed] Moved editor declarations out of `tinycore` into a shared UI schema package so core no longer owns editor presentation contracts
- [tinycore][changed] Split `SettingsSpec` from `SettingsRegistry` so declarative settings contracts now live in the shared UI schema package while persistence stays in `tinycore`
- [tinycore][changed] Narrowed `PluginContext` further by wrapping editor registration in a scoped adapter and removing the dead subprocess widget-registration path
- [tinycore][changed] Renamed the subprocess consumer descriptor to `ConsumerRuntimeSpec` and cleaned up stale plugin protocol language to match the new runtime model
- [tinycore][changed] Made consumer `requires` manifest-owned all the way through plugin registration instead of reading them dynamically from plugin objects
- [tinywidgets][changed] Renamed the session widget field contract from `remaining` to `session_time_left` so UI-facing telemetry fields are more explicit
- [plugins][changed] Renamed several LMU session, lap, and timing API methods to clearer exposed contract names such as `session_time_left`, `session_kind`, `current_lap`, and `gap_to_leader`
- [tinyui][changed] Reworked Dev Tools: the State tab now uses a source dropdown with collapsible inspection sections, and the Console `DEV` toggle now acts as a true all-categories on/off switch
- [tinyui][changed] Moved Dev Tools into its own feature folders so its QML and viewmodels are separated from the rest of the main window structure
- [tinywidgets][fixed] Fixed the widget list enable switch so it no longer opens the settings pane on click and now persists each widget's enabled state correctly
- [plugins] LMU connector logs game state transitions with full session context: session type, track, driver, car, class, car count, track temperature, ambient temperature, and game version
- [tinycore] Log output to terminal and Dev Tools console can now be controlled independently — set `console_level = "INFO"` (or `"DEBUG"`, `"WARNING"`) in `[tool.tinyui.debug]` to attach a terminal handler at that level; omit the key to suppress terminal output entirely
- [tinycore] Debug categories can be toggled at runtime from Dev Tools without restarting; `ALL_CATEGORIES` constant lists all available channels
- [tinyui] Dev Tools State tab now has a source selector — choose a widget context or connector to inspect; widget context properties are read live via QMetaObject introspection
- [tinyui][changed] Dutch comments in `ColorPicker.qml` translated to English
- [tinyui][removed] `tinyui/log.py` re-export shim — all layers import directly from `tinycore.log`
