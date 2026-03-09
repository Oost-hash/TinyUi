#
#  TinyUi - Heatmap Editor Service
#  Copyright (C) 2026 Oost-hash
#

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..core.editor_service import EditorService


@dataclass
class HeatmapPreset:
    """Domain model for a heatmap preset (temperature -> color mapping)."""

    name: str
    entries: Dict[float, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, str]:
        """Convert to raw dict with string keys for persistence."""
        return {f"{temp:.1f}": color for temp, color in self.entries.items()}

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, str]) -> "HeatmapPreset":
        """Create from raw dict (string keys -> float keys)."""
        entries = {}
        for temp_str, color in data.items():
            try:
                temp = float(temp_str)
                entries[temp] = color
            except ValueError:
                continue  # Skip invalid entries
        return cls(name=name, entries=entries)

    def sorted_temps(self) -> List[float]:
        """Return sorted list of temperatures."""
        return sorted(self.entries.keys())

    def copy(self) -> "HeatmapPreset":
        """Deep copy of this preset."""
        return HeatmapPreset(name=self.name, entries=dict(self.entries))


class HeatmapService(EditorService[HeatmapPreset]):
    """
    Service for heatmap editor.
    Handles persistence and default loading for reset functionality.
    """

    def __init__(self, store_adapter: Any):
        super().__init__(store_adapter, schema=None)
        self._cfg_attr = "heatmap"
        self._cfg_type = None  # Lazy loaded
        self._defaults: Dict[str, HeatmapPreset] = {}

    @property
    def cfg_type(self):
        if self._cfg_type is None:
            from tinyui.backend.constants import ConfigType

            self._cfg_type = ConfigType.HEATMAP
        return self._cfg_type

    def load(self) -> Dict[str, HeatmapPreset]:
        """Load all heatmap presets."""
        self.load_started.emit()

        try:
            raw_data = self._store.load(self._cfg_attr)
            presets = {
                name: HeatmapPreset.from_dict(name, data)
                for name, data in raw_data.items()
            }
            self._cache = presets
            self.load_completed.emit(presets)
            return presets

        except Exception as e:
            self.load_failed.emit(str(e))
            return {}

    def save(self, data: Dict[str, HeatmapPreset]) -> bool:
        """Validate and save heatmap presets."""
        self.save_started.emit()

        # Validate
        is_valid, error = self.validate(data)
        if not is_valid:
            self.save_failed.emit(error)
            return False

        # Transform to raw dict
        raw_data = {name: preset.to_dict() for name, preset in data.items()}

        # Persist
        try:
            self._store.save(self._cfg_attr, self.cfg_type, raw_data)
            self.save_completed.emit()
            return True

        except Exception as e:
            self.save_failed.emit(str(e))
            return False

    def validate(self, data: Dict[str, HeatmapPreset]) -> tuple[bool, Optional[str]]:
        """Validate heatmap presets."""
        for name, preset in data.items():
            if not name:
                return False, "Preset name cannot be empty"
            # Check for duplicate temperatures within a preset
            seen_temps = set()
            for temp in preset.entries.keys():
                if temp in seen_temps:
                    return False, f"{name}: duplicate temperature {temp}"
                seen_temps.add(temp)
        return True, None

    def load_defaults(self) -> Dict[str, HeatmapPreset]:
        """Load default presets for reset functionality."""
        try:
            raw_defaults = self._store.load_default(self._cfg_attr)
            self._defaults = {
                name: HeatmapPreset.from_dict(name, data)
                for name, data in raw_defaults.items()
            }
            return self._defaults
        except Exception:
            return {}

    def get_default(self, name: str) -> Optional[HeatmapPreset]:
        """Get default preset by name."""
        if not self._defaults:
            self.load_defaults()
        return self._defaults.get(name)

    def is_builtin(self, name: str) -> bool:
        """Check if preset is a built-in default."""
        if not self._defaults:
            self.load_defaults()
        return name in self._defaults

    def create_preset(
        self, name: str, entries: Optional[Dict[float, str]] = None
    ) -> HeatmapPreset:
        """Create new preset with optional initial entries."""
        return HeatmapPreset(
            name=name, entries=entries.copy() if entries else {0.0: "#FFFFFF"}
        )
