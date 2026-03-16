# Auto-generated widget
# Widget: deltabest_extended

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import BRIGHT


@dataclass
class DeltabestExtended(WidgetConfig):
    name: str = "deltabest_extended"

    # base overrides
    layout: int = 1

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=320, position_y=123))

    # cells
    all_time_deltabest: CellConfig = field(default_factory=lambda: CellConfig(id='all_time_deltabest', font_color=BRIGHT.font_color, bkg_color=BRIGHT.bkg_color, prefix='B ', column_index=1))
    deltalast: CellConfig = field(default_factory=lambda: CellConfig(id='deltalast', font_color='#BBBBBB', prefix='L ', column_index=4))
    session_deltabest: CellConfig = field(default_factory=lambda: CellConfig(id='session_deltabest', font_color='#22FFFF', prefix='S ', column_index=2))
    stint_deltabest: CellConfig = field(default_factory=lambda: CellConfig(id='stint_deltabest', font_color='#FFFF22', prefix='T ', column_index=3))

    # config
    decimal_places: int = 3
    delta_display_range: float = 99.999
    freeze_duration: int = 3

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["layout"] = self.layout
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.all_time_deltabest.to_flat())
        result.update(self.deltalast.to_flat())
        result.update(self.session_deltabest.to_flat())
        result.update(self.stint_deltabest.to_flat())
        result["decimal_places"] = self.decimal_places
        result["delta_display_range"] = self.delta_display_range
        result["freeze_duration"] = self.freeze_duration
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "DeltabestExtended":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.layout = data.get("layout", obj.layout)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.all_time_deltabest = CellConfig.from_flat(data, 'all_time_deltabest')
        obj.deltalast = CellConfig.from_flat(data, 'deltalast')
        obj.session_deltabest = CellConfig.from_flat(data, 'session_deltabest')
        obj.stint_deltabest = CellConfig.from_flat(data, 'stint_deltabest')
        obj.decimal_places = data.get("decimal_places", obj.decimal_places)
        obj.delta_display_range = data.get("delta_display_range", obj.delta_display_range)
        obj.freeze_duration = data.get("freeze_duration", obj.freeze_duration)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["layout"] = self.layout
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["all_time_deltabest"] = self.all_time_deltabest.to_dict()
        result["deltalast"] = self.deltalast.to_dict()
        result["session_deltabest"] = self.session_deltabest.to_dict()
        result["stint_deltabest"] = self.stint_deltabest.to_dict()
        result["decimal_places"] = self.decimal_places
        result["delta_display_range"] = self.delta_display_range
        result["freeze_duration"] = self.freeze_duration
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeltabestExtended":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.layout = data.get("layout", obj.layout)
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.all_time_deltabest = CellConfig.from_dict(data.get("all_time_deltabest", {}), 'all_time_deltabest')
        obj.deltalast = CellConfig.from_dict(data.get("deltalast", {}), 'deltalast')
        obj.session_deltabest = CellConfig.from_dict(data.get("session_deltabest", {}), 'session_deltabest')
        obj.stint_deltabest = CellConfig.from_dict(data.get("stint_deltabest", {}), 'stint_deltabest')
        obj.decimal_places = data.get("decimal_places", obj.decimal_places)
        obj.delta_display_range = data.get("delta_display_range", obj.delta_display_range)
        obj.freeze_duration = data.get("freeze_duration", obj.freeze_duration)
        return obj
