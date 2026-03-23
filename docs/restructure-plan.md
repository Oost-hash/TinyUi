# Restructure Plan

Moving towards a clean layered architecture where each package has one
responsibility and no cross-dependencies exist between tinyui and tinywidgets.

---

## Current state

```
src/
├── tinycore/
│   ├── app.py
│   ├── config/
│   ├── editor.py
│   ├── events/
│   ├── plugin/
│   ├── providers/
│   ├── settings.py
│   ├── telemetry/
│   └── widget.py           ← WidgetSpec/WidgetRegistry lives here (wrong place)
├── plugins/
│   └── demo/
├── tinyui/
│   ├── main.py             ← owns QApplication + QML engine
│   ├── viewmodels/
│   │   └── tyre_demo_viewmodel.py  ← hardcoded LMUConnector instantiation
│   └── qml/
└── (no tinywidgets yet)
```

**Problems:**
- `tinycore/widget.py` — widget concerns in the generic engine
- `tinyui/main.py` — owns QApplication, but tinywidgets will also need Qt
- No shared Qt foundation — tinyui and tinywidgets would both try to own Qt
- `TyreDemoViewModel` hardcodes connector instead of using ConnectorRegistry
- No `tinycore/poll/` — no central tick loop
- No `tinywidgets/` package

---

## Target state

```
src/
├── tinycore/
│   ├── qt/                 # NEW — shared Qt foundation (only Qt code in tinycore)
│   │   ├── __init__.py
│   │   ├── app.py          # QApplication lifecycle
│   │   └── engine.py       # QQmlApplicationEngine factory
│   ├── poll/               # NEW — central tick loop
│   │   ├── __init__.py
│   │   ├── loop.py         # PollLoop (uses QTimer from tinycore.qt)
│   │   └── tickable.py     # Tickable protocol (pure Python)
│   ├── app.py              # unchanged
│   ├── config/             # unchanged
│   ├── editor.py           # unchanged
│   ├── events/             # unchanged
│   ├── plugin/             # unchanged
│   ├── providers/          # unchanged
│   ├── settings.py         # unchanged
│   └── telemetry/          # unchanged
│   # widget.py removed — moves to tinywidgets
│
├── tinywidgets/            # NEW — self-contained widget system
│   ├── __init__.py
│   ├── spec.py             # WidgetSpec, load_widgets_toml
│   ├── registry.py         # WidgetRegistry
│   ├── paths.py            # telemetry path resolver
│   ├── threshold.py        # ThresholdEntry + evaluate()
│   ├── flash.py            # FlashState
│   ├── runner.py           # TextWidgetRunner, WidgetState
│   ├── context.py          # WidgetContext — bridges state_store to QML
│   ├── overlay.py          # transparent overlay window (own QML engine)
│   └── qml/
│       └── TextWidget.qml
│
├── plugins/
│   └── demo/
│       ├── plugin.py       # remove direct LMUConnector instantiation
│       ├── widgets.toml    # extended with source/format/thresholds
│       └── connector/
│           └── lmu.py      # unchanged
│
└── tinyui/
    ├── main.py             # starts QApplication via tinycore.qt, no widget code
    ├── viewmodels/
    │   └── (TyreDemoViewModel removed or cleaned up)
    └── qml/                # only main window QML, no widget QML
```

---

## Import rules (enforced)

| Package | May import from | May NOT import from |
|---------|----------------|---------------------|
| `tinycore` (non-qt) | stdlib only | Qt, tinywidgets, tinyui |
| `tinycore.qt` | PySide6, tinycore | tinywidgets, tinyui |
| `tinywidgets` | tinycore, tinycore.qt, PySide6 | tinyui |
| `tinyui` | tinycore, tinycore.qt, PySide6 | tinywidgets |
| `plugins` | tinycore | tinywidgets, tinyui |

`tinyui` and `tinywidgets` never import each other.

---

## Steps

### Step 1 — Add `tinycore/qt/`
Create the shared Qt foundation. Both tinyui and tinywidgets will use this.

- `app.py` — wraps `QApplication` creation and lifecycle
- `engine.py` — factory for `QQmlApplicationEngine` with common setup

Move QApplication creation out of `tinyui/main.py` into `tinycore.qt.app`.

### Step 2 — Add `tinycore/poll/`
Central tick loop. Pure protocol + QTimer-based loop.

- `tickable.py` — `Tickable` protocol: `tick(connector) -> None`
- `loop.py` — `PollLoop`: registers Tickables, drives them on a QTimer

### Step 3 — Remove `tinycore/widget.py`
`WidgetSpec` and `WidgetRegistry` move to `tinywidgets/spec.py` and
`tinywidgets/registry.py`. Update all imports.

### Step 4 — Create `tinywidgets/`
New package. All widget logic lives here:
- Load `widgets.toml` from plugin directories
- Build `TextWidgetRunner` instances
- Register runners with `PollLoop`
- Own the overlay window and QML engine
- `WidgetContext` subscribes to state_store and exposes properties to QML

### Step 5 — Fix connector registration in demo plugin
`TyreDemoViewModel` currently instantiates `LMUConnector()` directly.
Replace with `ctx.connector.register(LMUConnector())` in `DemoPlugin.register()`.
Remove `TyreDemoViewModel` or reduce it to a tab-level display only.

### Step 6 — Clean up `tinyui/main.py`
- Use `tinycore.qt.app` for QApplication
- Remove any widget-related code
- `tinywidgets` starts itself when activated — tinyui does not manage it

---

## What does NOT change

- Plugin protocol (`register` / `start` / `stop`)
- `PluginContext` and scoped access pattern
- `ConfigStore`, `EventBus`, `SettingsRegistry`
- `TelemetryReader` ABC and `LMUConnector` implementation
- All existing QML in `tinyui/qml/` (titlebar, settings dialog, console, tabs)
- `build.py`, CI workflow, `pyproject.toml`
