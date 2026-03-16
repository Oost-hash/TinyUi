# Auto-generated widget
# Widget: fuel

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import DATA, DATA_DIM, FUEL, INVERTED
from ..components import CaptionConfig, WarningFlashConfig


@dataclass
class Fuel(WidgetConfig):
    name: str = "fuel"

    # base overrides
    bar_gap: int = 0

    # groups
    bar: BarConfig = field(default_factory=lambda: BarConfig(bar_width=5))
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=57, position_y=208))

    # cells
    absolute_refuel: CellConfig = field(default_factory=lambda: CellConfig(id='absolute_refuel', caption_text='abfuel'))
    absolute_refueling: CellConfig = field(default_factory=lambda: CellConfig(id='absolute_refueling', show=False))
    delta: CellConfig = field(default_factory=lambda: CellConfig(id='delta', font_color=INVERTED.font_color, bkg_color=INVERTED.bkg_color, decimal_places=2, caption_text='delta'))
    delta_and_end_remaining: CellConfig = field(default_factory=lambda: CellConfig(id='delta_and_end_remaining'))
    early: CellConfig = field(default_factory=lambda: CellConfig(id='early', font_color=DATA.font_color, bkg_color=DATA.bkg_color, decimal_places=2, caption_text='early'))
    end: CellConfig = field(default_factory=lambda: CellConfig(id='end', font_color=DATA.font_color, bkg_color=DATA.bkg_color, decimal_places=2, caption_text='end'))
    estimated_pitstop_count: CellConfig = field(default_factory=lambda: CellConfig(id='estimated_pitstop_count'))
    fuel_level: CellConfig = field(default_factory=lambda: CellConfig(id='fuel_level'))
    fuel_level_bar: CellConfig = field(default_factory=lambda: CellConfig(id='fuel_level_bar'))
    laps: CellConfig = field(default_factory=lambda: CellConfig(id='laps', font_color=DATA_DIM.font_color, bkg_color=DATA_DIM.bkg_color, decimal_places=1, caption_text='laps'))
    lower: CellConfig = field(default_factory=lambda: CellConfig(id='lower', column_index=3))
    middle: CellConfig = field(default_factory=lambda: CellConfig(id='middle', column_index=2))
    minutes: CellConfig = field(default_factory=lambda: CellConfig(id='minutes', font_color=DATA_DIM.font_color, bkg_color=DATA_DIM.bkg_color, decimal_places=1, caption_text='mins'))
    pits: CellConfig = field(default_factory=lambda: CellConfig(id='pits', font_color=DATA.font_color, bkg_color=DATA.bkg_color, decimal_places=2, caption_text='pits'))
    refuel: CellConfig = field(default_factory=lambda: CellConfig(id='refuel', font_color=FUEL.font_color, bkg_color=FUEL.bkg_color, decimal_places=2, caption_text='refuel'))
    refueling_level_mark: CellConfig = field(default_factory=lambda: CellConfig(id='refueling_level_mark'))
    remain: CellConfig = field(default_factory=lambda: CellConfig(id='remain', font_color=FUEL.font_color, bkg_color=FUEL.bkg_color, decimal_places=2, caption_text='fuel'))
    save: CellConfig = field(default_factory=lambda: CellConfig(id='save', font_color=DATA.font_color, bkg_color=DATA.bkg_color, decimal_places=2, caption_text='save'))
    starting_fuel_level_mark: CellConfig = field(default_factory=lambda: CellConfig(id='starting_fuel_level_mark'))
    upper: CellConfig = field(default_factory=lambda: CellConfig(id='upper', column_index=1))
    used: CellConfig = field(default_factory=lambda: CellConfig(id='used', font_color=INVERTED.font_color, bkg_color=INVERTED.bkg_color, decimal_places=2, caption_text='used'))

    # components
    caption: CaptionConfig = field(default_factory=CaptionConfig)
    low_fuel_warning_flash: WarningFlashConfig = field(default_factory=lambda: WarningFlashConfig(interval=0.4))

    # config
    fuel_level_bar_height: int = 10
    highlight_color_fuel_level: str = '#FFFFFF'
    low_fuel_lap_threshold: int = 2
    refueling_level_mark_color: str = '#44FF00'
    refueling_level_mark_width: int = 3
    starting_fuel_level_mark_color: str = '#FF4400'
    starting_fuel_level_mark_width: int = 3
    swap_lower_caption: bool = False
    swap_upper_caption: bool = False
    warning_color_low_fuel: str = '#FF2200'

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["bar_gap"] = self.bar_gap
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.absolute_refuel.to_flat())
        result.update(self.absolute_refueling.to_flat())
        result.update(self.delta.to_flat())
        result.update(self.delta_and_end_remaining.to_flat())
        result.update(self.early.to_flat())
        result.update(self.end.to_flat())
        result.update(self.estimated_pitstop_count.to_flat())
        result.update(self.fuel_level.to_flat())
        result.update(self.fuel_level_bar.to_flat())
        result.update(self.laps.to_flat())
        result.update(self.lower.to_flat())
        result.update(self.middle.to_flat())
        result.update(self.minutes.to_flat())
        result.update(self.pits.to_flat())
        result.update(self.refuel.to_flat())
        result.update(self.refueling_level_mark.to_flat())
        result.update(self.remain.to_flat())
        result.update(self.save.to_flat())
        result.update(self.starting_fuel_level_mark.to_flat())
        result.update(self.upper.to_flat())
        result.update(self.used.to_flat())
        result["bkg_color_caption"] = self.caption.bkg_color
        result["font_color_caption"] = self.caption.font_color
        result["show_caption"] = self.caption.show
        result["number_of_warning_flashes"] = self.low_fuel_warning_flash.number_of_flashes
        result["show_low_fuel_warning_flash"] = self.low_fuel_warning_flash.enabled
        result["warning_flash_highlight_duration"] = self.low_fuel_warning_flash.highlight_duration
        result["warning_flash_interval"] = self.low_fuel_warning_flash.interval
        result["fuel_level_bar_height"] = self.fuel_level_bar_height
        result["highlight_color_fuel_level"] = self.highlight_color_fuel_level
        result["low_fuel_lap_threshold"] = self.low_fuel_lap_threshold
        result["refueling_level_mark_color"] = self.refueling_level_mark_color
        result["refueling_level_mark_width"] = self.refueling_level_mark_width
        result["starting_fuel_level_mark_color"] = self.starting_fuel_level_mark_color
        result["starting_fuel_level_mark_width"] = self.starting_fuel_level_mark_width
        result["swap_lower_caption"] = self.swap_lower_caption
        result["swap_upper_caption"] = self.swap_upper_caption
        result["warning_color_low_fuel"] = self.warning_color_low_fuel
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Fuel":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_gap = data.get("bar_gap", obj.bar_gap)
        obj.bar = BarConfig.from_flat(data)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.absolute_refuel = CellConfig.from_flat(data, 'absolute_refuel')
        obj.absolute_refueling = CellConfig.from_flat(data, 'absolute_refueling')
        obj.delta = CellConfig.from_flat(data, 'delta')
        obj.delta_and_end_remaining = CellConfig.from_flat(data, 'delta_and_end_remaining')
        obj.early = CellConfig.from_flat(data, 'early')
        obj.end = CellConfig.from_flat(data, 'end')
        obj.estimated_pitstop_count = CellConfig.from_flat(data, 'estimated_pitstop_count')
        obj.fuel_level = CellConfig.from_flat(data, 'fuel_level')
        obj.fuel_level_bar = CellConfig.from_flat(data, 'fuel_level_bar')
        obj.laps = CellConfig.from_flat(data, 'laps')
        obj.lower = CellConfig.from_flat(data, 'lower')
        obj.middle = CellConfig.from_flat(data, 'middle')
        obj.minutes = CellConfig.from_flat(data, 'minutes')
        obj.pits = CellConfig.from_flat(data, 'pits')
        obj.refuel = CellConfig.from_flat(data, 'refuel')
        obj.refueling_level_mark = CellConfig.from_flat(data, 'refueling_level_mark')
        obj.remain = CellConfig.from_flat(data, 'remain')
        obj.save = CellConfig.from_flat(data, 'save')
        obj.starting_fuel_level_mark = CellConfig.from_flat(data, 'starting_fuel_level_mark')
        obj.upper = CellConfig.from_flat(data, 'upper')
        obj.used = CellConfig.from_flat(data, 'used')
        obj.caption = CaptionConfig(
            bkg_color=data.get("bkg_color_caption", obj.caption.bkg_color),
            font_color=data.get("font_color_caption", obj.caption.font_color),
            show=data.get("show_caption", obj.caption.show),
        )
        obj.low_fuel_warning_flash = WarningFlashConfig(
            number_of_flashes=data.get("number_of_warning_flashes", obj.low_fuel_warning_flash.number_of_flashes),
            enabled=data.get("show_low_fuel_warning_flash", obj.low_fuel_warning_flash.enabled),
            highlight_duration=data.get("warning_flash_highlight_duration", obj.low_fuel_warning_flash.highlight_duration),
            interval=data.get("warning_flash_interval", obj.low_fuel_warning_flash.interval),
        )
        obj.fuel_level_bar_height = data.get("fuel_level_bar_height", obj.fuel_level_bar_height)
        obj.highlight_color_fuel_level = data.get("highlight_color_fuel_level", obj.highlight_color_fuel_level)
        obj.low_fuel_lap_threshold = data.get("low_fuel_lap_threshold", obj.low_fuel_lap_threshold)
        obj.refueling_level_mark_color = data.get("refueling_level_mark_color", obj.refueling_level_mark_color)
        obj.refueling_level_mark_width = data.get("refueling_level_mark_width", obj.refueling_level_mark_width)
        obj.starting_fuel_level_mark_color = data.get("starting_fuel_level_mark_color", obj.starting_fuel_level_mark_color)
        obj.starting_fuel_level_mark_width = data.get("starting_fuel_level_mark_width", obj.starting_fuel_level_mark_width)
        obj.swap_lower_caption = data.get("swap_lower_caption", obj.swap_lower_caption)
        obj.swap_upper_caption = data.get("swap_upper_caption", obj.swap_upper_caption)
        obj.warning_color_low_fuel = data.get("warning_color_low_fuel", obj.warning_color_low_fuel)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar_gap"] = self.bar_gap
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["absolute_refuel"] = self.absolute_refuel.to_dict()
        result["absolute_refueling"] = self.absolute_refueling.to_dict()
        result["delta"] = self.delta.to_dict()
        result["delta_and_end_remaining"] = self.delta_and_end_remaining.to_dict()
        result["early"] = self.early.to_dict()
        result["end"] = self.end.to_dict()
        result["estimated_pitstop_count"] = self.estimated_pitstop_count.to_dict()
        result["fuel_level"] = self.fuel_level.to_dict()
        result["fuel_level_bar"] = self.fuel_level_bar.to_dict()
        result["laps"] = self.laps.to_dict()
        result["lower"] = self.lower.to_dict()
        result["middle"] = self.middle.to_dict()
        result["minutes"] = self.minutes.to_dict()
        result["pits"] = self.pits.to_dict()
        result["refuel"] = self.refuel.to_dict()
        result["refueling_level_mark"] = self.refueling_level_mark.to_dict()
        result["remain"] = self.remain.to_dict()
        result["save"] = self.save.to_dict()
        result["starting_fuel_level_mark"] = self.starting_fuel_level_mark.to_dict()
        result["upper"] = self.upper.to_dict()
        result["used"] = self.used.to_dict()
        result["caption"] = self.caption.to_dict()
        result["low_fuel_warning_flash"] = self.low_fuel_warning_flash.to_dict()
        result["fuel_level_bar_height"] = self.fuel_level_bar_height
        result["highlight_color_fuel_level"] = self.highlight_color_fuel_level
        result["low_fuel_lap_threshold"] = self.low_fuel_lap_threshold
        result["refueling_level_mark_color"] = self.refueling_level_mark_color
        result["refueling_level_mark_width"] = self.refueling_level_mark_width
        result["starting_fuel_level_mark_color"] = self.starting_fuel_level_mark_color
        result["starting_fuel_level_mark_width"] = self.starting_fuel_level_mark_width
        result["swap_lower_caption"] = self.swap_lower_caption
        result["swap_upper_caption"] = self.swap_upper_caption
        result["warning_color_low_fuel"] = self.warning_color_low_fuel
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Fuel":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_gap = data.get("bar_gap", obj.bar_gap)
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.absolute_refuel = CellConfig.from_dict(data.get("absolute_refuel", {}), 'absolute_refuel')
        obj.absolute_refueling = CellConfig.from_dict(data.get("absolute_refueling", {}), 'absolute_refueling')
        obj.delta = CellConfig.from_dict(data.get("delta", {}), 'delta')
        obj.delta_and_end_remaining = CellConfig.from_dict(data.get("delta_and_end_remaining", {}), 'delta_and_end_remaining')
        obj.early = CellConfig.from_dict(data.get("early", {}), 'early')
        obj.end = CellConfig.from_dict(data.get("end", {}), 'end')
        obj.estimated_pitstop_count = CellConfig.from_dict(data.get("estimated_pitstop_count", {}), 'estimated_pitstop_count')
        obj.fuel_level = CellConfig.from_dict(data.get("fuel_level", {}), 'fuel_level')
        obj.fuel_level_bar = CellConfig.from_dict(data.get("fuel_level_bar", {}), 'fuel_level_bar')
        obj.laps = CellConfig.from_dict(data.get("laps", {}), 'laps')
        obj.lower = CellConfig.from_dict(data.get("lower", {}), 'lower')
        obj.middle = CellConfig.from_dict(data.get("middle", {}), 'middle')
        obj.minutes = CellConfig.from_dict(data.get("minutes", {}), 'minutes')
        obj.pits = CellConfig.from_dict(data.get("pits", {}), 'pits')
        obj.refuel = CellConfig.from_dict(data.get("refuel", {}), 'refuel')
        obj.refueling_level_mark = CellConfig.from_dict(data.get("refueling_level_mark", {}), 'refueling_level_mark')
        obj.remain = CellConfig.from_dict(data.get("remain", {}), 'remain')
        obj.save = CellConfig.from_dict(data.get("save", {}), 'save')
        obj.starting_fuel_level_mark = CellConfig.from_dict(data.get("starting_fuel_level_mark", {}), 'starting_fuel_level_mark')
        obj.upper = CellConfig.from_dict(data.get("upper", {}), 'upper')
        obj.used = CellConfig.from_dict(data.get("used", {}), 'used')
        obj.caption = CaptionConfig.from_dict(data.get("caption", {}))
        obj.low_fuel_warning_flash = WarningFlashConfig.from_dict(data.get("low_fuel_warning_flash", {}))
        obj.fuel_level_bar_height = data.get("fuel_level_bar_height", obj.fuel_level_bar_height)
        obj.highlight_color_fuel_level = data.get("highlight_color_fuel_level", obj.highlight_color_fuel_level)
        obj.low_fuel_lap_threshold = data.get("low_fuel_lap_threshold", obj.low_fuel_lap_threshold)
        obj.refueling_level_mark_color = data.get("refueling_level_mark_color", obj.refueling_level_mark_color)
        obj.refueling_level_mark_width = data.get("refueling_level_mark_width", obj.refueling_level_mark_width)
        obj.starting_fuel_level_mark_color = data.get("starting_fuel_level_mark_color", obj.starting_fuel_level_mark_color)
        obj.starting_fuel_level_mark_width = data.get("starting_fuel_level_mark_width", obj.starting_fuel_level_mark_width)
        obj.swap_lower_caption = data.get("swap_lower_caption", obj.swap_lower_caption)
        obj.swap_upper_caption = data.get("swap_upper_caption", obj.swap_upper_caption)
        obj.warning_color_low_fuel = data.get("warning_color_low_fuel", obj.warning_color_low_fuel)
        return obj
