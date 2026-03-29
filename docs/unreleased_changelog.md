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
- [0.4.1][tinyui][tinydevtools][tinywidgets] Migrated all QML types from setContextProperty to @QmlElement + qmlRegisterSingletonInstance — eliminates unqualified qmllint warnings and enables static QML analysis
- [0.4.1][tinyui][tinydevtools] Added pragma ComponentBehavior: Bound to all QML files — delegates now use required properties and qualified id access
- [0.4.1][tinydevtools] Split DevToolsWindow into DevToolsStateTab, DevToolsRuntimeTab, and ConsolePane components — ConsoleWindow reuses ConsolePane
- [0.4.1][tinyui] Fixed all remaining pragma ComponentBehavior: Bound warnings in SettingsDialog — delegates use ListView.view.dialog and settingRow._dlg to propagate context
- [0.4.1][tinyui][tinydevtools][tinywidgets] QML lint metadata now regenerates into .qml_linter, WindowController type registration no longer conflicts, and Zed qmlls points at the same generated import path
- [0.4.1][tinyui][tinydevtools][other] Fixed remaining static-analysis issues in SettingsDialog and DevTools color bindings, and aligned Zed with the project's venv-based basedpyright and qmlls configs
- [0.4.1][tinyui][other] Added compact diagnostics summary and inspect tasks for Zed, and updated qmllint module imports so QML and basedpyright output stay aligned and less verbose
- [0.4.2][tinycore][tinyui][other] Introduced shared tinyqt ownership for Qt bootstrap, timers, and windowing so tinycore is Qt-free and UI packages consume one shared Qt host layer
- [0.4.2][tinyui][other] Moved shared Qt host composition into tinyqt helpers for app setup, root-window loading, lifecycle wiring, and singleton registration so tinyui.main focuses more on UI assembly
- [0.4.2][tinyui][other] Moved the shared Qt launch and bootstrap flow into tinyqt so tinyui now contributes a launch spec and host assembly instead of owning the runtime host path
- [0.4.2][tinyui][other] Removed the remaining TinyUI host modules by moving TinyUI host settings, host assembly, and launch-spec composition into tinyqt so tinyui is reduced to UI features and presentation code
- [0.4.2][tinyui][tinydevtools][other] Rebuilt the shared shell around TinyQt chrome, restored a launch-first TinyUI widget editor baseline, and aligned devtools to reuse the same titlebar/tab shell instead of owning separate chrome
- [0.4.2][tinyui][tinydevtools][other] Added TinyQt manifest contracts for hosted app surfaces so TinyUI and TinyDevTools declare shared shell usage, panels, and required singleton seams through one host API
- [0.4.2][tinyui][tinydevtools][other] Moved devtools opening to a lazy TinyQt-hosted tool window and pushed shell state through host-owned window properties so the main app and tool surfaces follow the same window contract
