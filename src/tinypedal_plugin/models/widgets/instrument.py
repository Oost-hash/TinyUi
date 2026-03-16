# Auto-generated widget
# Widget: instrument

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, PositionConfig, WidgetConfig


@dataclass
class Instrument(WidgetConfig):
    name: str = "instrument"

    # base overrides
    layout: int = 1

    # groups
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=306, position_y=339))

    # cells
    clutch: CellConfig = field(default_factory=lambda: CellConfig(id='clutch', column_index=3))
    headlights: CellConfig = field(default_factory=lambda: CellConfig(id='headlights', column_index=1))
    ignition: CellConfig = field(default_factory=lambda: CellConfig(id='ignition', column_index=2))
    wheel_lock: CellConfig = field(default_factory=lambda: CellConfig(id='wheel_lock', column_index=4))
    wheel_slip: CellConfig = field(default_factory=lambda: CellConfig(id='wheel_slip', column_index=5))

    # config
    icon_size: int = 32
    stalling_rpm_threshold: int = 100
    warning_color_clutch: str = '#00BBDD'
    warning_color_stalling: str = '#00CC00'
    warning_color_wheel_lock: str = '#EE0000'
    warning_color_wheel_slip: str = '#FFAA00'
    wheel_lock_threshold: float = 0.3
    wheel_slip_threshold: float = 0.1

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["layout"] = self.layout
        result.update(self.position.to_flat())
        result.update(self.clutch.to_flat())
        result.update(self.headlights.to_flat())
        result.update(self.ignition.to_flat())
        result.update(self.wheel_lock.to_flat())
        result.update(self.wheel_slip.to_flat())
        result["icon_size"] = self.icon_size
        result["stalling_rpm_threshold"] = self.stalling_rpm_threshold
        result["warning_color_clutch"] = self.warning_color_clutch
        result["warning_color_stalling"] = self.warning_color_stalling
        result["warning_color_wheel_lock"] = self.warning_color_wheel_lock
        result["warning_color_wheel_slip"] = self.warning_color_wheel_slip
        result["wheel_lock_threshold"] = self.wheel_lock_threshold
        result["wheel_slip_threshold"] = self.wheel_slip_threshold
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Instrument":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.layout = data.get("layout", obj.layout)
        obj.position = PositionConfig.from_flat(data)
        obj.clutch = CellConfig.from_flat(data, 'clutch')
        obj.headlights = CellConfig.from_flat(data, 'headlights')
        obj.ignition = CellConfig.from_flat(data, 'ignition')
        obj.wheel_lock = CellConfig.from_flat(data, 'wheel_lock')
        obj.wheel_slip = CellConfig.from_flat(data, 'wheel_slip')
        obj.icon_size = data.get("icon_size", obj.icon_size)
        obj.stalling_rpm_threshold = data.get("stalling_rpm_threshold", obj.stalling_rpm_threshold)
        obj.warning_color_clutch = data.get("warning_color_clutch", obj.warning_color_clutch)
        obj.warning_color_stalling = data.get("warning_color_stalling", obj.warning_color_stalling)
        obj.warning_color_wheel_lock = data.get("warning_color_wheel_lock", obj.warning_color_wheel_lock)
        obj.warning_color_wheel_slip = data.get("warning_color_wheel_slip", obj.warning_color_wheel_slip)
        obj.wheel_lock_threshold = data.get("wheel_lock_threshold", obj.wheel_lock_threshold)
        obj.wheel_slip_threshold = data.get("wheel_slip_threshold", obj.wheel_slip_threshold)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["layout"] = self.layout
        result["position"] = self.position.to_dict()
        result["clutch"] = self.clutch.to_dict()
        result["headlights"] = self.headlights.to_dict()
        result["ignition"] = self.ignition.to_dict()
        result["wheel_lock"] = self.wheel_lock.to_dict()
        result["wheel_slip"] = self.wheel_slip.to_dict()
        result["icon_size"] = self.icon_size
        result["stalling_rpm_threshold"] = self.stalling_rpm_threshold
        result["warning_color_clutch"] = self.warning_color_clutch
        result["warning_color_stalling"] = self.warning_color_stalling
        result["warning_color_wheel_lock"] = self.warning_color_wheel_lock
        result["warning_color_wheel_slip"] = self.warning_color_wheel_slip
        result["wheel_lock_threshold"] = self.wheel_lock_threshold
        result["wheel_slip_threshold"] = self.wheel_slip_threshold
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Instrument":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.layout = data.get("layout", obj.layout)
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.clutch = CellConfig.from_dict(data.get("clutch", {}), 'clutch')
        obj.headlights = CellConfig.from_dict(data.get("headlights", {}), 'headlights')
        obj.ignition = CellConfig.from_dict(data.get("ignition", {}), 'ignition')
        obj.wheel_lock = CellConfig.from_dict(data.get("wheel_lock", {}), 'wheel_lock')
        obj.wheel_slip = CellConfig.from_dict(data.get("wheel_slip", {}), 'wheel_slip')
        obj.icon_size = data.get("icon_size", obj.icon_size)
        obj.stalling_rpm_threshold = data.get("stalling_rpm_threshold", obj.stalling_rpm_threshold)
        obj.warning_color_clutch = data.get("warning_color_clutch", obj.warning_color_clutch)
        obj.warning_color_stalling = data.get("warning_color_stalling", obj.warning_color_stalling)
        obj.warning_color_wheel_lock = data.get("warning_color_wheel_lock", obj.warning_color_wheel_lock)
        obj.warning_color_wheel_slip = data.get("warning_color_wheel_slip", obj.warning_color_wheel_slip)
        obj.wheel_lock_threshold = data.get("wheel_lock_threshold", obj.wheel_lock_threshold)
        obj.wheel_slip_threshold = data.get("wheel_slip_threshold", obj.wheel_slip_threshold)
        return obj
