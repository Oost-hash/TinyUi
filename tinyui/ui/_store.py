"""Centralized data store.

Single point for all config load/save/reload operations.
UI components never touch cfg/mctrl/wctrl/kctrl directly.
"""

from __future__ import annotations

import time

from tinyui.backend.settings import cfg, copy_setting


# ---------------------------------------------------------------------------
# Load operations (read-only, return copies)
# ---------------------------------------------------------------------------

def load(cfg_attr: str):
    """Load a copy of user config data (brakes, compounds, heatmap, etc.)."""
    return copy_setting(getattr(cfg.user, cfg_attr))


def load_default(cfg_attr: str):
    """Load a copy of default config data."""
    return copy_setting(getattr(cfg.default, cfg_attr))


# ---------------------------------------------------------------------------
# Save operations (write + persist + side effects)
# ---------------------------------------------------------------------------

def save(cfg_attr: str, cfg_type, data, *, reload: bool = True):
    """Save dict data to a config attribute.

    Used by dict-based editors (brakes, compounds, heatmap, etc.).
    """
    setattr(cfg.user, cfg_attr, copy_setting(data))
    persist(cfg_type)
    if reload:
        reload_modules()


def save_value(section, key: str, value, cfg_type, *, reload: bool = False):
    """Set a single value in a config section and save.

    Used by panels and menus for individual settings.
    section: cfg.application, cfg.api, cfg.telemetry, cfg.overlay,
             cfg.user.setting[name], cfg.user.shortcuts[name], etc.
    """
    section[key] = value
    persist(cfg_type)
    if reload:
        reload_modules()


def toggle(section, key: str, cfg_type, *, reload: bool = False):
    """Toggle a boolean config value and save.

    Returns the new value.
    """
    new_value = not section[key]
    save_value(section, key, new_value, cfg_type, reload=reload)
    return new_value


# ---------------------------------------------------------------------------
# Persistence internals
# ---------------------------------------------------------------------------

def persist(cfg_type):
    """Save to disk and wait for completion."""
    cfg.save(0, cfg_type=cfg_type)
    while cfg.is_saving:
        time.sleep(0.01)


# ---------------------------------------------------------------------------
# Reload operations
# ---------------------------------------------------------------------------

def reload_modules(module_name: str = ""):
    """Reload tinypedal modules and widgets."""
    from tinyui.backend.controls import mctrl, wctrl
    if module_name:
        mctrl.reload(module_name)
    else:
        mctrl.reload()
        wctrl.reload()


def reload_hotkeys():
    """Reload hotkey bindings."""
    from tinyui.backend.controls import kctrl
    kctrl.reload()


def refresh_ui():
    """Emit UI refresh signal."""
    from tinyui.backend.controls import app_signal
    app_signal.refresh.emit(True)


def reload_preset():
    """Emit preset reload signal."""
    from tinyui.backend.controls import app_signal
    app_signal.reload.emit(True)
