# Widget System Research

Research based on TinyPedal source code as reference.
Goal: build reusable base widgets instead of writing each widget from scratch.

---

## 1. Widget types in TinyPedal

TinyPedal has **71 widgets** across 5 categories:

| Category | Count | Examples |
|----------|-------|---------|
| Text / Numeric | ~40 | Battery, Engine, Fuel, Tyre Temp/Pressure/Wear, Deltabest, Sectors |
| Status indicator | ~15 | DRS (4 states), Flag (pit/blue/yellow), Push-to-Pass, Virtual Energy |
| Graphic (QPainter) | ~10 | Damage, Friction Circle, Radar, Track Map, Steering Wheel |
| Table / List | ~8 | Standings, Rivals, Relative, Laps & Position |
| Hybrid / Specialised | ~8 | Pit Stop Estimate, Stint History, System Performance |

**Over 60% falls into the first two categories** — those are also the widgets we need first.

---

## 2. Common patterns

### 2.1 Threshold

The most common pattern. A value determines which color to use via a tuple lookup:

```python
# Definition (config-driven):
bar_style = (
    wcfg["bkg_color_normal"],     # index 0 — normal
    wcfg["warning_color_low"],    # index 1 — low
    wcfg["warning_color_high"],   # index 2 — high / critical
)

# In update:
if value < low_threshold:
    color_index = 1
elif value > high_threshold:
    color_index = 2
else:
    color_index = 0

target.bg = bar_style[color_index]
```

Used by: Battery, Fuel, Brake Wear, Tyre Pressure, Engine temps, virtually all numeric widgets.

### 2.2 Flash

Separate helper class `warning_flash` from `_common.py`:

```python
# Init:
warn_flash = warning_flash(
    highlight_duration=0.1,   # how long one "on" phase lasts
    interval=0.3,             # time between blinks
    max_count=3               # number of blinks before staying on
)

# In update loop:
is_warning = value <= threshold
highlighted = warn_flash.send(is_warning)
# highlighted = True → show warning color
```

Used by: Battery, Fuel, Damage.

### 2.3 Change detection

Each widget caches the last value and only repaints when it actually changed:

```python
def update_element(self, target, data):
    if target.last != data:
        target.last = data
        target.text = f"{data:.1f}"
        target.update()  # repaint
```

Critical for overlay performance — without this every frame redraws everything.

### 2.4 Heatmap / color gradient

For temperature widgets (tyres, brakes). Separate `heatmap.py` with gradient tables:

```python
heatmap_styles = load_heatmap_color(heatmap_name="custom", ...)

# In update:
fg_color, bg_color = calc.select_grade(heatmap_style, temperature_value)
```

Color slides smoothly from cold (blue) through optimal (green) to hot (red).

### 2.5 EMA — Exponential Moving Average

For smoothing noisy sensor data (tyre temperatures etc.):

```python
from functools import partial
calc_ema = partial(exp_mov_avg, ema_factor(average_samples))

# In update:
avg_temp = calc_ema(previous_avg, new_reading)
```

Sampling window is configurable in seconds.

### 2.6 Freeze duration

At the start of a new lap some values are still unreliable.
Widgets wait `freeze_duration` seconds before switching to live data:

```python
if 0 <= lap_elapsed_time < freeze_duration:
    displayed_value = last_lap_value
else:
    displayed_value = current_value
```

### 2.7 Multi-state status (enum-based)

For widgets with more than 2 states (not just on/off):

```python
# DRS: 0=not available, 1=available, 2=allowed, 3=activated
drs_style = (
    wcfg["bkg_color_not_available"],
    wcfg["bkg_color_available"],
    wcfg["bkg_color_allowed"],
    wcfg["bkg_color_activated"],
)
target.bg = drs_style[drs_state]
```

---

## 3. Base widget types — proposal

Based on the patterns above, **5 base types** cover ~95% of all widgets:

### Type 1 — `TextWidget`
Most basic. Displays text with a fixed style.
- Text with padding and alignment
- Foreground + background color
- Change detection built in

### Type 2 — `ThresholdWidget`
Builds on TextWidget. Color changes based on value vs. threshold breakpoints.
- Configurable thresholds (low, high, critical)
- Tuple-based color lookup
- Optional: flash on warning
- Optional: heatmap gradient (for temperatures)

### Type 3 — `ProgressBarWidget`
Visual bar with optional text.
- Input value → bar width (0–100%)
- Optional: Min/Max markers
- Optional: threshold color on the bar
- Horizontal / Vertical

### Type 4 — `StatusWidget`
Enum-state display. Both color and text change per state.
- Multi-state tuple-based colors and labels
- Flash support for warning states
- Optional: duration tracking (how long in a state)

