# Auto-generated widget
# Widget: drs

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import DISABLED


@dataclass
class Drs(WidgetConfig):
    name: str = "drs"

    # groups
    bar: BarConfig = field(default_factory=lambda: BarConfig(bar_padding_horizontal=0.5, bar_padding_vertical=0.2))
    font: FontConfig = field(default_factory=lambda: FontConfig(font_size=30))
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=504, position_y=352))

    # cells
    activated: CellConfig = field(default_factory=lambda: CellConfig(id='activated', font_color='#000000', bkg_color='#44FF00'))
    allowed: CellConfig = field(default_factory=lambda: CellConfig(id='allowed', font_color='#000000', bkg_color='#FF4400'))
    available: CellConfig = field(default_factory=lambda: CellConfig(id='available', font_color='#000000', bkg_color='#00CCFF'))
    not_available: CellConfig = field(default_factory=lambda: CellConfig(id='not_available', font_color=DISABLED.font_color, bkg_color=DISABLED.bkg_color))

    # config
    drs_text: str = 'DRS'

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.activated.to_flat())
        result.update(self.allowed.to_flat())
        result.update(self.available.to_flat())
        result.update(self.not_available.to_flat())
        result["drs_text"] = self.drs_text
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Drs":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_flat(data)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.activated = CellConfig.from_flat(data, 'activated')
        obj.allowed = CellConfig.from_flat(data, 'allowed')
        obj.available = CellConfig.from_flat(data, 'available')
        obj.not_available = CellConfig.from_flat(data, 'not_available')
        obj.drs_text = data.get("drs_text", obj.drs_text)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["activated"] = self.activated.to_dict()
        result["allowed"] = self.allowed.to_dict()
        result["available"] = self.available.to_dict()
        result["not_available"] = self.not_available.to_dict()
        result["drs_text"] = self.drs_text
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Drs":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.activated = CellConfig.from_dict(data.get("activated", {}), 'activated')
        obj.allowed = CellConfig.from_dict(data.get("allowed", {}), 'allowed')
        obj.available = CellConfig.from_dict(data.get("available", {}), 'available')
        obj.not_available = CellConfig.from_dict(data.get("not_available", {}), 'not_available')
        obj.drs_text = data.get("drs_text", obj.drs_text)
        return obj
