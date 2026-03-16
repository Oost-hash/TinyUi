# Auto-generated widget
# Widget: timing

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import BRIGHT, ORANGE, SECONDARY


@dataclass
class Timing(WidgetConfig):
    name: str = "timing"

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=147, position_y=500))

    # cells
    average_pace: CellConfig = field(default_factory=lambda: CellConfig(id='average_pace', font_color='#AADD88', prefix='A ', column_index=20))
    best: CellConfig = field(default_factory=lambda: CellConfig(id='best', font_color=BRIGHT.font_color, bkg_color=BRIGHT.bkg_color, prefix='B ', column_index=2))
    current: CellConfig = field(default_factory=lambda: CellConfig(id='current', font_color='#88FF88', prefix='C ', column_index=4))
    estimated: CellConfig = field(default_factory=lambda: CellConfig(id='estimated', font_color='#FFFF88', prefix='E ', column_index=5))
    invalid_laptime: CellConfig = field(default_factory=lambda: CellConfig(id='invalid_laptime', font_color=ORANGE.font_color, bkg_color=ORANGE.bkg_color))
    last: CellConfig = field(default_factory=lambda: CellConfig(id='last', prefix='L ', column_index=3))
    session_best: CellConfig = field(default_factory=lambda: CellConfig(id='session_best', font_color='#44DDFF', prefix='S ', column_index=1))
    session_best_from_same_class_only: CellConfig = field(default_factory=lambda: CellConfig(id='session_best_from_same_class_only'))
    session_personal_best: CellConfig = field(default_factory=lambda: CellConfig(id='session_personal_best', font_color='#EE77FF', prefix='P ', column_index=10))
    stint_best: CellConfig = field(default_factory=lambda: CellConfig(id='stint_best', font_color=SECONDARY.font_color, bkg_color=SECONDARY.bkg_color, prefix='T ', column_index=15))

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.average_pace.to_flat())
        result.update(self.best.to_flat())
        result.update(self.current.to_flat())
        result.update(self.estimated.to_flat())
        result.update(self.invalid_laptime.to_flat())
        result.update(self.last.to_flat())
        result.update(self.session_best.to_flat())
        result.update(self.session_best_from_same_class_only.to_flat())
        result.update(self.session_personal_best.to_flat())
        result.update(self.stint_best.to_flat())
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Timing":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.average_pace = CellConfig.from_flat(data, 'average_pace')
        obj.best = CellConfig.from_flat(data, 'best')
        obj.current = CellConfig.from_flat(data, 'current')
        obj.estimated = CellConfig.from_flat(data, 'estimated')
        obj.invalid_laptime = CellConfig.from_flat(data, 'invalid_laptime')
        obj.last = CellConfig.from_flat(data, 'last')
        obj.session_best = CellConfig.from_flat(data, 'session_best')
        obj.session_best_from_same_class_only = CellConfig.from_flat(data, 'session_best_from_same_class_only')
        obj.session_personal_best = CellConfig.from_flat(data, 'session_personal_best')
        obj.stint_best = CellConfig.from_flat(data, 'stint_best')
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["average_pace"] = self.average_pace.to_dict()
        result["best"] = self.best.to_dict()
        result["current"] = self.current.to_dict()
        result["estimated"] = self.estimated.to_dict()
        result["invalid_laptime"] = self.invalid_laptime.to_dict()
        result["last"] = self.last.to_dict()
        result["session_best"] = self.session_best.to_dict()
        result["session_best_from_same_class_only"] = self.session_best_from_same_class_only.to_dict()
        result["session_personal_best"] = self.session_personal_best.to_dict()
        result["stint_best"] = self.stint_best.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Timing":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.average_pace = CellConfig.from_dict(data.get("average_pace", {}), 'average_pace')
        obj.best = CellConfig.from_dict(data.get("best", {}), 'best')
        obj.current = CellConfig.from_dict(data.get("current", {}), 'current')
        obj.estimated = CellConfig.from_dict(data.get("estimated", {}), 'estimated')
        obj.invalid_laptime = CellConfig.from_dict(data.get("invalid_laptime", {}), 'invalid_laptime')
        obj.last = CellConfig.from_dict(data.get("last", {}), 'last')
        obj.session_best = CellConfig.from_dict(data.get("session_best", {}), 'session_best')
        obj.session_best_from_same_class_only = CellConfig.from_dict(data.get("session_best_from_same_class_only", {}), 'session_best_from_same_class_only')
        obj.session_personal_best = CellConfig.from_dict(data.get("session_personal_best", {}), 'session_personal_best')
        obj.stint_best = CellConfig.from_dict(data.get("stint_best", {}), 'stint_best')
        return obj
