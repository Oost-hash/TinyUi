# Auto-generated widget
# Widget: suspension_travel

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import GREEN, LIGHT_BLUE, ORANGE, YELLOW_DIM
from ..components import CaptionConfig


@dataclass
class SuspensionTravel(WidgetConfig):
    name: str = "suspension_travel"

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=728, position_y=390))

    # cells
    bump_travel: CellConfig = field(default_factory=lambda: CellConfig(id='bump_travel', caption_text='bump', column_index=2))
    live_position: CellConfig = field(default_factory=lambda: CellConfig(id='live_position', font_color=GREEN.font_color, bkg_color=GREEN.bkg_color, caption_text='live pos', column_index=7))
    live_position_relative_to_static_position: CellConfig = field(default_factory=lambda: CellConfig(id='live_position_relative_to_static_position'))
    maximum_position: CellConfig = field(default_factory=lambda: CellConfig(id='maximum_position', font_color=ORANGE.font_color, bkg_color=ORANGE.bkg_color, caption_text='max pos', column_index=6))
    minimum_position: CellConfig = field(default_factory=lambda: CellConfig(id='minimum_position', font_color=LIGHT_BLUE.font_color, bkg_color=LIGHT_BLUE.bkg_color, caption_text='min pos', column_index=5))
    rebound_travel: CellConfig = field(default_factory=lambda: CellConfig(id='rebound_travel', caption_text='rebound', column_index=3))
    total_travel: CellConfig = field(default_factory=lambda: CellConfig(id='total_travel', caption_text='total', column_index=1))
    travel_ratio: CellConfig = field(default_factory=lambda: CellConfig(id='travel_ratio', font_color=YELLOW_DIM.font_color, bkg_color=YELLOW_DIM.bkg_color, caption_text='t.ratio', column_index=4))

    # components
    caption: CaptionConfig = field(default_factory=CaptionConfig)

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.bump_travel.to_flat())
        result.update(self.live_position.to_flat())
        result.update(self.live_position_relative_to_static_position.to_flat())
        result.update(self.maximum_position.to_flat())
        result.update(self.minimum_position.to_flat())
        result.update(self.rebound_travel.to_flat())
        result.update(self.total_travel.to_flat())
        result.update(self.travel_ratio.to_flat())
        result["bkg_color_caption"] = self.caption.bkg_color
        result["font_color_caption"] = self.caption.font_color
        result["show_caption"] = self.caption.show
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "SuspensionTravel":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.bump_travel = CellConfig.from_flat(data, 'bump_travel')
        obj.live_position = CellConfig.from_flat(data, 'live_position')
        obj.live_position_relative_to_static_position = CellConfig.from_flat(data, 'live_position_relative_to_static_position')
        obj.maximum_position = CellConfig.from_flat(data, 'maximum_position')
        obj.minimum_position = CellConfig.from_flat(data, 'minimum_position')
        obj.rebound_travel = CellConfig.from_flat(data, 'rebound_travel')
        obj.total_travel = CellConfig.from_flat(data, 'total_travel')
        obj.travel_ratio = CellConfig.from_flat(data, 'travel_ratio')
        obj.caption = CaptionConfig(
            bkg_color=data.get("bkg_color_caption", obj.caption.bkg_color),
            font_color=data.get("font_color_caption", obj.caption.font_color),
            show=data.get("show_caption", obj.caption.show),
        )
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["bump_travel"] = self.bump_travel.to_dict()
        result["live_position"] = self.live_position.to_dict()
        result["live_position_relative_to_static_position"] = self.live_position_relative_to_static_position.to_dict()
        result["maximum_position"] = self.maximum_position.to_dict()
        result["minimum_position"] = self.minimum_position.to_dict()
        result["rebound_travel"] = self.rebound_travel.to_dict()
        result["total_travel"] = self.total_travel.to_dict()
        result["travel_ratio"] = self.travel_ratio.to_dict()
        result["caption"] = self.caption.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SuspensionTravel":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.bump_travel = CellConfig.from_dict(data.get("bump_travel", {}), 'bump_travel')
        obj.live_position = CellConfig.from_dict(data.get("live_position", {}), 'live_position')
        obj.live_position_relative_to_static_position = CellConfig.from_dict(data.get("live_position_relative_to_static_position", {}), 'live_position_relative_to_static_position')
        obj.maximum_position = CellConfig.from_dict(data.get("maximum_position", {}), 'maximum_position')
        obj.minimum_position = CellConfig.from_dict(data.get("minimum_position", {}), 'minimum_position')
        obj.rebound_travel = CellConfig.from_dict(data.get("rebound_travel", {}), 'rebound_travel')
        obj.total_travel = CellConfig.from_dict(data.get("total_travel", {}), 'total_travel')
        obj.travel_ratio = CellConfig.from_dict(data.get("travel_ratio", {}), 'travel_ratio')
        obj.caption = CaptionConfig.from_dict(data.get("caption", {}))
        return obj
