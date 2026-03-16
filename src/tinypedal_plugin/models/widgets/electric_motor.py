# Auto-generated widget
# Widget: electric_motor

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig


@dataclass
class ElectricMotor(WidgetConfig):
    name: str = "electric_motor"

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=223, position_y=293))

    # cells
    motor_temperature: CellConfig = field(default_factory=lambda: CellConfig(id='motor_temperature', column_index=1))
    power: CellConfig = field(default_factory=lambda: CellConfig(id='power', column_index=5))
    rpm: CellConfig = field(default_factory=lambda: CellConfig(id='rpm', column_index=3))
    torque: CellConfig = field(default_factory=lambda: CellConfig(id='torque', column_index=4))
    water_temperature: CellConfig = field(default_factory=lambda: CellConfig(id='water_temperature', column_index=2))

    # config
    overheat_threshold_motor: int = 80
    overheat_threshold_water: int = 80
    warning_color_overheat: str = '#FF2200'

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.motor_temperature.to_flat())
        result.update(self.power.to_flat())
        result.update(self.rpm.to_flat())
        result.update(self.torque.to_flat())
        result.update(self.water_temperature.to_flat())
        result["overheat_threshold_motor"] = self.overheat_threshold_motor
        result["overheat_threshold_water"] = self.overheat_threshold_water
        result["warning_color_overheat"] = self.warning_color_overheat
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "ElectricMotor":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.motor_temperature = CellConfig.from_flat(data, 'motor_temperature')
        obj.power = CellConfig.from_flat(data, 'power')
        obj.rpm = CellConfig.from_flat(data, 'rpm')
        obj.torque = CellConfig.from_flat(data, 'torque')
        obj.water_temperature = CellConfig.from_flat(data, 'water_temperature')
        obj.overheat_threshold_motor = data.get("overheat_threshold_motor", obj.overheat_threshold_motor)
        obj.overheat_threshold_water = data.get("overheat_threshold_water", obj.overheat_threshold_water)
        obj.warning_color_overheat = data.get("warning_color_overheat", obj.warning_color_overheat)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["motor_temperature"] = self.motor_temperature.to_dict()
        result["power"] = self.power.to_dict()
        result["rpm"] = self.rpm.to_dict()
        result["torque"] = self.torque.to_dict()
        result["water_temperature"] = self.water_temperature.to_dict()
        result["overheat_threshold_motor"] = self.overheat_threshold_motor
        result["overheat_threshold_water"] = self.overheat_threshold_water
        result["warning_color_overheat"] = self.warning_color_overheat
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ElectricMotor":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.motor_temperature = CellConfig.from_dict(data.get("motor_temperature", {}), 'motor_temperature')
        obj.power = CellConfig.from_dict(data.get("power", {}), 'power')
        obj.rpm = CellConfig.from_dict(data.get("rpm", {}), 'rpm')
        obj.torque = CellConfig.from_dict(data.get("torque", {}), 'torque')
        obj.water_temperature = CellConfig.from_dict(data.get("water_temperature", {}), 'water_temperature')
        obj.overheat_threshold_motor = data.get("overheat_threshold_motor", obj.overheat_threshold_motor)
        obj.overheat_threshold_water = data.get("overheat_threshold_water", obj.overheat_threshold_water)
        obj.warning_color_overheat = data.get("warning_color_overheat", obj.warning_color_overheat)
        return obj
