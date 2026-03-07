# Changelog

## Version 0.5.0 (2026-03-07)

### Changed
- Extracted tray icon to self-contained ui/tray.py component (TrayIcon)
- Simplified main.py run(): replaced inline tray setup with TrayIcon class
- MainWindow no longer builds or configures the tray icon
- Extracted StatusButtonBar from app.py to ui/status_bar.py
- Moved theme styling from ui/__init__.py to tinyui/themes/ package
    - QSS template in window.qss with $placeholder substitution
    - Palette and stylesheet logic in themes/style.py
    - ui/__init__.py now only contains UIScaler
- Extracted TabView from app.py to ui/tab_view.py
- Renamed notification.py to notify_bar.py
- Split menu.py (~730 lines) into ui/menus/ package
    - Individual files: overlay, api, config, tools, window, help
    - Shared commands in _commands.py
- Deleted app.py (dead AppWindow class) and menu.py
- Moved UI components (tray, status bar, tab view, notify bar) to ui/components/

### Fixed
- generate_adapters.py no longer deletes hand-written files (e.g. core_loader.py)
- Deferred UI imports in main.py to after QApplication init
- generate_adapters.py skips writing unchanged files, preserving __pycache__
- Fixed status bar CSS selectors (AppWindow → MainWindow)

### Note
This preview release has been made to check if the CI/CD pipeline is working.
If people would like, they could test it. It does not change much yet on the
foreground, but that is to be expected halfway in the process of reworking the code.

### Todo
- Separate rest of UI code into components

## Version 0.4.0 (2026-03-06)

### Changed
- Updated icon to better differentiate between TinyPedal and TinyUi
    - Changed color to #9753ff
    - Updated metadata in compliance with CC BY-SA 4.0
    - Added CC BY-SA 4.0 license in images folder
- Refactored main, _common, _option, app, about, config, log_info, menu and
  notification to use new adapter layer
- Rewired all formatter, validator, regex imports to use backend adapters
- Rewired all setting imports (~22 files) to use backend adapters
- Rewired all control imports (api, mctrl, wctrl, octrl, kctrl, app_signal,
  loader) to use backend adapters
- Rewired all userfile and template imports to use backend adapters
- Rewired all remaining tinypedal imports (calculation, units, module_info,
  hotkey, async_request, realtime_state, log_handler, main, update) to
  use backend adapters
- TinyUi now uses its own icon for window and tray
- Restructured main.py: pure bootstrap (config, logging, Qt, PID, tray)
- Extracted MainWindow to ui/main_window.py
- Moved core_loader.py to backend/
- Moved tray icon setup from MainWindow to main.py
- Backend adapter layer now auto-generated from manifest.json
    - Delete and regenerate adapter files on every run.py execution
    - Supports aliasing (e.g., APP_NAME as TP_APP_NAME)
    - No manual file editing needed when TinyPedal structure changes

### Added
- Backend adapter layer for constants to keep code changes minimal when
  TinyPedal updates or changes
- Backend adapters for formatter, validator, and regex
- Backend adapter for settings (cfg, copy_setting, load/save JSON)
- Backend adapter for controls (api, mctrl, wctrl, octrl, kctrl,
  app_signal, loader, ModuleControl)
- Backend adapter for data (userfile functions, templates, driver stats,
  heatmaps, track notes, track map, shortcuts)
- Backend adapter for misc (calculation, units, module_info, hotkey,
  async_request, realtime_state, log_handler, update)
- Exported TinyUi icon as PNG and ICO from SVG source
- Non-invasive drop-in build: uses separate tinyui_lib/ to avoid overwriting
  TinyPedal's lib/. Uninstall by removing tinyui.exe, tinyui_lib/ and tinyui/
- manifest.json: single source of truth for all TinyPedal imports
- generate_adapters.py: code generator for backend adapter layer
    - Preserves __init__.py, generate_adapters.py, manifest.json
    - Generates 8 adapter files (constants, controls, data, formatter,
      misc, regex, settings, validator)
- build_release.py runs adapter generator before freeze, excludes
  generate_adapters.py and manifest.json from production builds

## Version 0.3.0 (2026-03-06)

### Changed
- Reorganized tinyui/ui/ into subdirectories: editors/, viewers/, dialogs/, views/
- Updated all internal imports to match new directory structure

### Added
- Table helper functions in _common.py: setup_table, editor_button_bar, combo_selector
- TableEditor base class with shared sort/delete/save flow
- Declarative TAB_DEFS and MENU_DEFS lists in app.py
- Config form builder: dispatch table replaces if/elif chain in UserConfig
- Removed duplicate code from editors by using shared helpers
- Auto-discover tinyui modules in build_release.py
- PySide version auto-detection in build script
- Minimal drop-in build mode for existing TinyPedal installs
- Frozen theme path resolution for py2exe builds

## Version 0.2.0 (2026-03-06)

### Added
- Initial release
- Separated run.py into main.py and core_loader.py
- GitHub Actions CI/CD pipeline
- Theme colors loaded from JSON files (tinyui/themes/dark.json, light.json)
- build_release.py for py2exe builds

### Changed
- run.py now chdir's to tinypedal/ so data folders stay in the submodule
- Removed hardcoded palette functions in favor of JSON theme loading

### Fixed
- Data folders (settings/, brandlogo/, etc.) no longer pollute the project root

## Version 0.1.0 (2026-03-05)

### Added
- Proof of concept
- Basic UI replacement
