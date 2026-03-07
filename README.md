# TinyUi

![Version](https://img.shields.io/badge/version-0.5.0-purple)
![Status](https://img.shields.io/badge/status-work%20in%20progress-orange)
![TinyPedal](https://img.shields.io/badge/TinyPedal-v2.42.0-lightgrey)
![License](https://img.shields.io/badge/license-GPLv3-green)

A modular UI layer for [TinyPedal](https://github.com/TinyPedal/TinyPedal), the open-source racing overlay application.

TinyUi replaces TinyPedal's built-in interface with a separated, customizable UI module. The goal is to decouple the UI from TinyPedal's core so it can be modified independently — different themes, layouts, or workflows without touching TinyPedal itself.

**This project is in early development. Things will break.**

## Current state

- UI module runs as a layer on top of TinyPedal (v2.42.0, pinned as submodule)
- Modular UI components (`ui/components/`)
- Menus split into individual modules (`ui/menus/`)
- Theme system with QSS templates (`themes/`)
- Backend adapter layer auto-generated from manifest
- py2exe build pipeline works

## Installation

1. Download [TinyPedal v2.42.0](https://github.com/TinyPedal/TinyPedal/releases/tag/v2.42.0)
2. Download the latest TinyUi release zip
3. Extract TinyUi into the TinyPedal folder
4. Run `tinyui.exe`

## Uninstall

Delete `tinyui.exe`, `tinyui/`, and `tinyui_lib/` from the TinyPedal folder. TinyPedal continues to work unmodified.

## Testing

### Requirements

- Python 3.10
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

## License

GPLv3 — see [LICENSE](LICENSE).

TinyUi builds on [TinyPedal](https://github.com/TinyPedal/TinyPedal) by s-victor, which is also licensed under GPLv3.
