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

- [0.4.1][tinycore] Provider activation is now on_demand — open/close driven by active consumer bindings
- [0.4.1][tinycore] Removed auto-start of first plugin at boot
- [0.4.1][tinycore] Added startup_participant to HostAssembly protocol — host decides which plugin to activate at startup
- [0.4.1][tinycore] plugin.toml now supports display_name field
- [0.4.1][tinyui] Tab bar now registers one tab per consumer plugin using display_name
- [0.4.1][tinyui] Tab selection activates the corresponding plugin
- [0.4.1][tinyui] Added startup_plugin setting (default: demo) — configures which plugin activates at boot
- [0.4.1][plugins] LMU_RF2_Connector returns mode inactive when not opened — widgets show idle state gracefully
- [0.4.1][plugins] Cleaned up shared memory type annotations — removed pyright suppressions, added proper types and attribution
- [0.4.1][tinyui][tinydevtools] Fixed QML warnings — removed unused imports, fixed missing-property on Window casts, corrected layout-positioning (width/height → implicitWidth/implicitHeight)
