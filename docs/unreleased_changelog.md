# Unreleased

Add changes here before releasing. Use the correct section for each change.
Run `python scripts/release.py patch|minor|major` to create a release.

### major
<!-- Breaking changes -->

### minor
<!-- New features -->
- Introduced `tinywidgets` package — widget infrastructure moved out of `tinycore` into its own self-contained layer
- Introduced `tinycore/qt/` — shared Qt bootstrap (`create_application`, `create_engine`, `PollLoop`) used by both `tinyui` and `tinywidgets`
- Introduced `tinycore/poll/` — `Tickable` protocol, pure Python, no Qt dependency
- Introduced `src/app/` composition root — single place that knows all layers; entry point changed to `app.main:main`
- `tinyui.main` refactored into `launch(core, lifecycle)` — receives a fully booted core instead of owning the boot sequence
- `WidgetRegistry` and `WidgetSpec` removed from `tinycore` and `PluginContext`
- Removed `plugins/demo2` and `plugins/tinypedal` — no longer needed
- Removed `TyreDemoViewModel` — connector lifecycle will be managed by the plugin system

### patch
<!-- Bug fixes and small improvements -->
- Editor buttons in the status bar now open the settings panel instead of logging to console
- Title bar left zone now syncs when the dropdown menu opens, preventing drag zone overlap with menu items
- Menu dismiss area now covers the tab bar so switching tabs while a menu is open works correctly
