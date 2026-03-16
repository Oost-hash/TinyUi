# Auto-generated widget
# Widget: speedometer

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import AMBER, BRIGHT, BRIGHT_GREEN, GREEN


@dataclass
class Speedometer(WidgetConfig):
    name: str = "speedometer"

    # base overrides
    layout: int = 1

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=57, position_y=640))

    # cells
    speed: CellConfig = field(default_factory=lambda: CellConfig(id='speed', column_index=1))
    speed_fastest: CellConfig = field(default_factory=lambda: CellConfig(id='speed_fastest', font_color=BRIGHT.font_color, bkg_color=BRIGHT.bkg_color, column_index=4))
    speed_maximum: CellConfig = field(default_factory=lambda: CellConfig(id='speed_maximum', font_color=BRIGHT_GREEN.font_color, bkg_color=BRIGHT_GREEN.bkg_color, column_index=3))
    speed_minimum: CellConfig = field(default_factory=lambda: CellConfig(id='speed_minimum', font_color=AMBER.font_color, bkg_color=AMBER.bkg_color, column_index=2))

    # config
    decimal_places: int = 1
    leading_zero: int = 1
    off_throttle_threshold: float = 0.5
    on_throttle_threshold: float = 0.01
    speed_maximum_reset_cooldown: int = 10
    speed_minimum_reset_cooldown: int = 5

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["layout"] = self.layout
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.speed.to_flat())
        result.update(self.speed_fastest.to_flat())
        result.update(self.speed_maximum.to_flat())
        result.update(self.speed_minimum.to_flat())
        result["decimal_places"] = self.decimal_places
        result["leading_zero"] = self.leading_zero
        result["off_throttle_threshold"] = self.off_throttle_threshold
        result["on_throttle_threshold"] = self.on_throttle_threshold
        result["speed_maximum_reset_cooldown"] = self.speed_maximum_reset_cooldown
        result["speed_minimum_reset_cooldown"] = self.speed_minimum_reset_cooldown
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Speedometer":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.layout = data.get("layout", obj.layout)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.speed = CellConfig.from_flat(data, 'speed')
        obj.speed_fastest = CellConfig.from_flat(data, 'speed_fastest')
        obj.speed_maximum = CellConfig.from_flat(data, 'speed_maximum')
        obj.speed_minimum = CellConfig.from_flat(data, 'speed_minimum')
        obj.decimal_places = data.get("decimal_places", obj.decimal_places)
        obj.leading_zero = data.get("leading_zero", obj.leading_zero)
        obj.off_throttle_threshold = data.get("off_throttle_threshold", obj.off_throttle_threshold)
        obj.on_throttle_threshold = data.get("on_throttle_threshold", obj.on_throttle_threshold)
        obj.speed_maximum_reset_cooldown = data.get("speed_maximum_reset_cooldown", obj.speed_maximum_reset_cooldown)
        obj.speed_minimum_reset_cooldown = data.get("speed_minimum_reset_cooldown", obj.speed_minimum_reset_cooldown)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["layout"] = self.layout
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["speed"] = self.speed.to_dict()
        result["speed_fastest"] = self.speed_fastest.to_dict()
        result["speed_maximum"] = self.speed_maximum.to_dict()
        result["speed_minimum"] = self.speed_minimum.to_dict()
        result["decimal_places"] = self.decimal_places
        result["leading_zero"] = self.leading_zero
        result["off_throttle_threshold"] = self.off_throttle_threshold
        result["on_throttle_threshold"] = self.on_throttle_threshold
        result["speed_maximum_reset_cooldown"] = self.speed_maximum_reset_cooldown
        result["speed_minimum_reset_cooldown"] = self.speed_minimum_reset_cooldown
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Speedometer":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.layout = data.get("layout", obj.layout)
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.speed = CellConfig.from_dict(data.get("speed", {}), 'speed')
        obj.speed_fastest = CellConfig.from_dict(data.get("speed_fastest", {}), 'speed_fastest')
        obj.speed_maximum = CellConfig.from_dict(data.get("speed_maximum", {}), 'speed_maximum')
        obj.speed_minimum = CellConfig.from_dict(data.get("speed_minimum", {}), 'speed_minimum')
        obj.decimal_places = data.get("decimal_places", obj.decimal_places)
        obj.leading_zero = data.get("leading_zero", obj.leading_zero)
        obj.off_throttle_threshold = data.get("off_throttle_threshold", obj.off_throttle_threshold)
        obj.on_throttle_threshold = data.get("on_throttle_threshold", obj.on_throttle_threshold)
        obj.speed_maximum_reset_cooldown = data.get("speed_maximum_reset_cooldown", obj.speed_maximum_reset_cooldown)
        obj.speed_minimum_reset_cooldown = data.get("speed_minimum_reset_cooldown", obj.speed_minimum_reset_cooldown)
        return obj
