# Auto-generated widget
# Widget: pace_notes

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import NOTES


@dataclass
class PaceNotes(WidgetConfig):
    name: str = "pace_notes"

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=739, position_y=251))

    # cells
    background: CellConfig = field(default_factory=lambda: CellConfig(id='background'))
    comments: CellConfig = field(default_factory=lambda: CellConfig(id='comments', font_color=NOTES.font_color, bkg_color=NOTES.bkg_color, show=False, column_index=2))
    debugging: CellConfig = field(default_factory=lambda: CellConfig(id='debugging', font_color=NOTES.font_color, bkg_color=NOTES.bkg_color, show=False, column_index=3))
    pace_notes: CellConfig = field(default_factory=lambda: CellConfig(id='pace_notes', font_color=NOTES.font_color, bkg_color=NOTES.bkg_color, column_index=1))
    pit_notes_while_in_pit: CellConfig = field(default_factory=lambda: CellConfig(id='pit_notes_while_in_pit'))

    # config
    auto_hide_if_not_available: bool = True
    comments_text_alignment: str = 'Center'
    comments_width: int = 30
    debugging_text_alignment: str = 'Center'
    debugging_width: int = 30
    enable_comments_line_break: bool = True
    maximum_display_duration: int = -1
    pace_notes_text_alignment: str = 'Center'
    pace_notes_width: int = 30
    pit_comments_text: str = ''
    pit_notes_text: str = 'Pit Lane'

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.background.to_flat())
        result.update(self.comments.to_flat())
        result.update(self.debugging.to_flat())
        result.update(self.pace_notes.to_flat())
        result.update(self.pit_notes_while_in_pit.to_flat())
        result["auto_hide_if_not_available"] = self.auto_hide_if_not_available
        result["comments_text_alignment"] = self.comments_text_alignment
        result["comments_width"] = self.comments_width
        result["debugging_text_alignment"] = self.debugging_text_alignment
        result["debugging_width"] = self.debugging_width
        result["enable_comments_line_break"] = self.enable_comments_line_break
        result["maximum_display_duration"] = self.maximum_display_duration
        result["pace_notes_text_alignment"] = self.pace_notes_text_alignment
        result["pace_notes_width"] = self.pace_notes_width
        result["pit_comments_text"] = self.pit_comments_text
        result["pit_notes_text"] = self.pit_notes_text
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "PaceNotes":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.background = CellConfig.from_flat(data, 'background')
        obj.comments = CellConfig.from_flat(data, 'comments')
        obj.debugging = CellConfig.from_flat(data, 'debugging')
        obj.pace_notes = CellConfig.from_flat(data, 'pace_notes')
        obj.pit_notes_while_in_pit = CellConfig.from_flat(data, 'pit_notes_while_in_pit')
        obj.auto_hide_if_not_available = data.get("auto_hide_if_not_available", obj.auto_hide_if_not_available)
        obj.comments_text_alignment = data.get("comments_text_alignment", obj.comments_text_alignment)
        obj.comments_width = data.get("comments_width", obj.comments_width)
        obj.debugging_text_alignment = data.get("debugging_text_alignment", obj.debugging_text_alignment)
        obj.debugging_width = data.get("debugging_width", obj.debugging_width)
        obj.enable_comments_line_break = data.get("enable_comments_line_break", obj.enable_comments_line_break)
        obj.maximum_display_duration = data.get("maximum_display_duration", obj.maximum_display_duration)
        obj.pace_notes_text_alignment = data.get("pace_notes_text_alignment", obj.pace_notes_text_alignment)
        obj.pace_notes_width = data.get("pace_notes_width", obj.pace_notes_width)
        obj.pit_comments_text = data.get("pit_comments_text", obj.pit_comments_text)
        obj.pit_notes_text = data.get("pit_notes_text", obj.pit_notes_text)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["background"] = self.background.to_dict()
        result["comments"] = self.comments.to_dict()
        result["debugging"] = self.debugging.to_dict()
        result["pace_notes"] = self.pace_notes.to_dict()
        result["pit_notes_while_in_pit"] = self.pit_notes_while_in_pit.to_dict()
        result["auto_hide_if_not_available"] = self.auto_hide_if_not_available
        result["comments_text_alignment"] = self.comments_text_alignment
        result["comments_width"] = self.comments_width
        result["debugging_text_alignment"] = self.debugging_text_alignment
        result["debugging_width"] = self.debugging_width
        result["enable_comments_line_break"] = self.enable_comments_line_break
        result["maximum_display_duration"] = self.maximum_display_duration
        result["pace_notes_text_alignment"] = self.pace_notes_text_alignment
        result["pace_notes_width"] = self.pace_notes_width
        result["pit_comments_text"] = self.pit_comments_text
        result["pit_notes_text"] = self.pit_notes_text
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PaceNotes":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.background = CellConfig.from_dict(data.get("background", {}), 'background')
        obj.comments = CellConfig.from_dict(data.get("comments", {}), 'comments')
        obj.debugging = CellConfig.from_dict(data.get("debugging", {}), 'debugging')
        obj.pace_notes = CellConfig.from_dict(data.get("pace_notes", {}), 'pace_notes')
        obj.pit_notes_while_in_pit = CellConfig.from_dict(data.get("pit_notes_while_in_pit", {}), 'pit_notes_while_in_pit')
        obj.auto_hide_if_not_available = data.get("auto_hide_if_not_available", obj.auto_hide_if_not_available)
        obj.comments_text_alignment = data.get("comments_text_alignment", obj.comments_text_alignment)
        obj.comments_width = data.get("comments_width", obj.comments_width)
        obj.debugging_text_alignment = data.get("debugging_text_alignment", obj.debugging_text_alignment)
        obj.debugging_width = data.get("debugging_width", obj.debugging_width)
        obj.enable_comments_line_break = data.get("enable_comments_line_break", obj.enable_comments_line_break)
        obj.maximum_display_duration = data.get("maximum_display_duration", obj.maximum_display_duration)
        obj.pace_notes_text_alignment = data.get("pace_notes_text_alignment", obj.pace_notes_text_alignment)
        obj.pace_notes_width = data.get("pace_notes_width", obj.pace_notes_width)
        obj.pit_comments_text = data.get("pit_comments_text", obj.pit_comments_text)
        obj.pit_notes_text = data.get("pit_notes_text", obj.pit_notes_text)
        return obj
