# Auto-generated widget
# Widget: laps_and_position

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import BRIGHT


@dataclass
class LapsAndPosition(WidgetConfig):
    name: str = "laps_and_position"

    # base overrides
    layout: int = 1
    update_interval: int = 100

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=57, position_y=42))

    # cells
    lap_number: CellConfig = field(default_factory=lambda: CellConfig(id='lap_number', font_color=BRIGHT.font_color, bkg_color=BRIGHT.bkg_color, prefix='L', column_index=1))
    maxlap_warn: CellConfig = field(default_factory=lambda: CellConfig(id='maxlap_warn', bkg_color='#FF0000'))
    position_in_class: CellConfig = field(default_factory=lambda: CellConfig(id='position_in_class', prefix='C', bkg_color='#666666', column_index=3))
    position_overall: CellConfig = field(default_factory=lambda: CellConfig(id='position_overall', prefix='P', column_index=2))

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["layout"] = self.layout
        result["update_interval"] = self.update_interval
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.lap_number.to_flat())
        result.update(self.maxlap_warn.to_flat())
        result.update(self.position_in_class.to_flat())
        result.update(self.position_overall.to_flat())
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "LapsAndPosition":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.layout = data.get("layout", obj.layout)
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.lap_number = CellConfig.from_flat(data, 'lap_number')
        obj.maxlap_warn = CellConfig.from_flat(data, 'maxlap_warn')
        obj.position_in_class = CellConfig.from_flat(data, 'position_in_class')
        obj.position_overall = CellConfig.from_flat(data, 'position_overall')
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["layout"] = self.layout
        result["update_interval"] = self.update_interval
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["lap_number"] = self.lap_number.to_dict()
        result["maxlap_warn"] = self.maxlap_warn.to_dict()
        result["position_in_class"] = self.position_in_class.to_dict()
        result["position_overall"] = self.position_overall.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LapsAndPosition":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.layout = data.get("layout", obj.layout)
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.lap_number = CellConfig.from_dict(data.get("lap_number", {}), 'lap_number')
        obj.maxlap_warn = CellConfig.from_dict(data.get("maxlap_warn", {}), 'maxlap_warn')
        obj.position_in_class = CellConfig.from_dict(data.get("position_in_class", {}), 'position_in_class')
        obj.position_overall = CellConfig.from_dict(data.get("position_overall", {}), 'position_overall')
        return obj
