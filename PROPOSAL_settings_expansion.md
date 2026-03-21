# Proposal: TinyUI Settings Expansion

## Aanleiding

TinyPedal organiseert settings in typed dataclasses per categorie
(`ApplicationConfig`, `CompatibilityConfig`, etc.). We nemen dat patroon over
door een `section` veld aan `SettingsSpec` toe te voegen en `TinyUIPlugin` uit
te breiden met zinvolle instellingen.

---

## 1. Wijziging `SettingsSpec` — `section` veld

```python
@dataclass
class SettingsSpec:
    key:         str
    label:       str
    type:        str        # "bool" | "enum" | "int" | "str"
    default:     Any
    description: str        = ""
    options:     list[str]  = field(default_factory=list)
    section:     str        = ""   # NIEUW — groepering in de settings dialog
```

Sectie is optioneel. Settings zonder sectie komen onder een anoniem blok.

---

## 2. TinyUI settings per sectie

### Application
| key        | type | default | opties         | beschrijving                      |
|------------|------|---------|----------------|-----------------------------------|
| `theme`    | enum | `dark`  | dark / light   | Kleurthema van de applicatie      |
| `language` | enum | `en`    | en / nl        | Interfacetaal (toekomstig)        |

### Window
| key                 | type | default | beschrijving                              |
|---------------------|------|---------|-------------------------------------------|
| `remember_position` | bool | `true`  | Herstelt vensterpositie bij opstarten     |
| `remember_size`     | bool | `true`  | Herstelt venstergrootte bij opstarten     |

> Interne waarden `_position_x`, `_position_y`, `_window_width`,
> `_window_height` worden opgeslagen in dezelfde `settings.json` maar hebben
> geen `SettingsSpec` (niet zichtbaar in de dialog).

---

## 3. Implementatie `remember_position` / `remember_size`

**Bij opstarten** (na `engine.load()`):
```python
if core.settings.get_value("TinyUI", "remember_position"):
    x = core.settings.get_value("TinyUI", "_position_x")
    y = core.settings.get_value("TinyUI", "_position_y")
    if x is not None and y is not None:
        window.setX(x); window.setY(y)

if core.settings.get_value("TinyUI", "remember_size"):
    w = core.settings.get_value("TinyUI", "_window_width")
    h = core.settings.get_value("TinyUI", "_window_height")
    if w is not None and h is not None:
        window.setWidth(w); window.setHeight(h)
```

**Bij afsluiten** (`app.aboutToQuit`):
```python
if core.settings.get_value("TinyUI", "remember_position"):
    core.settings.set_value("TinyUI", "_position_x", window.x())
    core.settings.set_value("TinyUI", "_position_y", window.y())

if core.settings.get_value("TinyUI", "remember_size"):
    core.settings.set_value("TinyUI", "_window_width",  window.width())
    core.settings.set_value("TinyUI", "_window_height", window.height())

core.settings.save("TinyUI")
```

---

## 4. Settings dialog — secties + int stepper

`SettingsPanel.qml` groepeert settings per sectie binnen elk plugin-blok.

**Weergave per type:**
- `bool`  → toggle (bestaand)
- `enum`  → pijltjes-selector (bestaand)
- `int`   → NIEUW: inline stepper `[ − | 10 | + ]`

**Structuur in `settingsByPlugin`** (CoreViewModel):
```json
[
  {
    "plugin": "TinyUI",
    "settings": [
      { "key": "theme", "section": "Application", ... },
      { "key": "language", "section": "Application", ... },
      { "key": "remember_position", "section": "Window", ... },
      { "key": "remember_size", "section": "Window", ... },
    ]
  }
]
```

Groepering op sectie gebeurt in QML via een JS-functie in de delegate.

---

## 5. Bestanden die wijzigen

| Bestand                                          | Wijziging                                      |
|--------------------------------------------------|------------------------------------------------|
| `tinycore/settings.py`                           | `section` veld aan `SettingsSpec`              |
| `tinyui_qml/plugin.py`                           | Nieuwe settings met secties                    |
| `tinyui_qml/viewmodels/core_viewmodel.py`        | `section` meesturen in settings dict           |
| `tinyui_qml/qml/layout/SettingsPanel.qml`        | Sectikoppen + int stepper                      |
| `tinyui_qml/main.py`                             | Window state restore + save on quit            |

---

## Openstaande vragen

1. **`language`** — ✅ als placeholder toevoegen, nog geen implementatie.
2. **`int` type** — geen int settings meer voor TinyUI zelf; `min`/`max` velden op `SettingsSpec` uitstellen tot een plugin het nodig heeft.
