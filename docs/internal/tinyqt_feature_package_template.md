# TinyQt Feature Package Template

## Purpose
Use this layout for first-party hosted feature packages so that:
- ownership stays obvious
- manifests are easy to find
- QML/viewmodels stay predictable
- new surfaces do not invent new local structure without a reason

## Standard Layout
```text
src/<feature_package>/
  __init__.py
  manifest.toml
  qml/
  viewmodels/
```

## Optional Feature Files
Add these only when the feature actually needs them:

```text
  actions.py
  rows.py
  window.py
```

Meaning:
- `actions.py`: feature-owned button/toolbar action maps
- `rows.py`: feature-specific row/editor builders
- `window.py`: feature-owned native window implementation

## Current Examples
- main:
  - [C:\Users\rroet\Documents\TinyUi\src\tinyqt_main](C:\Users\rroet\Documents\TinyUi\src\tinyqt_main)
- settings:
  - [C:\Users\rroet\Documents\TinyUi\src\tinyqt_settings](C:\Users\rroet\Documents\TinyUi\src\tinyqt_settings)
- devtools:
  - [C:\Users\rroet\Documents\TinyUi\src\tinyqt_devtools](C:\Users\rroet\Documents\TinyUi\src\tinyqt_devtools)

## Boundary Rules
- feature package owns:
  - feature manifest
  - feature QML
  - feature viewmodels
  - feature native window/actions/rows if needed
- `tinyqt` owns:
  - orchestration
  - manifest loading
  - launch/bootstrap
  - shared host state wiring
- `tinyqt_native` owns:
  - reusable native primitives only
- `tinyqt_native_qml` owns:
  - shared hosted shell roots only

## Naming Guidance
- prefer:
  - `window.py`
  - `actions.py`
  - `rows.py`
- avoid:
  - one-off names that repeat the package name
  - duplicated concepts such as both `native_feature_window.py` and `window.py`

## When To Deviate
Only deviate from this structure when:
- the feature has a real subdomain split
- the file would otherwise become too large
- the split makes ownership clearer, not just more abstract
