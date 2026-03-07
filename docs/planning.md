# TinyUi — Component separation roadmap

Work-in-progress plan to break the UI into isolated, reusable components.
Each phase is a single deliverable. Order matters — later phases build on earlier ones.

## ~~Phase 1: Extract shared UI helpers~~ DONE (v0.3.0)

## ~~Phase 2: TableEditor base class~~ DONE (v0.3.0)

## ~~Phase 3: Modular MainWindow assembly~~ DONE (v0.3.0)

## ~~Phase 4: Config form builder~~ DONE (v0.3.0)

## ~~Phase 5: Menu builder~~ SKIPPED

Too much variation (checkable items, dynamic QActionGroups, submenus, tray mode)
for a generic builder to add value. Current code is readable.

## ~~Phase 6: Rework build_release.py~~ DONE (v0.4.0)

- Auto-discover tinyui modules
- PySide version auto-detection
- Non-invasive drop-in build with separate `tinyui_lib/`
- TinyUi own icon for exe, window, and tray

## Phase 7: CI/CD pipeline — DEFERRED

Will be set up when closer to release.

## ~~Phase 8: Decouple from tinypedal backend~~ DONE (v0.4.0)

Currently every file in `tinyui/` imports directly from `tinypedal.*` (~100 imports).
Introduce `tinyui/backend/` as an adapter layer. All tinypedal imports are
centralized there — if TinyPedal changes, only the adapter needs updating.

Sub-phases:

### ~~8a: Constants~~ DONE
Re-export constants via `tinyui/backend/constants.py`. ~27 imports rewired.

### ~~8b: Formatters & validators~~ DONE
Re-export pure functions (`format_option_name`, `strip_invalid_char`,
`is_hex_color`, `regex_pattern`, etc.) via `tinyui/backend/`. ~14 imports rewired.

### ~~8c: Settings interface~~ DONE
Abstract `cfg`, `copy_setting`, `load_setting_json_file`, `save_and_verify_json_file`
behind `tinyui/backend/settings.py`. ~22 imports rewired.

### ~~8d: Control interfaces~~ DONE
Abstract `api`, `mctrl`, `wctrl`, `octrl`, `kctrl`, `app_signal`, `loader`
behind `tinyui/backend/controls.py`. ~20 imports rewired.

### ~~8e: Data & userfile~~ DONE
Abstract userfile functions and templates behind `tinyui/backend/data.py`. ~11 imports rewired.

### ~~8f: Remaining imports~~ DONE
`calculation`, `units`, `module_info`, `hotkey.common`, `async_request`,
`realtime_state`, `log_handler`, `main`, `update`. ~17 imports rewired.
All tinypedal imports now centralized in `tinyui/backend/`.

## ~~Phase 9: Rework main.py and core_loader.py~~ DONE (v0.4.0)

- main.py is now pure bootstrap (config, logging, Qt, PID, tray, entry point)
- Extracted MainWindow to `tinyui/ui/main_window.py`
- Moved `core_loader.py` to `tinyui/backend/core_loader.py`
- Moved tray icon setup from MainWindow to main.py
- All tinypedal imports go through backend adapters

## Phase 10: Non-invasive drop-in architecture — DONE (v0.4.0)

- Separate `tinyui_lib/library.zip` (does not touch TinyPedal's `lib/`)
- TinyUi-specific files live under `tinyui/` subfolder
- TinyPedal continues to work unmodified
- Uninstall by deleting `tinyui.exe`, `tinyui_lib/`, and `tinyui/`

## Phase 11: UI components (v0.5.0)

Goal: every piece of UI is a self-contained component. MainWindow just
assembles them like lego. Each component owns its own signals, layout,
and cfg interactions.

### ~~11a: Tray icon component~~ DONE
Extract tray icon from main.py to `tinyui/ui/tray.py`.
Owns: icon, tooltip, context menu, double-click-to-show, hide-on-quit.
MainWindow receives it, doesn't build it.

### ~~11b: Status bar component~~ DONE
Extract `StatusButtonBar` from app.py to `tinyui/ui/status_bar.py`.
Owns: API button, theme toggle, DPI toggle, refresh logic.

### ~~11b-side: Extract theming to tinyui/themes/~~ DONE
Moved palette loading, QSS generation from `ui/__init__.py` to `tinyui/themes/`.
- `window.qss` — QSS template with `$placeholder` substitution (string.Template)
- `style.py` — `set_style_palette()`, `set_style_window()`, `load_theme()`
- `ui/__init__.py` now only contains `UIScaler`
- Fixed CSS selectors targeting old `AppWindow` class → `MainWindow`

### ~~11c: Tab view component~~ DONE
Extract `TabView` from app.py to `tinyui/ui/tab_view.py`.
Owns: tab definitions, tab creation, notify bar integration.
TAB_DEFS stays with it.

### ~~11d: Notify bar component~~ DONE
Renamed `notification.py` to `notify_bar.py`. Already standalone.

### ~~11e: Menu components~~ DONE
Split menu.py (~730 lines) into `tinyui/ui/menus/`:
`overlay.py`, `api.py`, `config.py`, `tools.py`, `window.py`, `help.py`.
Shared commands in `_commands.py`, re-exports in `__init__.py`.

### ~~11f: Clean up app.py~~ DONE
Deleted `app.py` (only dead `AppWindow` class remained) and `menu.py`.

### 11g: CI/CD pipeline
GitHub Actions: lint, import check, build test.
Defer until components are stable.

---

## Rules

- One phase at a time. Verify it works before starting the next.
- No feature additions — this is pure structural refactoring.
- Every phase must pass: `python run.py` starts, all dialogs open, themes apply.
- If a phase turns out wrong, we revert and rethink before continuing.
- NEVER commit this file (planning.md) — it is a personal planning document.
- No phase numbers in commit messages — describe what changed, not which phase.
