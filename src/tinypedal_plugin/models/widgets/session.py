# Auto-generated widget
# Widget: session

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig


@dataclass
class Session(WidgetConfig):
    name: str = "session"

    # base overrides
    layout: int = 1
    update_interval: int = 100

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=57, position_y=127))

    # cells
    estimated_laps: CellConfig = field(default_factory=lambda: CellConfig(id='estimated_laps', prefix='L ', bkg_color='#008888', column_index=3))
    session_name: CellConfig = field(default_factory=lambda: CellConfig(id='session_name'))
    session_time: CellConfig = field(default_factory=lambda: CellConfig(id='session_time', bkg_color='#880088', column_index=2))
    system_clock: CellConfig = field(default_factory=lambda: CellConfig(id='system_clock', column_index=1))

    # config
    session_text_practice: str = 'PRAC'
    session_text_qualify: str = 'QUAL'
    session_text_race: str = 'RACE'
    session_text_testday: str = 'TEST'
    session_text_warmup: str = 'WARM'
    system_clock_format: str = '%H:%M%p'

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["layout"] = self.layout
        result["update_interval"] = self.update_interval
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.estimated_laps.to_flat())
        result.update(self.session_name.to_flat())
        result.update(self.session_time.to_flat())
        result.update(self.system_clock.to_flat())
        result["session_text_practice"] = self.session_text_practice
        result["session_text_qualify"] = self.session_text_qualify
        result["session_text_race"] = self.session_text_race
        result["session_text_testday"] = self.session_text_testday
        result["session_text_warmup"] = self.session_text_warmup
        result["system_clock_format"] = self.system_clock_format
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Session":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.layout = data.get("layout", obj.layout)
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.estimated_laps = CellConfig.from_flat(data, 'estimated_laps')
        obj.session_name = CellConfig.from_flat(data, 'session_name')
        obj.session_time = CellConfig.from_flat(data, 'session_time')
        obj.system_clock = CellConfig.from_flat(data, 'system_clock')
        obj.session_text_practice = data.get("session_text_practice", obj.session_text_practice)
        obj.session_text_qualify = data.get("session_text_qualify", obj.session_text_qualify)
        obj.session_text_race = data.get("session_text_race", obj.session_text_race)
        obj.session_text_testday = data.get("session_text_testday", obj.session_text_testday)
        obj.session_text_warmup = data.get("session_text_warmup", obj.session_text_warmup)
        obj.system_clock_format = data.get("system_clock_format", obj.system_clock_format)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["layout"] = self.layout
        result["update_interval"] = self.update_interval
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["estimated_laps"] = self.estimated_laps.to_dict()
        result["session_name"] = self.session_name.to_dict()
        result["session_time"] = self.session_time.to_dict()
        result["system_clock"] = self.system_clock.to_dict()
        result["session_text_practice"] = self.session_text_practice
        result["session_text_qualify"] = self.session_text_qualify
        result["session_text_race"] = self.session_text_race
        result["session_text_testday"] = self.session_text_testday
        result["session_text_warmup"] = self.session_text_warmup
        result["system_clock_format"] = self.system_clock_format
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.layout = data.get("layout", obj.layout)
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.estimated_laps = CellConfig.from_dict(data.get("estimated_laps", {}), 'estimated_laps')
        obj.session_name = CellConfig.from_dict(data.get("session_name", {}), 'session_name')
        obj.session_time = CellConfig.from_dict(data.get("session_time", {}), 'session_time')
        obj.system_clock = CellConfig.from_dict(data.get("system_clock", {}), 'system_clock')
        obj.session_text_practice = data.get("session_text_practice", obj.session_text_practice)
        obj.session_text_qualify = data.get("session_text_qualify", obj.session_text_qualify)
        obj.session_text_race = data.get("session_text_race", obj.session_text_race)
        obj.session_text_testday = data.get("session_text_testday", obj.session_text_testday)
        obj.session_text_warmup = data.get("session_text_warmup", obj.session_text_warmup)
        obj.system_clock_format = data.get("system_clock_format", obj.system_clock_format)
        return obj
