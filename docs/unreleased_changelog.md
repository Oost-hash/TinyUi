# Unreleased

Add changes here before releasing. Use the correct section for each change.
Run `python scripts/release.py patch|minor|major` to create a release.

### major
<!-- Breaking changes -->

### minor
<!-- New features -->
- Introduced `tinywidgets` package — self-contained widget system, separated from `tinycore`
- Introduced `tinycore/qt/` — shared Qt bootstrap (`create_application`, `create_engine`, `PollLoop`)
- Introduced `tinycore/poll/` — `Tickable` protocol, pure Python, no Qt dependency
- Introduced `src/app/` composition root — single place that wires all layers together
- Entry point changed from `tinyui.main:main` to `app.main:main`
- `tinyui.main` refactored into `launch(core, lifecycle)` — boot sequence moved to composition root
- `WidgetRegistry` and `WidgetSpec` removed from `tinycore` and `PluginContext`
- Removed `plugins/demo2` and `plugins/tinypedal`
- Removed `TyreDemoViewModel` — connector lifecycle will be managed by the plugin system
- Central logger moved from `tinyui.log` to `tinycore.log` — now shared across all layers
- First working widget: `TextWidget` with live telemetry, threshold colors, flash effect, and drag-to-position
- Each widget is an independent `Qt.Tool` window — transparent background is click-through by default
- Widget windows close automatically when tinyui closes
- Widget settings panel in the Widgets tab — edit label, position, flash target, and thresholds live
- Threshold colors editable via built-in color picker; add and remove thresholds at runtime
- Flash is now configured per threshold entry (with per-entry speed), not as a global widget setting
- Threshold logic: each entry is an upper bound — color applies while value is at or below that number
- `plugin.toml` supports `[mock_connector]` section to declare a test connector per plugin
- `MockConnector` sweep is configurable: min, max, and step settable at runtime
- Demo button in the widget settings header — switches between live and mock connector on the fly

### patch
<!-- Bug fixes and small improvements -->
- Editor buttons in the status bar now open the settings panel instead of logging to console
- Title bar left zone now syncs when the dropdown menu opens, preventing drag zone overlap with menu items
- Menu dismiss area now covers the tab bar so switching tabs while a menu is open works correctly
- Removed `DemoTab` from the UI
- Removed placeholder settings that had no working implementation (`language`, demo overlay settings)
- Window chrome dimensions moved from inline literals to `Theme` constants
- `NumberStepper` and `ThemedComboBox` extracted as shared QML components
- Widget settings panel layout aligned with the SettingsDialog style (same row heights, label/control columns)
