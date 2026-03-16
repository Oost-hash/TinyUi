# Auto-generated widget
# Widget: brake_bias

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig


@dataclass
class BrakeBias(WidgetConfig):
    name: str = "brake_bias"

    # base overrides
    layout: int = 1

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=593, position_y=292))

    # cells
    baseline_bias_delta: CellConfig = field(default_factory=lambda: CellConfig(id='baseline_bias_delta', decimal_places=2, column_index=2))
    brake_bias: CellConfig = field(default_factory=lambda: CellConfig(id='brake_bias', decimal_places=2, prefix='BB ', column_index=1))
    brake_migration: CellConfig = field(default_factory=lambda: CellConfig(id='brake_migration', decimal_places=1, prefix='BM ', suffix='F', column_index=3))
    front_and_rear: CellConfig = field(default_factory=lambda: CellConfig(id='front_and_rear', show=False))
    percentage_sign: CellConfig = field(default_factory=lambda: CellConfig(id='percentage_sign'))

    # config
    electric_braking_allocation: int = -1

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["layout"] = self.layout
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.baseline_bias_delta.to_flat())
        result.update(self.brake_bias.to_flat())
        result.update(self.brake_migration.to_flat())
        result.update(self.front_and_rear.to_flat())
        result.update(self.percentage_sign.to_flat())
        result["electric_braking_allocation"] = self.electric_braking_allocation
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "BrakeBias":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.layout = data.get("layout", obj.layout)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.baseline_bias_delta = CellConfig.from_flat(data, 'baseline_bias_delta')
        obj.brake_bias = CellConfig.from_flat(data, 'brake_bias')
        obj.brake_migration = CellConfig.from_flat(data, 'brake_migration')
        obj.front_and_rear = CellConfig.from_flat(data, 'front_and_rear')
        obj.percentage_sign = CellConfig.from_flat(data, 'percentage_sign')
        obj.electric_braking_allocation = data.get("electric_braking_allocation", obj.electric_braking_allocation)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["layout"] = self.layout
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["baseline_bias_delta"] = self.baseline_bias_delta.to_dict()
        result["brake_bias"] = self.brake_bias.to_dict()
        result["brake_migration"] = self.brake_migration.to_dict()
        result["front_and_rear"] = self.front_and_rear.to_dict()
        result["percentage_sign"] = self.percentage_sign.to_dict()
        result["electric_braking_allocation"] = self.electric_braking_allocation
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BrakeBias":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.layout = data.get("layout", obj.layout)
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.baseline_bias_delta = CellConfig.from_dict(data.get("baseline_bias_delta", {}), 'baseline_bias_delta')
        obj.brake_bias = CellConfig.from_dict(data.get("brake_bias", {}), 'brake_bias')
        obj.brake_migration = CellConfig.from_dict(data.get("brake_migration", {}), 'brake_migration')
        obj.front_and_rear = CellConfig.from_dict(data.get("front_and_rear", {}), 'front_and_rear')
        obj.percentage_sign = CellConfig.from_dict(data.get("percentage_sign", {}), 'percentage_sign')
        obj.electric_braking_allocation = data.get("electric_braking_allocation", obj.electric_braking_allocation)
        return obj
