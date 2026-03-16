# Auto-generated widget
# Widget: virtual_energy

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import DATA, DATA_DIM, ENERGY, INVERTED
from ..components import CaptionConfig, WarningFlashConfig


@dataclass
class VirtualEnergy(WidgetConfig):
    name: str = "virtual_energy"

    # base overrides
    bar_gap: int = 0

    # groups
    bar: BarConfig = field(default_factory=lambda: BarConfig(bar_width=5))
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=115, position_y=824))

    # cells
    absolute_refill: CellConfig = field(default_factory=lambda: CellConfig(id='absolute_refill', caption_text='abfill'))
    absolute_refilling: CellConfig = field(default_factory=lambda: CellConfig(id='absolute_refilling', show=False))
    bias: CellConfig = field(default_factory=lambda: CellConfig(id='bias', font_color=DATA.font_color, bkg_color=DATA.bkg_color, decimal_places=2, caption_text='bias'))
    delta: CellConfig = field(default_factory=lambda: CellConfig(id='delta', font_color=INVERTED.font_color, bkg_color=INVERTED.bkg_color, decimal_places=2, caption_text='delta'))
    delta_and_end_remaining: CellConfig = field(default_factory=lambda: CellConfig(id='delta_and_end_remaining'))
    early: CellConfig = field(default_factory=lambda: CellConfig(id='early', font_color=DATA.font_color, bkg_color=DATA.bkg_color, decimal_places=2, caption_text='early'))
    end: CellConfig = field(default_factory=lambda: CellConfig(id='end', font_color=DATA.font_color, bkg_color=DATA.bkg_color, decimal_places=2, caption_text='end'))
    energy_level: CellConfig = field(default_factory=lambda: CellConfig(id='energy_level'))
    energy_level_bar: CellConfig = field(default_factory=lambda: CellConfig(id='energy_level_bar'))
    estimated_pitstop_count: CellConfig = field(default_factory=lambda: CellConfig(id='estimated_pitstop_count'))
    fuel_ratio_and_bias: CellConfig = field(default_factory=lambda: CellConfig(id='fuel_ratio_and_bias'))
    laps: CellConfig = field(default_factory=lambda: CellConfig(id='laps', font_color=DATA_DIM.font_color, bkg_color=DATA_DIM.bkg_color, decimal_places=1, caption_text='laps'))
    lower: CellConfig = field(default_factory=lambda: CellConfig(id='lower', column_index=3))
    middle: CellConfig = field(default_factory=lambda: CellConfig(id='middle', column_index=2))
    minutes: CellConfig = field(default_factory=lambda: CellConfig(id='minutes', font_color=DATA_DIM.font_color, bkg_color=DATA_DIM.bkg_color, decimal_places=1, caption_text='mins'))
    pits: CellConfig = field(default_factory=lambda: CellConfig(id='pits', font_color=DATA.font_color, bkg_color=DATA.bkg_color, decimal_places=2, caption_text='pits'))
    ratio: CellConfig = field(default_factory=lambda: CellConfig(id='ratio', font_color=INVERTED.font_color, bkg_color=INVERTED.bkg_color, decimal_places=3, caption_text='ratio'))
    refill: CellConfig = field(default_factory=lambda: CellConfig(id='refill', font_color=ENERGY.font_color, bkg_color=ENERGY.bkg_color, decimal_places=2, caption_text='refill'))
    refilling_level_mark: CellConfig = field(default_factory=lambda: CellConfig(id='refilling_level_mark'))
    remain: CellConfig = field(default_factory=lambda: CellConfig(id='remain', font_color=ENERGY.font_color, bkg_color=ENERGY.bkg_color, decimal_places=2, caption_text='energy'))
    save: CellConfig = field(default_factory=lambda: CellConfig(id='save', font_color=DATA.font_color, bkg_color=DATA.bkg_color, decimal_places=2, caption_text='save'))
    starting_energy_level_mark: CellConfig = field(default_factory=lambda: CellConfig(id='starting_energy_level_mark'))
    upper: CellConfig = field(default_factory=lambda: CellConfig(id='upper', column_index=1))
    used: CellConfig = field(default_factory=lambda: CellConfig(id='used', font_color=INVERTED.font_color, bkg_color=INVERTED.bkg_color, decimal_places=2, caption_text='used'))

    # components
    caption: CaptionConfig = field(default_factory=CaptionConfig)
    low_energy_warning_flash: WarningFlashConfig = field(default_factory=lambda: WarningFlashConfig(interval=0.4))

    # config
    energy_level_bar_height: int = 10
    highlight_color_energy_level: str = '#FFFFFF'
    low_energy_lap_threshold: int = 2
    refilling_level_mark_color: str = '#44FF00'
    refilling_level_mark_width: int = 3
    starting_energy_level_mark_color: str = '#FF4400'
    starting_energy_level_mark_width: int = 3
    swap_lower_caption: bool = False
    swap_upper_caption: bool = False
    warning_color_low_energy: str = '#FF22FF'

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["bar_gap"] = self.bar_gap
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.absolute_refill.to_flat())
        result.update(self.absolute_refilling.to_flat())
        result.update(self.bias.to_flat())
        result.update(self.delta.to_flat())
        result.update(self.delta_and_end_remaining.to_flat())
        result.update(self.early.to_flat())
        result.update(self.end.to_flat())
        result.update(self.energy_level.to_flat())
        result.update(self.energy_level_bar.to_flat())
        result.update(self.estimated_pitstop_count.to_flat())
        result.update(self.fuel_ratio_and_bias.to_flat())
        result.update(self.laps.to_flat())
        result.update(self.lower.to_flat())
        result.update(self.middle.to_flat())
        result.update(self.minutes.to_flat())
        result.update(self.pits.to_flat())
        result.update(self.ratio.to_flat())
        result.update(self.refill.to_flat())
        result.update(self.refilling_level_mark.to_flat())
        result.update(self.remain.to_flat())
        result.update(self.save.to_flat())
        result.update(self.starting_energy_level_mark.to_flat())
        result.update(self.upper.to_flat())
        result.update(self.used.to_flat())
        result["bkg_color_caption"] = self.caption.bkg_color
        result["font_color_caption"] = self.caption.font_color
        result["show_caption"] = self.caption.show
        result["number_of_warning_flashes"] = self.low_energy_warning_flash.number_of_flashes
        result["show_low_energy_warning_flash"] = self.low_energy_warning_flash.enabled
        result["warning_flash_highlight_duration"] = self.low_energy_warning_flash.highlight_duration
        result["warning_flash_interval"] = self.low_energy_warning_flash.interval
        result["energy_level_bar_height"] = self.energy_level_bar_height
        result["highlight_color_energy_level"] = self.highlight_color_energy_level
        result["low_energy_lap_threshold"] = self.low_energy_lap_threshold
        result["refilling_level_mark_color"] = self.refilling_level_mark_color
        result["refilling_level_mark_width"] = self.refilling_level_mark_width
        result["starting_energy_level_mark_color"] = self.starting_energy_level_mark_color
        result["starting_energy_level_mark_width"] = self.starting_energy_level_mark_width
        result["swap_lower_caption"] = self.swap_lower_caption
        result["swap_upper_caption"] = self.swap_upper_caption
        result["warning_color_low_energy"] = self.warning_color_low_energy
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "VirtualEnergy":
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
        obj.absolute_refill = CellConfig.from_flat(data, 'absolute_refill')
        obj.absolute_refilling = CellConfig.from_flat(data, 'absolute_refilling')
        obj.bias = CellConfig.from_flat(data, 'bias')
        obj.delta = CellConfig.from_flat(data, 'delta')
        obj.delta_and_end_remaining = CellConfig.from_flat(data, 'delta_and_end_remaining')
        obj.early = CellConfig.from_flat(data, 'early')
        obj.end = CellConfig.from_flat(data, 'end')
        obj.energy_level = CellConfig.from_flat(data, 'energy_level')
        obj.energy_level_bar = CellConfig.from_flat(data, 'energy_level_bar')
        obj.estimated_pitstop_count = CellConfig.from_flat(data, 'estimated_pitstop_count')
        obj.fuel_ratio_and_bias = CellConfig.from_flat(data, 'fuel_ratio_and_bias')
        obj.laps = CellConfig.from_flat(data, 'laps')
        obj.lower = CellConfig.from_flat(data, 'lower')
        obj.middle = CellConfig.from_flat(data, 'middle')
        obj.minutes = CellConfig.from_flat(data, 'minutes')
        obj.pits = CellConfig.from_flat(data, 'pits')
        obj.ratio = CellConfig.from_flat(data, 'ratio')
        obj.refill = CellConfig.from_flat(data, 'refill')
        obj.refilling_level_mark = CellConfig.from_flat(data, 'refilling_level_mark')
        obj.remain = CellConfig.from_flat(data, 'remain')
        obj.save = CellConfig.from_flat(data, 'save')
        obj.starting_energy_level_mark = CellConfig.from_flat(data, 'starting_energy_level_mark')
        obj.upper = CellConfig.from_flat(data, 'upper')
        obj.used = CellConfig.from_flat(data, 'used')
        obj.caption = CaptionConfig(
            bkg_color=data.get("bkg_color_caption", obj.caption.bkg_color),
            font_color=data.get("font_color_caption", obj.caption.font_color),
            show=data.get("show_caption", obj.caption.show),
        )
        obj.low_energy_warning_flash = WarningFlashConfig(
            number_of_flashes=data.get("number_of_warning_flashes", obj.low_energy_warning_flash.number_of_flashes),
            enabled=data.get("show_low_energy_warning_flash", obj.low_energy_warning_flash.enabled),
            highlight_duration=data.get("warning_flash_highlight_duration", obj.low_energy_warning_flash.highlight_duration),
            interval=data.get("warning_flash_interval", obj.low_energy_warning_flash.interval),
        )
        obj.energy_level_bar_height = data.get("energy_level_bar_height", obj.energy_level_bar_height)
        obj.highlight_color_energy_level = data.get("highlight_color_energy_level", obj.highlight_color_energy_level)
        obj.low_energy_lap_threshold = data.get("low_energy_lap_threshold", obj.low_energy_lap_threshold)
        obj.refilling_level_mark_color = data.get("refilling_level_mark_color", obj.refilling_level_mark_color)
        obj.refilling_level_mark_width = data.get("refilling_level_mark_width", obj.refilling_level_mark_width)
        obj.starting_energy_level_mark_color = data.get("starting_energy_level_mark_color", obj.starting_energy_level_mark_color)
        obj.starting_energy_level_mark_width = data.get("starting_energy_level_mark_width", obj.starting_energy_level_mark_width)
        obj.swap_lower_caption = data.get("swap_lower_caption", obj.swap_lower_caption)
        obj.swap_upper_caption = data.get("swap_upper_caption", obj.swap_upper_caption)
        obj.warning_color_low_energy = data.get("warning_color_low_energy", obj.warning_color_low_energy)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar_gap"] = self.bar_gap
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["absolute_refill"] = self.absolute_refill.to_dict()
        result["absolute_refilling"] = self.absolute_refilling.to_dict()
        result["bias"] = self.bias.to_dict()
        result["delta"] = self.delta.to_dict()
        result["delta_and_end_remaining"] = self.delta_and_end_remaining.to_dict()
        result["early"] = self.early.to_dict()
        result["end"] = self.end.to_dict()
        result["energy_level"] = self.energy_level.to_dict()
        result["energy_level_bar"] = self.energy_level_bar.to_dict()
        result["estimated_pitstop_count"] = self.estimated_pitstop_count.to_dict()
        result["fuel_ratio_and_bias"] = self.fuel_ratio_and_bias.to_dict()
        result["laps"] = self.laps.to_dict()
        result["lower"] = self.lower.to_dict()
        result["middle"] = self.middle.to_dict()
        result["minutes"] = self.minutes.to_dict()
        result["pits"] = self.pits.to_dict()
        result["ratio"] = self.ratio.to_dict()
        result["refill"] = self.refill.to_dict()
        result["refilling_level_mark"] = self.refilling_level_mark.to_dict()
        result["remain"] = self.remain.to_dict()
        result["save"] = self.save.to_dict()
        result["starting_energy_level_mark"] = self.starting_energy_level_mark.to_dict()
        result["upper"] = self.upper.to_dict()
        result["used"] = self.used.to_dict()
        result["caption"] = self.caption.to_dict()
        result["low_energy_warning_flash"] = self.low_energy_warning_flash.to_dict()
        result["energy_level_bar_height"] = self.energy_level_bar_height
        result["highlight_color_energy_level"] = self.highlight_color_energy_level
        result["low_energy_lap_threshold"] = self.low_energy_lap_threshold
        result["refilling_level_mark_color"] = self.refilling_level_mark_color
        result["refilling_level_mark_width"] = self.refilling_level_mark_width
        result["starting_energy_level_mark_color"] = self.starting_energy_level_mark_color
        result["starting_energy_level_mark_width"] = self.starting_energy_level_mark_width
        result["swap_lower_caption"] = self.swap_lower_caption
        result["swap_upper_caption"] = self.swap_upper_caption
        result["warning_color_low_energy"] = self.warning_color_low_energy
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VirtualEnergy":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_gap = data.get("bar_gap", obj.bar_gap)
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.absolute_refill = CellConfig.from_dict(data.get("absolute_refill", {}), 'absolute_refill')
        obj.absolute_refilling = CellConfig.from_dict(data.get("absolute_refilling", {}), 'absolute_refilling')
        obj.bias = CellConfig.from_dict(data.get("bias", {}), 'bias')
        obj.delta = CellConfig.from_dict(data.get("delta", {}), 'delta')
        obj.delta_and_end_remaining = CellConfig.from_dict(data.get("delta_and_end_remaining", {}), 'delta_and_end_remaining')
        obj.early = CellConfig.from_dict(data.get("early", {}), 'early')
        obj.end = CellConfig.from_dict(data.get("end", {}), 'end')
        obj.energy_level = CellConfig.from_dict(data.get("energy_level", {}), 'energy_level')
        obj.energy_level_bar = CellConfig.from_dict(data.get("energy_level_bar", {}), 'energy_level_bar')
        obj.estimated_pitstop_count = CellConfig.from_dict(data.get("estimated_pitstop_count", {}), 'estimated_pitstop_count')
        obj.fuel_ratio_and_bias = CellConfig.from_dict(data.get("fuel_ratio_and_bias", {}), 'fuel_ratio_and_bias')
        obj.laps = CellConfig.from_dict(data.get("laps", {}), 'laps')
        obj.lower = CellConfig.from_dict(data.get("lower", {}), 'lower')
        obj.middle = CellConfig.from_dict(data.get("middle", {}), 'middle')
        obj.minutes = CellConfig.from_dict(data.get("minutes", {}), 'minutes')
        obj.pits = CellConfig.from_dict(data.get("pits", {}), 'pits')
        obj.ratio = CellConfig.from_dict(data.get("ratio", {}), 'ratio')
        obj.refill = CellConfig.from_dict(data.get("refill", {}), 'refill')
        obj.refilling_level_mark = CellConfig.from_dict(data.get("refilling_level_mark", {}), 'refilling_level_mark')
        obj.remain = CellConfig.from_dict(data.get("remain", {}), 'remain')
        obj.save = CellConfig.from_dict(data.get("save", {}), 'save')
        obj.starting_energy_level_mark = CellConfig.from_dict(data.get("starting_energy_level_mark", {}), 'starting_energy_level_mark')
        obj.upper = CellConfig.from_dict(data.get("upper", {}), 'upper')
        obj.used = CellConfig.from_dict(data.get("used", {}), 'used')
        obj.caption = CaptionConfig.from_dict(data.get("caption", {}))
        obj.low_energy_warning_flash = WarningFlashConfig.from_dict(data.get("low_energy_warning_flash", {}))
        obj.energy_level_bar_height = data.get("energy_level_bar_height", obj.energy_level_bar_height)
        obj.highlight_color_energy_level = data.get("highlight_color_energy_level", obj.highlight_color_energy_level)
        obj.low_energy_lap_threshold = data.get("low_energy_lap_threshold", obj.low_energy_lap_threshold)
        obj.refilling_level_mark_color = data.get("refilling_level_mark_color", obj.refilling_level_mark_color)
        obj.refilling_level_mark_width = data.get("refilling_level_mark_width", obj.refilling_level_mark_width)
        obj.starting_energy_level_mark_color = data.get("starting_energy_level_mark_color", obj.starting_energy_level_mark_color)
        obj.starting_energy_level_mark_width = data.get("starting_energy_level_mark_width", obj.starting_energy_level_mark_width)
        obj.swap_lower_caption = data.get("swap_lower_caption", obj.swap_lower_caption)
        obj.swap_upper_caption = data.get("swap_upper_caption", obj.swap_upper_caption)
        obj.warning_color_low_energy = data.get("warning_color_low_energy", obj.warning_color_low_energy)
        return obj
