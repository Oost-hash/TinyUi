# Unreleased

Add entries here before running a release.
Version tags control which release an entry belongs to.

## Format

Use one line per change:
  - [0.3.1][tinycore] New provider registry API
  - [0.3.1][tinyui][fixed] Settings panel not opening from toolbar
  - [0.3.1][tinywidgets][removed] Legacy overlay shim
  - [0.3.2][plugins][changed] LMU connector now logs session transitions

Known packages:
  - app
  - plugins
  - tinycore
  - tinyui
  - tinywidgets
  - other

## Entries
- [0.3.2][plugins][changed] Rebuilt the LMU and rF2 connector stack into a single TinyUi-owned `LMU_RF2_Connector` family with shared contracts, source switching, full capability coverage, and no remaining legacy or vendor runtime dependency
- [0.3.2][plugins][changed] Cleaned up the new connector family further by removing transitional raw auto-mapping hints, trimming dead runtime exports, and improving LMU electric and flap decoding so more values now come from real shared-memory fields instead of placeholders
- [0.3.2][tinycore][changed] Extended runtime inspection so providers can expose normalized telemetry, struct-level raw snapshots, and real shared-memory memory dumps from the existing Dev Tools flow for connector discovery and decoding work
- [0.3.2][tinyui][changed] Added `Copy all`, source recording, and capture path copy actions to the state dev tools so full connector snapshots can be collected during live driving sessions for later analysis
- [0.3.1][app][changed] Cleaned up the startup import path to delay heavy UI and Qt loading, reducing a measured bootstrap profiling run from about 1.6s to about 0.48s
- [0.3.1][app][changed] Added built-in startup timing logs across manifest discovery, runtime bootstrap, Qt setup, QML load, and pre-run phases so boot costs are visible without ad-hoc profiling
- [0.3.1][plugins][changed] Added a packaged plugin build flow that outputs `runtime`, `widgets`, `editors`, `config/defaults`, `_internal`, and `manifest.lock`, with stricter manifest validation and direct support for deployable zip artifacts
- [0.3.1][plugins][changed] Packaged plugin manifests now load consumer and provider runtimes from `runtime/*.pkg`, preserve user config files on later syncs, and use explicit `widgets` and `editors` paths in the active packaged layout
- [0.3.1][tinycore][changed] Updated plugin manifest scanning for the packaged `_internal/plugin.toml` layout while keeping plugin paths resolved from the plugin root
- [0.3.1][app][changed] Updated the standalone build to use `_runtime`, package plugins into `dist/TinyUi/plugins`, separate app and plugin build steps, and expose clearer `build.py` CLI modes
- [0.3.1][app][changed] Added an internal packaged demo smoke path to verify packaged plugin discovery, runtime loading, and preserved user files in the new distribution flow
- [0.3.1][other][changed] Split release note rendering out of the mutating release flow and added `preview_release_notes.py` so version-tagged release notes can be reviewed without mutating `unreleased`
- [0.3.1][other][changed] Added project-scoped Zed and basedpyright configuration, then cleaned up the active `src` and `scripts` code paths so the current 0.3.1 scope type-checks cleanly while `lmu_connector` stays parked for the next update
- [0.3.1][tinyui][fixed] Fixed the state dev tool so live heartbeat and change updates keep the state list scroll stable, show the correct empty state, and allow quick copying of `key: value` entries
- [0.3.1][tinyui][changed] Replaced the bundled Linux icon font and legacy image set with dedicated SVG chrome assets for menu and window controls
- [0.3.1][tinyui][changed] Increased the custom title bar and menu chrome icons to a cleaner 16px SVG canvas with lighter strokes for better desktop readability
- [0.3.1][tinyui][removed] Removed the old icon glyph loader and unused chrome image/font assets after moving the title bar to direct SVG icons
