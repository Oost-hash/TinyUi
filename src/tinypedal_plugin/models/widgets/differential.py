# Auto-generated widget
# Widget: differential

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import BRIGHT


@dataclass
class Differential(WidgetConfig):
    name: str = "differential"

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=57, position_y=860))

    # cells
    coast_front: CellConfig = field(default_factory=lambda: CellConfig(id='coast_front', prefix='C '))
    coast_locking_front: CellConfig = field(default_factory=lambda: CellConfig(id='coast_locking_front', column_index=2))
    coast_locking_rear: CellConfig = field(default_factory=lambda: CellConfig(id='coast_locking_rear', font_color=BRIGHT.font_color, bkg_color=BRIGHT.bkg_color, column_index=4))
    coast_rear: CellConfig = field(default_factory=lambda: CellConfig(id='coast_rear', prefix='C '))
    inverted_locking: CellConfig = field(default_factory=lambda: CellConfig(id='inverted_locking', show=False))
    power_front: CellConfig = field(default_factory=lambda: CellConfig(id='power_front', prefix='P '))
    power_locking_front: CellConfig = field(default_factory=lambda: CellConfig(id='power_locking_front', column_index=1))
    power_locking_rear: CellConfig = field(default_factory=lambda: CellConfig(id='power_locking_rear', font_color=BRIGHT.font_color, bkg_color=BRIGHT.bkg_color, column_index=3))
    power_rear: CellConfig = field(default_factory=lambda: CellConfig(id='power_rear', prefix='P '))

    # config
    coast_locking_reset_cooldown: int = 5
    decimal_places: int = 0
    off_throttle_threshold: float = 0.01
    on_throttle_threshold: float = 0.01
    power_locking_reset_cooldown: int = 5

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.coast_front.to_flat())
        result.update(self.coast_locking_front.to_flat())
        result.update(self.coast_locking_rear.to_flat())
        result.update(self.coast_rear.to_flat())
        result.update(self.inverted_locking.to_flat())
        result.update(self.power_front.to_flat())
        result.update(self.power_locking_front.to_flat())
        result.update(self.power_locking_rear.to_flat())
        result.update(self.power_rear.to_flat())
        result["coast_locking_reset_cooldown"] = self.coast_locking_reset_cooldown
        result["decimal_places"] = self.decimal_places
        result["off_throttle_threshold"] = self.off_throttle_threshold
        result["on_throttle_threshold"] = self.on_throttle_threshold
        result["power_locking_reset_cooldown"] = self.power_locking_reset_cooldown
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Differential":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.coast_front = CellConfig.from_flat(data, 'coast_front')
        obj.coast_locking_front = CellConfig.from_flat(data, 'coast_locking_front')
        obj.coast_locking_rear = CellConfig.from_flat(data, 'coast_locking_rear')
        obj.coast_rear = CellConfig.from_flat(data, 'coast_rear')
        obj.inverted_locking = CellConfig.from_flat(data, 'inverted_locking')
        obj.power_front = CellConfig.from_flat(data, 'power_front')
        obj.power_locking_front = CellConfig.from_flat(data, 'power_locking_front')
        obj.power_locking_rear = CellConfig.from_flat(data, 'power_locking_rear')
        obj.power_rear = CellConfig.from_flat(data, 'power_rear')
        obj.coast_locking_reset_cooldown = data.get("coast_locking_reset_cooldown", obj.coast_locking_reset_cooldown)
        obj.decimal_places = data.get("decimal_places", obj.decimal_places)
        obj.off_throttle_threshold = data.get("off_throttle_threshold", obj.off_throttle_threshold)
        obj.on_throttle_threshold = data.get("on_throttle_threshold", obj.on_throttle_threshold)
        obj.power_locking_reset_cooldown = data.get("power_locking_reset_cooldown", obj.power_locking_reset_cooldown)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["coast_front"] = self.coast_front.to_dict()
        result["coast_locking_front"] = self.coast_locking_front.to_dict()
        result["coast_locking_rear"] = self.coast_locking_rear.to_dict()
        result["coast_rear"] = self.coast_rear.to_dict()
        result["inverted_locking"] = self.inverted_locking.to_dict()
        result["power_front"] = self.power_front.to_dict()
        result["power_locking_front"] = self.power_locking_front.to_dict()
        result["power_locking_rear"] = self.power_locking_rear.to_dict()
        result["power_rear"] = self.power_rear.to_dict()
        result["coast_locking_reset_cooldown"] = self.coast_locking_reset_cooldown
        result["decimal_places"] = self.decimal_places
        result["off_throttle_threshold"] = self.off_throttle_threshold
        result["on_throttle_threshold"] = self.on_throttle_threshold
        result["power_locking_reset_cooldown"] = self.power_locking_reset_cooldown
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Differential":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.coast_front = CellConfig.from_dict(data.get("coast_front", {}), 'coast_front')
        obj.coast_locking_front = CellConfig.from_dict(data.get("coast_locking_front", {}), 'coast_locking_front')
        obj.coast_locking_rear = CellConfig.from_dict(data.get("coast_locking_rear", {}), 'coast_locking_rear')
        obj.coast_rear = CellConfig.from_dict(data.get("coast_rear", {}), 'coast_rear')
        obj.inverted_locking = CellConfig.from_dict(data.get("inverted_locking", {}), 'inverted_locking')
        obj.power_front = CellConfig.from_dict(data.get("power_front", {}), 'power_front')
        obj.power_locking_front = CellConfig.from_dict(data.get("power_locking_front", {}), 'power_locking_front')
        obj.power_locking_rear = CellConfig.from_dict(data.get("power_locking_rear", {}), 'power_locking_rear')
        obj.power_rear = CellConfig.from_dict(data.get("power_rear", {}), 'power_rear')
        obj.coast_locking_reset_cooldown = data.get("coast_locking_reset_cooldown", obj.coast_locking_reset_cooldown)
        obj.decimal_places = data.get("decimal_places", obj.decimal_places)
        obj.off_throttle_threshold = data.get("off_throttle_threshold", obj.off_throttle_threshold)
        obj.on_throttle_threshold = data.get("on_throttle_threshold", obj.on_throttle_threshold)
        obj.power_locking_reset_cooldown = data.get("power_locking_reset_cooldown", obj.power_locking_reset_cooldown)
        return obj
