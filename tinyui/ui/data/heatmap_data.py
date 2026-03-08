"""Heatmap data operations - pure functions, no Qt."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from tinyui.backend.constants import ConfigType
from tinyui.backend.settings import cfg, copy_setting


@dataclass
class HeatmapEntry:
    temperature: float
    color: str


# Validatie functies (kunnen ook naar core/validators.py)
def validate_preset_name(name: str, existing_names: List[str]) -> Tuple[bool, str]:
    """Validate new heatmap preset name."""
    if not name or not name.strip():
        return False, "Name cannot be empty"
    if name in existing_names:
        return False, f"Preset '{name}' already exists"
    if len(name) > 40:
        return False, "Name too long (max 40 characters)"
    # Regex check voor invalid chars
    if not all(c.isalnum() or c in " _-" for c in name):
        return False, "Invalid characters (only alphanumeric, space, -, _)"
    return True, ""


def validate_temperature(value: float) -> Tuple[bool, str]:
    """Validate temperature value."""
    if value < -273.15:
        return False, "Temperature below absolute zero"
    if value > 10000:
        return False, "Temperature unrealistically high"
    return True, ""


def validate_color(value: str) -> Tuple[bool, str]:
    """Validate hex color format."""
    if not value.startswith("#"):
        return False, "Color must start with #"
    if len(value) not in (7, 9):  # #RRGGBB of #RRGGBBAA
        return False, "Invalid color length"
    try:
        int(value[1:], 16)
    except ValueError:
        return False, "Invalid hex color"
    return True, ""


# Data transformatie functies
def load_heatmaps() -> Dict[str, Dict[str, str]]:
    """Load all heatmap presets from user config."""
    return copy_setting(cfg.user.heatmap)


def get_default_heatmap(name: str) -> Optional[Dict[str, str]]:
    """Get default heatmap config if exists."""
    return cfg.default.heatmap.get(name)


def is_builtin_preset(name: str) -> bool:
    """Check if preset is built-in (cannot delete)."""
    return name in cfg.default.heatmap


def sort_entries(entries: Dict[str, str]) -> List[HeatmapEntry]:
    """Sort heatmap entries by temperature ascending."""
    sorted_items = sorted(entries.items(), key=lambda x: float(x[0]))
    return [HeatmapEntry(float(temp), color) for temp, color in sorted_items]


def apply_offset(
    entries: List[HeatmapEntry],
    selected_indices: List[int],
    offset: float,
    is_scale: bool = False,
) -> List[HeatmapEntry]:
    """Apply offset to selected temperature entries."""
    result = []
    for i, entry in enumerate(entries):
        if i in selected_indices:
            if is_scale:
                new_temp = entry.temperature * offset
            else:
                new_temp = entry.temperature + offset
            result.append(HeatmapEntry(new_temp, entry.color))
        else:
            result.append(entry)
    return result


def create_preset(
    heatmaps: Dict[str, Dict[str, str]], name: str, copy_from: Optional[str] = None
) -> Tuple[Dict[str, Dict[str, str]], Optional[str]]:
    """Create new preset, optionally copying from existing."""
    error = validate_preset_name(name, list(heatmaps.keys()))
    if not error[0]:
        return heatmaps, error[1]

    new_heatmaps = dict(heatmaps)  # copy

    if copy_from and copy_from in heatmaps:
        new_heatmaps[name] = copy_setting(heatmaps[copy_from])
    else:
        # Default new preset
        new_heatmaps[name] = {"-273.0": "#4444FF"}

    return new_heatmaps, None


def delete_preset(
    heatmaps: Dict[str, Dict[str, str]], name: str
) -> Tuple[Dict[str, Dict[str, str]], Optional[str]]:
    """Delete preset if not built-in."""
    if is_builtin_preset(name):
        return heatmaps, "Cannot delete built-in preset"

    new_heatmaps = {k: v for k, v in heatmaps.items() if k != name}
    return new_heatmaps, None


def reset_preset(
    heatmaps: Dict[str, Dict[str, str]], name: str
) -> Tuple[Dict[str, Dict[str, str]], Optional[str]]:
    """Reset preset to default."""
    default = get_default_heatmap(name)
    if default is None:
        return heatmaps, "No default preset found"

    new_heatmaps = dict(heatmaps)
    new_heatmaps[name] = copy_setting(default)
    return new_heatmaps, None


def table_to_entries(table_data: List[Tuple[float, str]]) -> Dict[str, str]:
    """Convert table rows to heatmap dict format."""
    return {f"{temp:.1f}": color for temp, color in table_data}


def entries_to_table(entries: Dict[str, str]) -> List[HeatmapEntry]:
    """Convert heatmap dict to sorted table format."""
    return sort_entries(entries)


# Persistence
def save_heatmaps(heatmaps: Dict[str, Dict[str, str]]) -> None:
    """Persist all heatmaps to disk."""
    cfg.user.heatmap = copy_setting(heatmaps)
    cfg.save(0, cfg_type=ConfigType.HEATMAP)

    # Wacht op save completion (blocking, maar snel)
    import time

    while cfg.is_saving:
        time.sleep(0.01)
