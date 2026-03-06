# TinyUi

![Version](https://img.shields.io/badge/version-0.2.0-blue)
![Status](https://img.shields.io/badge/status-work%20in%20progress-orange)
![TinyPedal](https://img.shields.io/badge/TinyPedal-v2.42.0-lightgrey)
![License](https://img.shields.io/badge/license-GPLv3-green)

A modular UI layer for [TinyPedal](https://github.com/TinyPedal/TinyPedal), the open-source racing overlay application.

TinyUi replaces TinyPedal's built-in interface with a separated, customizable UI module. The goal is to decouple the UI from TinyPedal's core so it can be modified independently — different themes, layouts, or workflows without touching TinyPedal itself.

**This project is in early development. Things will break.**

## Current state

- UI module runs as a layer on top of TinyPedal (v2.42.0, pinned as submodule)
- Theme colors are defined in JSON files (`tinyui/themes/`) instead of hardcoded Python
- Main window, tray icon, menu bar, and all config dialogs are functional
- py2exe build pipeline works

## Testing

### Requirements

- Python 3.12+
- PySide2 5.15.x
- psutil

### Setup

```bash
git clone --recurse-submodules https://github.com/Oost-hash/TinyUi.git
cd TinyUi
pip install -r requirements.txt
```

### Run

```bash
python run.py
```

TinyPedal needs a supported sim running (or at least its API accessible) to do anything useful. Without a sim, the app will start but most features won't have data to display.

## Project structure

```
TinyUi/
  run.py              # Entry point
  tinyui/             # UI module
    main.py           # Main window and app startup
    core_loader.py    # TinyPedal core integration
    ui/               # All dialogs, views, menus
    themes/           # JSON theme files (dark.json, light.json)
  tinypedal/          # TinyPedal submodule (pinned to v2.42.0)
```

## License

GPLv3 — see [LICENSE.txt](LICENSE.txt).

TinyUi builds on [TinyPedal](https://github.com/TinyPedal/TinyPedal) by s-victor, which is also licensed under GPLv3.