### Type 5 — `PainterWidget`
Free QPainter/Canvas rendering for complex visualisations.
- Abstract paint method
- No standard layout
- Reserved for: damage diagram, friction circle, radar

---

## 4. Gap analysis — TinyUi vs. TinyPedal

### 4.1 What TinyUi already has ✓

| Component | Status | Location |
|-----------|--------|---------|
| Plugin system (register/start/stop) | ✓ done | `tinycore/plugin/` |
| TelemetryReader ABC (11 sub-readers) | ✓ done | `tinycore/telemetry/reader.py` |
| LMU Connector | ✓ done | `plugins/demo/connector/lmu.py` |
| ConfigStore (pub/sub) | ✓ done | `tinycore/config/store.py` |
| EventBus | ✓ done | `tinycore/events/bus.py` |
| SettingsSpec (bool/int/float/color/enum) | ✓ done | `tinycore/settings.py` |
| QML host window | ✓ done | `tinyui/qml/main.qml` |

### 4.2 What is missing — the gaps ✗

#### Gap 1 — No widget renderer
`WidgetSpec` describes a widget (id, title, description) but **nothing actually renders it**. No overlay, no QML widget canvas, no instantiation logic.

> TinyPedal: each `Realtime(Overlay)` class draws itself via `timerEvent()` + `RawText`/`ProgressBar` components.
> TinyUi: widget spec exists, but nothing renders it.

#### Gap 2 — No standardised data flow to widgets
`TyreDemoViewModel` fetches data directly via a hardcoded `LMUConnector` instance. There is no general mechanism for a widget to declare *"I want `tyre.surface_temperature()` for wheel FL"* and receive it automatically.

```
Desired:
    Widget declaration → data binding → ConnectorRegistry → TelemetryReader

Current:
    TyreDemoViewModel → hardcoded new LMUConnector() → direct call
```

#### Gap 3 — No central timer / update system
TinyPedal has one coordinated `timerEvent()` per widget at a configurable interval.
TinyUi has one `QTimer` per ViewModel — ad-hoc, does not scale to dozens of widgets.

> Needed: a `PollLoop` that polls the connector once per frame and ticks all active runners.

#### Gap 4 — No per-widget configuration
TinyPedal widgets have rich config: position, color per element, thresholds, formats, decimal places, etc.
TinyUi `SettingsSpec` is designed for plugin-level settings (via the settings dialog), not per-widget visual config.

> Needed: widget config system — TOML definition of what options a widget has (thresholds, colors, decimals), JSON storage per widget instance.

#### Gap 5 — No widget position / layout storage
Widgets need to be somewhere on screen. Nothing tracks where a widget is, how large it is, or whether it is visible.

> Needed: per-widget position/size/visibility stored in user config (e.g. `data/widget-config/{plugin}/{widget_id}.json`).

#### Gap 6 — QML has no knowledge of widgets
`CoreViewModel` exposes `widgets` as a list of specs to QML but QML does nothing with it. No QML component renders a widget, no overlay layer, no dynamic loading of widget QML files.

> Needed: a QML `WidgetOverlay` that creates a `Loader` per active widget and loads the correct QML component. Widget QML lives in `tinywidgets/qml/`, not in `tinyui`.

---

## 5. Build order

To get widget rendering working the gaps should be closed in this order:

```
1. tinywidgets package (Gaps 1, 2, 4, 6)
   → WidgetSpec, paths resolver, threshold/flash helpers, ValueWidgetRunner
   → ValueWidget.qml lives inside tinywidgets

2. PollLoop in tinycore (Gap 3)
   → Tickable protocol + PollLoop
   → One connector poll per frame, ticks all registered runners

3. Widget config + position storage (Gaps 4, 5)
   → widgets.toml extended with source/format/thresholds
   → data/widget-config/{plugin}/{widget_id}.json for user overrides + position

4. Wire into tinyui (Gap 6)
   → ViewModel reads state store, emits signals to QML
   → QML overlay loads ValueWidget.qml from tinywidgets
```

---

## 6. Reference — TinyPedal key files

| File | Purpose |
|------|---------|
| `tinypedal/widget/_base.py` | `Overlay` base class (font, layout, rawtext helpers) |
| `tinypedal/widget/_painter.py` | `RawText`, `ProgressBar`, `PedalInputBar` rendering components |
| `tinypedal/widget/_common.py` | `warning_flash`, `FontMetrics` utilities |
| `tinypedal/userfile/heatmap.py` | Heatmap gradient tables + selector |
| `tinypedal/calculation.py` | `exp_mov_avg`, `ema_factor`, `select_grade` |
| `tinypedal/widget/battery.py` | Example: threshold + flash |
| `tinypedal/widget/brake_temperature.py` | Example: heatmap + EMA |
| `tinypedal/widget/flag.py` | Example: multi-state + timer helpers |
