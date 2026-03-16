# Auto-generated widget
# Widget: brake_performance

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import PLAYER, PLAYER_HIGHLIGHT


@dataclass
class BrakePerformance(WidgetConfig):
    name: str = "brake_performance"

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=57, position_y=753))

    # cells
    braking_rate_gain: CellConfig = field(default_factory=lambda: CellConfig(id='braking_rate_gain', bkg_color='#008800'))
    braking_rate_loss: CellConfig = field(default_factory=lambda: CellConfig(id='braking_rate_loss', bkg_color='#CC7700'))
    delta_braking_rate: CellConfig = field(default_factory=lambda: CellConfig(id='delta_braking_rate', column_index=3))
    delta_braking_rate_in_percentage: CellConfig = field(default_factory=lambda: CellConfig(id='delta_braking_rate_in_percentage'))
    front_wheel_lock_duration: CellConfig = field(default_factory=lambda: CellConfig(id='front_wheel_lock_duration', column_index=4))
    max_braking_rate: CellConfig = field(default_factory=lambda: CellConfig(id='max_braking_rate', font_color=PLAYER_HIGHLIGHT.font_color, bkg_color=PLAYER_HIGHLIGHT.bkg_color, column_index=2))
    rear_wheel_lock_duration: CellConfig = field(default_factory=lambda: CellConfig(id='rear_wheel_lock_duration', column_index=5))
    transient_max_braking_rate: CellConfig = field(default_factory=lambda: CellConfig(id='transient_max_braking_rate', column_index=1))

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.braking_rate_gain.to_flat())
        result.update(self.braking_rate_loss.to_flat())
        result.update(self.delta_braking_rate.to_flat())
        result.update(self.delta_braking_rate_in_percentage.to_flat())
        result.update(self.front_wheel_lock_duration.to_flat())
        result.update(self.max_braking_rate.to_flat())
        result.update(self.rear_wheel_lock_duration.to_flat())
        result.update(self.transient_max_braking_rate.to_flat())
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "BrakePerformance":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.braking_rate_gain = CellConfig.from_flat(data, 'braking_rate_gain')
        obj.braking_rate_loss = CellConfig.from_flat(data, 'braking_rate_loss')
        obj.delta_braking_rate = CellConfig.from_flat(data, 'delta_braking_rate')
        obj.delta_braking_rate_in_percentage = CellConfig.from_flat(data, 'delta_braking_rate_in_percentage')
        obj.front_wheel_lock_duration = CellConfig.from_flat(data, 'front_wheel_lock_duration')
        obj.max_braking_rate = CellConfig.from_flat(data, 'max_braking_rate')
        obj.rear_wheel_lock_duration = CellConfig.from_flat(data, 'rear_wheel_lock_duration')
        obj.transient_max_braking_rate = CellConfig.from_flat(data, 'transient_max_braking_rate')
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["braking_rate_gain"] = self.braking_rate_gain.to_dict()
        result["braking_rate_loss"] = self.braking_rate_loss.to_dict()
        result["delta_braking_rate"] = self.delta_braking_rate.to_dict()
        result["delta_braking_rate_in_percentage"] = self.delta_braking_rate_in_percentage.to_dict()
        result["front_wheel_lock_duration"] = self.front_wheel_lock_duration.to_dict()
        result["max_braking_rate"] = self.max_braking_rate.to_dict()
        result["rear_wheel_lock_duration"] = self.rear_wheel_lock_duration.to_dict()
        result["transient_max_braking_rate"] = self.transient_max_braking_rate.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BrakePerformance":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.braking_rate_gain = CellConfig.from_dict(data.get("braking_rate_gain", {}), 'braking_rate_gain')
        obj.braking_rate_loss = CellConfig.from_dict(data.get("braking_rate_loss", {}), 'braking_rate_loss')
        obj.delta_braking_rate = CellConfig.from_dict(data.get("delta_braking_rate", {}), 'delta_braking_rate')
        obj.delta_braking_rate_in_percentage = CellConfig.from_dict(data.get("delta_braking_rate_in_percentage", {}), 'delta_braking_rate_in_percentage')
        obj.front_wheel_lock_duration = CellConfig.from_dict(data.get("front_wheel_lock_duration", {}), 'front_wheel_lock_duration')
        obj.max_braking_rate = CellConfig.from_dict(data.get("max_braking_rate", {}), 'max_braking_rate')
        obj.rear_wheel_lock_duration = CellConfig.from_dict(data.get("rear_wheel_lock_duration", {}), 'rear_wheel_lock_duration')
        obj.transient_max_braking_rate = CellConfig.from_dict(data.get("transient_max_braking_rate", {}), 'transient_max_braking_rate')
        return obj
