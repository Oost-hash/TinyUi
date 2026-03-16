# Auto-generated widget
# Widget: system_performance

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig


@dataclass
class SystemPerformance(WidgetConfig):
    name: str = "system_performance"

    # base overrides
    update_interval: int = 500

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=145, position_y=710))

    # cells
    system: CellConfig = field(default_factory=lambda: CellConfig(id='system', prefix='OS ', column_index=1))
    system_performance: CellConfig = field(default_factory=lambda: CellConfig(id='system_performance'))
    tinypedal: CellConfig = field(default_factory=lambda: CellConfig(id='tinypedal', prefix='TP ', column_index=2))
    tinypedal_performance: CellConfig = field(default_factory=lambda: CellConfig(id='tinypedal_performance'))

    # config
    average_samples: int = 40

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["update_interval"] = self.update_interval
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.system.to_flat())
        result.update(self.system_performance.to_flat())
        result.update(self.tinypedal.to_flat())
        result.update(self.tinypedal_performance.to_flat())
        result["average_samples"] = self.average_samples
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "SystemPerformance":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.system = CellConfig.from_flat(data, 'system')
        obj.system_performance = CellConfig.from_flat(data, 'system_performance')
        obj.tinypedal = CellConfig.from_flat(data, 'tinypedal')
        obj.tinypedal_performance = CellConfig.from_flat(data, 'tinypedal_performance')
        obj.average_samples = data.get("average_samples", obj.average_samples)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["update_interval"] = self.update_interval
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["system"] = self.system.to_dict()
        result["system_performance"] = self.system_performance.to_dict()
        result["tinypedal"] = self.tinypedal.to_dict()
        result["tinypedal_performance"] = self.tinypedal_performance.to_dict()
        result["average_samples"] = self.average_samples
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemPerformance":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.system = CellConfig.from_dict(data.get("system", {}), 'system')
        obj.system_performance = CellConfig.from_dict(data.get("system_performance", {}), 'system_performance')
        obj.tinypedal = CellConfig.from_dict(data.get("tinypedal", {}), 'tinypedal')
        obj.tinypedal_performance = CellConfig.from_dict(data.get("tinypedal_performance", {}), 'tinypedal_performance')
        obj.average_samples = data.get("average_samples", obj.average_samples)
        return obj
