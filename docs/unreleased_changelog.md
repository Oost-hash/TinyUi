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
- [plugins] LMU connector logs game state transitions with full session context: session type, track, driver, car, class, car count, track temperature, ambient temperature, and game version
- [tinycore] Log output to terminal and Dev Tools console can now be controlled independently — set `console_level = "INFO"` (or `"DEBUG"`, `"WARNING"`) in `[tool.tinyui.debug]` to attach a terminal handler at that level; omit the key to suppress terminal output entirely
- [tinycore] Debug categories can be toggled at runtime from Dev Tools without restarting; `ALL_CATEGORIES` constant lists all available channels
- [tinyui] Dev Tools State tab now has a source selector — choose a widget context or connector to inspect; widget context properties are read live via QMetaObject introspection
- [tinyui][changed] Dutch comments in `ColorPicker.qml` translated to English
- [tinyui][removed] `tinyui/log.py` re-export shim — all layers import directly from `tinycore.log`
