# Auto-generated widget
# Widget: elevation

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig


@dataclass
class Elevation(WidgetConfig):
    name: str = "elevation"

    # base overrides
    bkg_color: str = '#66222222'

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=115, position_y=753))

    # cells
    background: CellConfig = field(default_factory=lambda: CellConfig(id='background'))
    elevation: CellConfig = field(default_factory=lambda: CellConfig(id='elevation', bkg_color='#CC222222'))
    elevation_background: CellConfig = field(default_factory=lambda: CellConfig(id='elevation_background'))
    elevation_line: CellConfig = field(default_factory=lambda: CellConfig(id='elevation_line'))
    elevation_progress: CellConfig = field(default_factory=lambda: CellConfig(id='elevation_progress'))
    elevation_progress_line: CellConfig = field(default_factory=lambda: CellConfig(id='elevation_progress_line'))
    elevation_reading: CellConfig = field(default_factory=lambda: CellConfig(id='elevation_reading'))
    elevation_scale: CellConfig = field(default_factory=lambda: CellConfig(id='elevation_scale'))
    position_mark: CellConfig = field(default_factory=lambda: CellConfig(id='position_mark'))
    sector_line: CellConfig = field(default_factory=lambda: CellConfig(id='sector_line'))
    start_line: CellConfig = field(default_factory=lambda: CellConfig(id='start_line'))
    zero_elevation_line: CellConfig = field(default_factory=lambda: CellConfig(id='zero_elevation_line'))

    # config
    display_detail_level: int = 1
    display_height: int = 60
    display_margin_bottom: int = 10
    display_margin_top: int = 10
    display_width: int = 400
    elevation_line_color: str = '#AA888888'
    elevation_line_width: int = 2
    elevation_progress_color: str = '#66CCCCCC'
    elevation_progress_line_color: str = '#FFFFFF'
    elevation_progress_line_width: int = 2
    elevation_reading_offset_x: float = 0.12
    elevation_reading_offset_y: float = 0.15
    elevation_reading_text_alignment: str = 'Left'
    elevation_scale_offset_x: float = 0.88
    elevation_scale_offset_y: float = 0.15
    elevation_scale_text_alignment: str = 'Right'
    font_color: str = '#FFFFFF'
    position_mark_color: str = '#FF4422'
    position_mark_width: int = 2
    sector_line_color: str = '#88888888'
    sector_line_width: int = 2
    start_line_color: str = '#88FFFFFF'
    start_line_width: int = 4
    zero_elevation_line_color: str = '#88FFFFFF'
    zero_elevation_line_width: int = 1

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["bkg_color"] = self.bkg_color
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.background.to_flat())
        result.update(self.elevation.to_flat())
        result.update(self.elevation_background.to_flat())
        result.update(self.elevation_line.to_flat())
        result.update(self.elevation_progress.to_flat())
        result.update(self.elevation_progress_line.to_flat())
        result.update(self.elevation_reading.to_flat())
        result.update(self.elevation_scale.to_flat())
        result.update(self.position_mark.to_flat())
        result.update(self.sector_line.to_flat())
        result.update(self.start_line.to_flat())
        result.update(self.zero_elevation_line.to_flat())
        result["display_detail_level"] = self.display_detail_level
        result["display_height"] = self.display_height
        result["display_margin_bottom"] = self.display_margin_bottom
        result["display_margin_top"] = self.display_margin_top
        result["display_width"] = self.display_width
        result["elevation_line_color"] = self.elevation_line_color
        result["elevation_line_width"] = self.elevation_line_width
        result["elevation_progress_color"] = self.elevation_progress_color
        result["elevation_progress_line_color"] = self.elevation_progress_line_color
        result["elevation_progress_line_width"] = self.elevation_progress_line_width
        result["elevation_reading_offset_x"] = self.elevation_reading_offset_x
        result["elevation_reading_offset_y"] = self.elevation_reading_offset_y
        result["elevation_reading_text_alignment"] = self.elevation_reading_text_alignment
        result["elevation_scale_offset_x"] = self.elevation_scale_offset_x
        result["elevation_scale_offset_y"] = self.elevation_scale_offset_y
        result["elevation_scale_text_alignment"] = self.elevation_scale_text_alignment
        result["font_color"] = self.font_color
        result["position_mark_color"] = self.position_mark_color
        result["position_mark_width"] = self.position_mark_width
        result["sector_line_color"] = self.sector_line_color
        result["sector_line_width"] = self.sector_line_width
        result["start_line_color"] = self.start_line_color
        result["start_line_width"] = self.start_line_width
        result["zero_elevation_line_color"] = self.zero_elevation_line_color
        result["zero_elevation_line_width"] = self.zero_elevation_line_width
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Elevation":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bkg_color = data.get("bkg_color", obj.bkg_color)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.background = CellConfig.from_flat(data, 'background')
        obj.elevation = CellConfig.from_flat(data, 'elevation')
        obj.elevation_background = CellConfig.from_flat(data, 'elevation_background')
        obj.elevation_line = CellConfig.from_flat(data, 'elevation_line')
        obj.elevation_progress = CellConfig.from_flat(data, 'elevation_progress')
        obj.elevation_progress_line = CellConfig.from_flat(data, 'elevation_progress_line')
        obj.elevation_reading = CellConfig.from_flat(data, 'elevation_reading')
        obj.elevation_scale = CellConfig.from_flat(data, 'elevation_scale')
        obj.position_mark = CellConfig.from_flat(data, 'position_mark')
        obj.sector_line = CellConfig.from_flat(data, 'sector_line')
        obj.start_line = CellConfig.from_flat(data, 'start_line')
        obj.zero_elevation_line = CellConfig.from_flat(data, 'zero_elevation_line')
        obj.display_detail_level = data.get("display_detail_level", obj.display_detail_level)
        obj.display_height = data.get("display_height", obj.display_height)
        obj.display_margin_bottom = data.get("display_margin_bottom", obj.display_margin_bottom)
        obj.display_margin_top = data.get("display_margin_top", obj.display_margin_top)
        obj.display_width = data.get("display_width", obj.display_width)
        obj.elevation_line_color = data.get("elevation_line_color", obj.elevation_line_color)
        obj.elevation_line_width = data.get("elevation_line_width", obj.elevation_line_width)
        obj.elevation_progress_color = data.get("elevation_progress_color", obj.elevation_progress_color)
        obj.elevation_progress_line_color = data.get("elevation_progress_line_color", obj.elevation_progress_line_color)
        obj.elevation_progress_line_width = data.get("elevation_progress_line_width", obj.elevation_progress_line_width)
        obj.elevation_reading_offset_x = data.get("elevation_reading_offset_x", obj.elevation_reading_offset_x)
        obj.elevation_reading_offset_y = data.get("elevation_reading_offset_y", obj.elevation_reading_offset_y)
        obj.elevation_reading_text_alignment = data.get("elevation_reading_text_alignment", obj.elevation_reading_text_alignment)
        obj.elevation_scale_offset_x = data.get("elevation_scale_offset_x", obj.elevation_scale_offset_x)
        obj.elevation_scale_offset_y = data.get("elevation_scale_offset_y", obj.elevation_scale_offset_y)
        obj.elevation_scale_text_alignment = data.get("elevation_scale_text_alignment", obj.elevation_scale_text_alignment)
        obj.font_color = data.get("font_color", obj.font_color)
        obj.position_mark_color = data.get("position_mark_color", obj.position_mark_color)
        obj.position_mark_width = data.get("position_mark_width", obj.position_mark_width)
        obj.sector_line_color = data.get("sector_line_color", obj.sector_line_color)
        obj.sector_line_width = data.get("sector_line_width", obj.sector_line_width)
        obj.start_line_color = data.get("start_line_color", obj.start_line_color)
        obj.start_line_width = data.get("start_line_width", obj.start_line_width)
        obj.zero_elevation_line_color = data.get("zero_elevation_line_color", obj.zero_elevation_line_color)
        obj.zero_elevation_line_width = data.get("zero_elevation_line_width", obj.zero_elevation_line_width)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bkg_color"] = self.bkg_color
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["background"] = self.background.to_dict()
        result["elevation"] = self.elevation.to_dict()
        result["elevation_background"] = self.elevation_background.to_dict()
        result["elevation_line"] = self.elevation_line.to_dict()
        result["elevation_progress"] = self.elevation_progress.to_dict()
        result["elevation_progress_line"] = self.elevation_progress_line.to_dict()
        result["elevation_reading"] = self.elevation_reading.to_dict()
        result["elevation_scale"] = self.elevation_scale.to_dict()
        result["position_mark"] = self.position_mark.to_dict()
        result["sector_line"] = self.sector_line.to_dict()
        result["start_line"] = self.start_line.to_dict()
        result["zero_elevation_line"] = self.zero_elevation_line.to_dict()
        result["display_detail_level"] = self.display_detail_level
        result["display_height"] = self.display_height
        result["display_margin_bottom"] = self.display_margin_bottom
        result["display_margin_top"] = self.display_margin_top
        result["display_width"] = self.display_width
        result["elevation_line_color"] = self.elevation_line_color
        result["elevation_line_width"] = self.elevation_line_width
        result["elevation_progress_color"] = self.elevation_progress_color
        result["elevation_progress_line_color"] = self.elevation_progress_line_color
        result["elevation_progress_line_width"] = self.elevation_progress_line_width
        result["elevation_reading_offset_x"] = self.elevation_reading_offset_x
        result["elevation_reading_offset_y"] = self.elevation_reading_offset_y
        result["elevation_reading_text_alignment"] = self.elevation_reading_text_alignment
        result["elevation_scale_offset_x"] = self.elevation_scale_offset_x
        result["elevation_scale_offset_y"] = self.elevation_scale_offset_y
        result["elevation_scale_text_alignment"] = self.elevation_scale_text_alignment
        result["font_color"] = self.font_color
        result["position_mark_color"] = self.position_mark_color
        result["position_mark_width"] = self.position_mark_width
        result["sector_line_color"] = self.sector_line_color
        result["sector_line_width"] = self.sector_line_width
        result["start_line_color"] = self.start_line_color
        result["start_line_width"] = self.start_line_width
        result["zero_elevation_line_color"] = self.zero_elevation_line_color
        result["zero_elevation_line_width"] = self.zero_elevation_line_width
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Elevation":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bkg_color = data.get("bkg_color", obj.bkg_color)
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.background = CellConfig.from_dict(data.get("background", {}), 'background')
        obj.elevation = CellConfig.from_dict(data.get("elevation", {}), 'elevation')
        obj.elevation_background = CellConfig.from_dict(data.get("elevation_background", {}), 'elevation_background')
        obj.elevation_line = CellConfig.from_dict(data.get("elevation_line", {}), 'elevation_line')
        obj.elevation_progress = CellConfig.from_dict(data.get("elevation_progress", {}), 'elevation_progress')
        obj.elevation_progress_line = CellConfig.from_dict(data.get("elevation_progress_line", {}), 'elevation_progress_line')
        obj.elevation_reading = CellConfig.from_dict(data.get("elevation_reading", {}), 'elevation_reading')
        obj.elevation_scale = CellConfig.from_dict(data.get("elevation_scale", {}), 'elevation_scale')
        obj.position_mark = CellConfig.from_dict(data.get("position_mark", {}), 'position_mark')
        obj.sector_line = CellConfig.from_dict(data.get("sector_line", {}), 'sector_line')
        obj.start_line = CellConfig.from_dict(data.get("start_line", {}), 'start_line')
        obj.zero_elevation_line = CellConfig.from_dict(data.get("zero_elevation_line", {}), 'zero_elevation_line')
        obj.display_detail_level = data.get("display_detail_level", obj.display_detail_level)
        obj.display_height = data.get("display_height", obj.display_height)
        obj.display_margin_bottom = data.get("display_margin_bottom", obj.display_margin_bottom)
        obj.display_margin_top = data.get("display_margin_top", obj.display_margin_top)
        obj.display_width = data.get("display_width", obj.display_width)
        obj.elevation_line_color = data.get("elevation_line_color", obj.elevation_line_color)
        obj.elevation_line_width = data.get("elevation_line_width", obj.elevation_line_width)
        obj.elevation_progress_color = data.get("elevation_progress_color", obj.elevation_progress_color)
        obj.elevation_progress_line_color = data.get("elevation_progress_line_color", obj.elevation_progress_line_color)
        obj.elevation_progress_line_width = data.get("elevation_progress_line_width", obj.elevation_progress_line_width)
        obj.elevation_reading_offset_x = data.get("elevation_reading_offset_x", obj.elevation_reading_offset_x)
        obj.elevation_reading_offset_y = data.get("elevation_reading_offset_y", obj.elevation_reading_offset_y)
        obj.elevation_reading_text_alignment = data.get("elevation_reading_text_alignment", obj.elevation_reading_text_alignment)
        obj.elevation_scale_offset_x = data.get("elevation_scale_offset_x", obj.elevation_scale_offset_x)
        obj.elevation_scale_offset_y = data.get("elevation_scale_offset_y", obj.elevation_scale_offset_y)
        obj.elevation_scale_text_alignment = data.get("elevation_scale_text_alignment", obj.elevation_scale_text_alignment)
        obj.font_color = data.get("font_color", obj.font_color)
        obj.position_mark_color = data.get("position_mark_color", obj.position_mark_color)
        obj.position_mark_width = data.get("position_mark_width", obj.position_mark_width)
        obj.sector_line_color = data.get("sector_line_color", obj.sector_line_color)
        obj.sector_line_width = data.get("sector_line_width", obj.sector_line_width)
        obj.start_line_color = data.get("start_line_color", obj.start_line_color)
        obj.start_line_width = data.get("start_line_width", obj.start_line_width)
        obj.zero_elevation_line_color = data.get("zero_elevation_line_color", obj.zero_elevation_line_color)
        obj.zero_elevation_line_width = data.get("zero_elevation_line_width", obj.zero_elevation_line_width)
        return obj
