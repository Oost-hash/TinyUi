# Auto-generated widget
# Widget: force

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import PLAYER, PLAYER_HIGHLIGHT


@dataclass
class Force(WidgetConfig):
    name: str = "force"

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=453, position_y=395))

    # cells
    downforce_ratio: CellConfig = field(default_factory=lambda: CellConfig(id='downforce_ratio', font_color=PLAYER_HIGHLIGHT.font_color, bkg_color=PLAYER_HIGHLIGHT.bkg_color, column_index=3))
    front_downforce: CellConfig = field(default_factory=lambda: CellConfig(id='front_downforce', column_index=4))
    g_force: CellConfig = field(default_factory=lambda: CellConfig(id='g_force', font_color='#FFCC00'))
    lat_gforce: CellConfig = field(default_factory=lambda: CellConfig(id='lat_gforce', column_index=2))
    long_gforce: CellConfig = field(default_factory=lambda: CellConfig(id='long_gforce', column_index=1))
    rear_downforce: CellConfig = field(default_factory=lambda: CellConfig(id='rear_downforce', column_index=5))

    # config
    warning_color_liftforce: str = '#FF2200'

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.downforce_ratio.to_flat())
        result.update(self.front_downforce.to_flat())
        result.update(self.g_force.to_flat())
        result.update(self.lat_gforce.to_flat())
        result.update(self.long_gforce.to_flat())
        result.update(self.rear_downforce.to_flat())
        result["warning_color_liftforce"] = self.warning_color_liftforce
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Force":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.downforce_ratio = CellConfig.from_flat(data, 'downforce_ratio')
        obj.front_downforce = CellConfig.from_flat(data, 'front_downforce')
        obj.g_force = CellConfig.from_flat(data, 'g_force')
        obj.lat_gforce = CellConfig.from_flat(data, 'lat_gforce')
        obj.long_gforce = CellConfig.from_flat(data, 'long_gforce')
        obj.rear_downforce = CellConfig.from_flat(data, 'rear_downforce')
        obj.warning_color_liftforce = data.get("warning_color_liftforce", obj.warning_color_liftforce)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["downforce_ratio"] = self.downforce_ratio.to_dict()
        result["front_downforce"] = self.front_downforce.to_dict()
        result["g_force"] = self.g_force.to_dict()
        result["lat_gforce"] = self.lat_gforce.to_dict()
        result["long_gforce"] = self.long_gforce.to_dict()
        result["rear_downforce"] = self.rear_downforce.to_dict()
        result["warning_color_liftforce"] = self.warning_color_liftforce
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Force":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.downforce_ratio = CellConfig.from_dict(data.get("downforce_ratio", {}), 'downforce_ratio')
        obj.front_downforce = CellConfig.from_dict(data.get("front_downforce", {}), 'front_downforce')
        obj.g_force = CellConfig.from_dict(data.get("g_force", {}), 'g_force')
        obj.lat_gforce = CellConfig.from_dict(data.get("lat_gforce", {}), 'lat_gforce')
        obj.long_gforce = CellConfig.from_dict(data.get("long_gforce", {}), 'long_gforce')
        obj.rear_downforce = CellConfig.from_dict(data.get("rear_downforce", {}), 'rear_downforce')
        obj.warning_color_liftforce = data.get("warning_color_liftforce", obj.warning_color_liftforce)
        return obj
