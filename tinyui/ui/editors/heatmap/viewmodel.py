#
#  TinyUi - Heatmap Editor ViewModel
#  Copyright (C) 2026 Oost-hash
#

from typing import Any, Dict, List, Optional, Tuple

from PySide2.QtCore import Signal

from ..core.base_viewmodel import BaseViewModel
from .service import HeatmapPreset, HeatmapService


class HeatmapEditorVM(BaseViewModel[HeatmapPreset]):
    """
    ViewModel for heatmap editor.
    Manages two-level state: all presets + selected preset's entries.
    """

    # Heatmap-specific signals
    preset_selected = Signal(str)  # New preset selected
    preset_list_changed = Signal(list)  # List of preset names updated
    entry_added = Signal(float, str)  # temp, color
    entry_removed = Signal(float)  # temp
    entries_sorted = Signal()  # Entries were reordered

    def __init__(self, service: HeatmapService):
        super().__init__(service)
        self._service: HeatmapService = service
        self._selected_preset_name: Optional[str] = None
        self._defaults: Dict[str, HeatmapPreset] = {}

    def load(self) -> bool:
        """Load presets and defaults."""
        success = super().load()
        if success:
            self._defaults = self._service.load_defaults()
            # Auto-select first preset
            if self._model and len(self._model) > 0:
                first_preset = next(iter(self._model.keys()))
                self.select_preset(first_preset)
        return success

    @property
    def selected_preset_name(self) -> Optional[str]:
        """Currently selected preset name."""
        return self._selected_preset_name

    @property
    def selected_preset(self) -> Optional[HeatmapPreset]:
        """Currently selected preset data."""
        if self._model and self._selected_preset_name:
            return self._model.get(self._selected_preset_name)
        return None

    @property
    def preset_names(self) -> List[str]:
        """List of all preset names."""
        return list(self._model.keys()) if self._model else []

    @property
    def is_builtin_preset(self) -> bool:
        """Is selected preset a built-in?"""
        if self._selected_preset_name:
            return self._service.is_builtin(self._selected_preset_name)
        return False

    def select_preset(self, name: str):
        """Switch to different preset."""
        if self._model and name in self._model:
            self._selected_preset_name = name
            self.preset_selected.emit(name)

    def create_preset(self, name: str) -> bool:
        """Create new empty preset."""
        if not self._model or name in self._model:
            self.error_occurred.emit(f"Preset '{name}' already exists")
            return False

        preset = self._service.create_preset(name)
        self.add_item(name, preset)
        self.preset_list_changed.emit(self.preset_names)
        self.select_preset(name)
        return True

    def copy_preset(self, source_name: str, new_name: str) -> bool:
        """Duplicate existing preset."""
        if not self._model or new_name in self._model:
            self.error_occurred.emit(f"Preset '{new_name}' already exists")
            return False

        source = self._model.get(source_name)
        if not source:
            return False

        new_preset = HeatmapPreset(name=new_name, entries=source.entries.copy())
        self.add_item(new_name, new_preset)
        self.preset_list_changed.emit(self.preset_names)
        self.select_preset(new_name)
        return True

    def delete_preset(self, name: str) -> bool:
        """Delete preset (not allowed for built-ins)."""
        if self._service.is_builtin(name):
            self.error_occurred.emit("Cannot delete built-in preset")
            return False

        self.remove_item(name)

        # Update selection
        if self.preset_names:
            new_selection = self.preset_names[0]
            self.select_preset(new_selection)
        else:
            self._selected_preset_name = None

        self.preset_list_changed.emit(self.preset_names)
        return True

    def reset_preset(self, name: str) -> bool:
        """Reset preset to default."""
        default = self._service.get_default(name)
        if not default:
            self.error_occurred.emit("No default available for this preset")
            return False

        if self._model:
            # Replace entries with default copy
            self._model[name] = default.copy()
            self._model._mark_dirty()  # Force dirty
            if name == self._selected_preset_name:
                self.preset_selected.emit(name)
        return True

    # --- Entry CRUD (operates on selected preset) ---

    def add_temperature(
        self, temp: Optional[float] = None, color: str = "#FFFFFF"
    ) -> float:
        """Add new temperature entry to selected preset."""
        preset = self.selected_preset
        if not preset:
            return 0.0

        # Auto-generate temp if not provided
        if temp is None:
            if preset.entries:
                temp = max(preset.entries.keys()) + 10.0
            else:
                temp = 0.0

        # Ensure unique
        while temp in preset.entries:
            temp += 1.0

        preset.entries[temp] = color
        self._model._mark_dirty()
        self.entry_added.emit(temp, color)
        return temp

    def remove_temperatures(self, temps: List[float]):
        """Remove multiple temperatures from selected preset."""
        preset = self.selected_preset
        if not preset:
            return

        for temp in temps:
            if temp in preset.entries:
                del preset.entries[temp]
                self.entry_removed.emit(temp)

        self._model._mark_dirty()

    def update_temperature(
        self, old_temp: float, new_temp: float, new_color: Optional[str] = None
    ):
        """Update temperature value and/or color."""
        preset = self.selected_preset
        if not preset or old_temp not in preset.entries:
            return

        color = new_color if new_color is not None else preset.entries[old_temp]

        # If temp changed, delete old and add new
        if old_temp != new_temp:
            del preset.entries[old_temp]
            # Handle collision
            while new_temp in preset.entries:
                new_temp += 0.1

        preset.entries[new_temp] = color
        self._model._mark_dirty()

        # Notify view to refresh
        self.preset_selected.emit(self._selected_preset_name or "")

    def update_color(self, temp: float, color: str):
        """Update just the color for a temperature."""
        preset = self.selected_preset
        if preset and temp in preset.entries:
            preset.entries[temp] = color
            self._model._mark_dirty()

    def sort_temperatures(self):
        """Sort entries by temperature ascending."""
        preset = self.selected_preset
        if not preset or len(preset.entries) < 2:
            return

        # Rebuild dict in sorted order
        sorted_items = sorted(preset.entries.items())
        preset.entries.clear()
        preset.entries.update(sorted_items)
        self._model._mark_dirty()
        self.entries_sorted.emit()

    def apply_offset(self, temps: List[float], offset: float, is_scale: bool = False):
        """Apply offset or scale to selected temperatures."""
        preset = self.selected_preset
        if not preset:
            return

        # Build new entries to avoid modifying during iteration
        updates = []
        for temp in temps:
            if temp in preset.entries:
                if is_scale:
                    new_temp = temp * offset
                else:
                    new_temp = temp + offset
                updates.append((temp, new_temp, preset.entries[temp]))

        # Apply updates (remove old, add new)
        for old_temp, new_temp, color in updates:
            del preset.entries[old_temp]
            # Handle collisions
            final_temp = new_temp
            while final_temp in preset.entries:
                final_temp += 0.1
            preset.entries[final_temp] = color

        self.sort_temperatures()  # Re-sort after offset
        self._model._mark_dirty()
        self.preset_selected.emit(self._selected_preset_name or "")

    # --- Data access for View ---

    def get_entries(self) -> List[Tuple[float, str]]:
        """Get sorted list of (temp, color) for table."""
        preset = self.selected_preset
        if not preset:
            return []
        return sorted(preset.entries.items())

    def get_row_data(self, temp: float, color: str) -> List[Any]:
        """Format for table display."""
        return [temp, color]

    def _validate(self) -> bool:
        """Validate before save."""
        if not self._model:
            return True

        presets = {}
        for name, data in self._model.to_dict().items():
            if isinstance(data, HeatmapPreset):
                presets[name] = data
            else:
                presets[name] = HeatmapPreset.from_dict(name, data)

        is_valid, error = self._service.validate(presets)
        if not is_valid:
            self.error_occurred.emit(error)
        return is_valid
