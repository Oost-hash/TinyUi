# Auto-generated widget
# Widget: sectors

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import READING


@dataclass
class Sectors(WidgetConfig):
    name: str = "sectors"

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=57, position_y=157))

    # cells
    current_time: CellConfig = field(default_factory=lambda: CellConfig(id='current_time'))
    sector: CellConfig = field(default_factory=lambda: CellConfig(id='sector', font_color=READING.font_color, bkg_color=READING.bkg_color))
    sector_highlighted: CellConfig = field(default_factory=lambda: CellConfig(id='sector_highlighted'))
    target_time: CellConfig = field(default_factory=lambda: CellConfig(id='target_time', font_color=READING.font_color, bkg_color=READING.bkg_color))
    time_gain: CellConfig = field(default_factory=lambda: CellConfig(id='time_gain', font_color='#22CC22', bkg_color='#008800'))
    time_loss: CellConfig = field(default_factory=lambda: CellConfig(id='time_loss', font_color='#BBAA00', bkg_color='#887700'))

    # config
    freeze_duration: int = 5
    target_laptime: str = 'Theoretical'

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.current_time.to_flat())
        result.update(self.sector.to_flat())
        result.update(self.sector_highlighted.to_flat())
        result.update(self.target_time.to_flat())
        result.update(self.time_gain.to_flat())
        result.update(self.time_loss.to_flat())
        result["freeze_duration"] = self.freeze_duration
        result["target_laptime"] = self.target_laptime
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Sectors":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.current_time = CellConfig.from_flat(data, 'current_time')
        obj.sector = CellConfig.from_flat(data, 'sector')
        obj.sector_highlighted = CellConfig.from_flat(data, 'sector_highlighted')
        obj.target_time = CellConfig.from_flat(data, 'target_time')
        obj.time_gain = CellConfig.from_flat(data, 'time_gain')
        obj.time_loss = CellConfig.from_flat(data, 'time_loss')
        obj.freeze_duration = data.get("freeze_duration", obj.freeze_duration)
        obj.target_laptime = data.get("target_laptime", obj.target_laptime)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["current_time"] = self.current_time.to_dict()
        result["sector"] = self.sector.to_dict()
        result["sector_highlighted"] = self.sector_highlighted.to_dict()
        result["target_time"] = self.target_time.to_dict()
        result["time_gain"] = self.time_gain.to_dict()
        result["time_loss"] = self.time_loss.to_dict()
        result["freeze_duration"] = self.freeze_duration
        result["target_laptime"] = self.target_laptime
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Sectors":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.current_time = CellConfig.from_dict(data.get("current_time", {}), 'current_time')
        obj.sector = CellConfig.from_dict(data.get("sector", {}), 'sector')
        obj.sector_highlighted = CellConfig.from_dict(data.get("sector_highlighted", {}), 'sector_highlighted')
        obj.target_time = CellConfig.from_dict(data.get("target_time", {}), 'target_time')
        obj.time_gain = CellConfig.from_dict(data.get("time_gain", {}), 'time_gain')
        obj.time_loss = CellConfig.from_dict(data.get("time_loss", {}), 'time_loss')
        obj.freeze_duration = data.get("freeze_duration", obj.freeze_duration)
        obj.target_laptime = data.get("target_laptime", obj.target_laptime)
        return obj
