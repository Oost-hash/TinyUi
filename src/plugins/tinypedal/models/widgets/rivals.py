# Auto-generated widget
# Widget: rivals

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, WidgetConfig
from ..colors import AMBER, CLASS_POSITION, CYAN, GAIN, GARAGE, LIME, LIME_DARK, LOSS, ORANGE, ORANGE_DARK, PENALTY, PIT, PIT_REQUEST, READING, RED, SUBTLE, TABLE_DIM, TABLE_HEADER, TABLE_ROW, YELLOW_FLAG


@dataclass
class Rivals(WidgetConfig):
    name: str = "rivals"

    # base overrides
    bar_gap: int = 1
    position_x: int = 433
    position_y: int = 688
    update_interval: int = 50

    # groups
    font: FontConfig = field(default_factory=FontConfig)

    # cells
    best_laptime: CellConfig = field(default_factory=lambda: CellConfig(id='best_laptime', font_color=TABLE_ROW.font_color, bkg_color=TABLE_ROW.bkg_color, show=False, column_index=11))
    best_laptime_from_recent_laps_in_race: CellConfig = field(default_factory=lambda: CellConfig(id='best_laptime_from_recent_laps_in_race', show=False))
    brand_logo: CellConfig = field(default_factory=lambda: CellConfig(id='brand_logo', show=False, column_index=8))
    class_: CellConfig = field(default_factory=lambda: CellConfig(id='class', font_color=TABLE_HEADER.font_color, bkg_color=TABLE_HEADER.bkg_color, column_index=5))
    class_style_for_position_in_class: CellConfig = field(default_factory=lambda: CellConfig(id='class_style_for_position_in_class', show=False))
    delta_laptime: CellConfig = field(default_factory=lambda: CellConfig(id='delta_laptime', font_color=READING.font_color, bkg_color=READING.bkg_color, show=False, column_index=18))
    delta_laptime_gain: CellConfig = field(default_factory=lambda: CellConfig(id='delta_laptime_gain', font_color=LIME_DARK.font_color, bkg_color=LIME_DARK.bkg_color))
    delta_laptime_loss: CellConfig = field(default_factory=lambda: CellConfig(id='delta_laptime_loss', font_color=ORANGE_DARK.font_color, bkg_color=ORANGE_DARK.bkg_color))
    driver: CellConfig = field(default_factory=lambda: CellConfig(id='driver', column_index=2))
    driver_name: CellConfig = field(default_factory=lambda: CellConfig(id='driver_name'))
    energy_remaining: CellConfig = field(default_factory=lambda: CellConfig(id='energy_remaining', font_color=SUBTLE.font_color, bkg_color=SUBTLE.bkg_color, column_index=20))
    energy_remaining_critical: CellConfig = field(default_factory=lambda: CellConfig(id='energy_remaining_critical', font_color=RED.font_color, bkg_color=RED.bkg_color))
    energy_remaining_high: CellConfig = field(default_factory=lambda: CellConfig(id='energy_remaining_high', font_color=LIME.font_color, bkg_color=LIME.bkg_color))
    energy_remaining_low: CellConfig = field(default_factory=lambda: CellConfig(id='energy_remaining_low', font_color=AMBER.font_color, bkg_color=AMBER.bkg_color))
    energy_remaining_unavailable: CellConfig = field(default_factory=lambda: CellConfig(id='energy_remaining_unavailable', font_color=READING.font_color, bkg_color=READING.bkg_color))
    garage: CellConfig = field(default_factory=lambda: CellConfig(id='garage', font_color=GARAGE.font_color, bkg_color=GARAGE.bkg_color))
    inverted_delta_laptime_layout: CellConfig = field(default_factory=lambda: CellConfig(id='inverted_delta_laptime_layout', show=False))
    laptime: CellConfig = field(default_factory=lambda: CellConfig(id='laptime', font_color=TABLE_ROW.font_color, bkg_color=TABLE_ROW.bkg_color, column_index=3))
    penalty_count: CellConfig = field(default_factory=lambda: CellConfig(id='penalty_count', font_color=PENALTY.font_color, bkg_color=PENALTY.bkg_color))
    pit: CellConfig = field(default_factory=lambda: CellConfig(id='pit', font_color=PIT.font_color, bkg_color=PIT.bkg_color))
    pit_request: CellConfig = field(default_factory=lambda: CellConfig(id='pit_request', font_color=PIT_REQUEST.font_color, bkg_color=PIT_REQUEST.bkg_color))
    pit_status: CellConfig = field(default_factory=lambda: CellConfig(id='pit_status'))
    pitstatus: CellConfig = field(default_factory=lambda: CellConfig(id='pitstatus', column_index=22))
    pitstop_count: CellConfig = field(default_factory=lambda: CellConfig(id='pitstop_count', font_color=TABLE_DIM.font_color, bkg_color=TABLE_DIM.bkg_color, column_index=10))
    pitstop_duration_while_requested_pitstop: CellConfig = field(default_factory=lambda: CellConfig(id='pitstop_duration_while_requested_pitstop'))
    position: CellConfig = field(default_factory=lambda: CellConfig(id='position', font_color=TABLE_HEADER.font_color, bkg_color=TABLE_HEADER.bkg_color, column_index=1))
    position_change: CellConfig = field(default_factory=lambda: CellConfig(id='position_change', column_index=12))
    position_change_in_class: CellConfig = field(default_factory=lambda: CellConfig(id='position_change_in_class'))
    position_gain: CellConfig = field(default_factory=lambda: CellConfig(id='position_gain', font_color=GAIN.font_color, bkg_color=GAIN.bkg_color))
    position_in_class: CellConfig = field(default_factory=lambda: CellConfig(id='position_in_class', font_color=CLASS_POSITION.font_color, bkg_color=CLASS_POSITION.bkg_color, column_index=4))
    position_loss: CellConfig = field(default_factory=lambda: CellConfig(id='position_loss', font_color=LOSS.font_color, bkg_color=LOSS.bkg_color))
    position_same: CellConfig = field(default_factory=lambda: CellConfig(id='position_same', font_color=TABLE_DIM.font_color, bkg_color=TABLE_DIM.bkg_color))
    speed_trap: CellConfig = field(default_factory=lambda: CellConfig(id='speed_trap', font_color=TABLE_ROW.font_color, bkg_color=TABLE_ROW.bkg_color, column_index=19))
    stint_laps: CellConfig = field(default_factory=lambda: CellConfig(id='stint_laps', font_color=TABLE_DIM.font_color, bkg_color=TABLE_DIM.bkg_color, column_index=16))
    time_interval: CellConfig = field(default_factory=lambda: CellConfig(id='time_interval'))
    time_interval_ahead: CellConfig = field(default_factory=lambda: CellConfig(id='time_interval_ahead', font_color='#66FF00'))
    time_interval_behind: CellConfig = field(default_factory=lambda: CellConfig(id='time_interval_behind', font_color=ORANGE.font_color, bkg_color=ORANGE.bkg_color))
    timeinterval: CellConfig = field(default_factory=lambda: CellConfig(id='timeinterval', column_index=13))
    tyre_compound: CellConfig = field(default_factory=lambda: CellConfig(id='tyre_compound', font_color=TABLE_ROW.font_color, bkg_color=TABLE_ROW.bkg_color, column_index=7))
    vehicle: CellConfig = field(default_factory=lambda: CellConfig(id='vehicle', column_index=6))
    vehicle_brand_as_name: CellConfig = field(default_factory=lambda: CellConfig(id='vehicle_brand_as_name'))
    vehicle_integrity: CellConfig = field(default_factory=lambda: CellConfig(id='vehicle_integrity', font_color=SUBTLE.font_color, bkg_color=SUBTLE.bkg_color, column_index=17))
    vehicle_integrity_full: CellConfig = field(default_factory=lambda: CellConfig(id='vehicle_integrity_full', font_color=READING.font_color, bkg_color=READING.bkg_color))
    vehicle_integrity_high: CellConfig = field(default_factory=lambda: CellConfig(id='vehicle_integrity_high', font_color=CYAN.font_color, bkg_color=CYAN.bkg_color))
    vehicle_integrity_low: CellConfig = field(default_factory=lambda: CellConfig(id='vehicle_integrity_low', font_color=RED.font_color, bkg_color=RED.bkg_color))
    vehicle_name: CellConfig = field(default_factory=lambda: CellConfig(id='vehicle_name', show=False))
    yellow_flag: CellConfig = field(default_factory=lambda: CellConfig(id='yellow_flag', font_color=YELLOW_FLAG.font_color, bkg_color=YELLOW_FLAG.bkg_color))

    # config
    brand_logo_width: int = 20
    class_width: int = 4
    driver_name_align_center: bool = False
    driver_name_shorten: bool = False
    driver_name_uppercase: bool = False
    driver_name_width: int = 10
    energy_remaining_decimal_places: int = 0
    garage_status_text: str = 'G'
    number_of_delta_laptime: int = 3
    pit_status_text: str = 'P'
    time_interval_align_center: bool = False
    time_interval_decimal_places: int = 3
    time_interval_width: int = 7
    vehicle_name_align_center: bool = False
    vehicle_name_uppercase: bool = False
    vehicle_name_width: int = 10
    yellow_flag_status_text: str = 'Y'

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["bar_gap"] = self.bar_gap
        result["position_x"] = self.position_x
        result["position_y"] = self.position_y
        result["update_interval"] = self.update_interval
        result.update(self.font.to_flat())
        result.update(self.best_laptime.to_flat())
        result.update(self.best_laptime_from_recent_laps_in_race.to_flat())
        result.update(self.brand_logo.to_flat())
        result.update(self.class_.to_flat())
        result.update(self.class_style_for_position_in_class.to_flat())
        result.update(self.delta_laptime.to_flat())
        result.update(self.delta_laptime_gain.to_flat())
        result.update(self.delta_laptime_loss.to_flat())
        result.update(self.driver.to_flat())
        result.update(self.driver_name.to_flat())
        result.update(self.energy_remaining.to_flat())
        result.update(self.energy_remaining_critical.to_flat())
        result.update(self.energy_remaining_high.to_flat())
        result.update(self.energy_remaining_low.to_flat())
        result.update(self.energy_remaining_unavailable.to_flat())
        result.update(self.garage.to_flat())
        result.update(self.inverted_delta_laptime_layout.to_flat())
        result.update(self.laptime.to_flat())
        result.update(self.penalty_count.to_flat())
        result.update(self.pit.to_flat())
        result.update(self.pit_request.to_flat())
        result.update(self.pit_status.to_flat())
        result.update(self.pitstatus.to_flat())
        result.update(self.pitstop_count.to_flat())
        result.update(self.pitstop_duration_while_requested_pitstop.to_flat())
        result.update(self.position.to_flat())
        result.update(self.position_change.to_flat())
        result.update(self.position_change_in_class.to_flat())
        result.update(self.position_gain.to_flat())
        result.update(self.position_in_class.to_flat())
        result.update(self.position_loss.to_flat())
        result.update(self.position_same.to_flat())
        result.update(self.speed_trap.to_flat())
        result.update(self.stint_laps.to_flat())
        result.update(self.time_interval.to_flat())
        result.update(self.time_interval_ahead.to_flat())
        result.update(self.time_interval_behind.to_flat())
        result.update(self.timeinterval.to_flat())
        result.update(self.tyre_compound.to_flat())
        result.update(self.vehicle.to_flat())
        result.update(self.vehicle_brand_as_name.to_flat())
        result.update(self.vehicle_integrity.to_flat())
        result.update(self.vehicle_integrity_full.to_flat())
        result.update(self.vehicle_integrity_high.to_flat())
        result.update(self.vehicle_integrity_low.to_flat())
        result.update(self.vehicle_name.to_flat())
        result.update(self.yellow_flag.to_flat())
        result["brand_logo_width"] = self.brand_logo_width
        result["class_width"] = self.class_width
        result["driver_name_align_center"] = self.driver_name_align_center
        result["driver_name_shorten"] = self.driver_name_shorten
        result["driver_name_uppercase"] = self.driver_name_uppercase
        result["driver_name_width"] = self.driver_name_width
        result["energy_remaining_decimal_places"] = self.energy_remaining_decimal_places
        result["garage_status_text"] = self.garage_status_text
        result["number_of_delta_laptime"] = self.number_of_delta_laptime
        result["pit_status_text"] = self.pit_status_text
        result["time_interval_align_center"] = self.time_interval_align_center
        result["time_interval_decimal_places"] = self.time_interval_decimal_places
        result["time_interval_width"] = self.time_interval_width
        result["vehicle_name_align_center"] = self.vehicle_name_align_center
        result["vehicle_name_uppercase"] = self.vehicle_name_uppercase
        result["vehicle_name_width"] = self.vehicle_name_width
        result["yellow_flag_status_text"] = self.yellow_flag_status_text
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Rivals":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_gap = data.get("bar_gap", obj.bar_gap)
        obj.position_x = data.get("position_x", obj.position_x)
        obj.position_y = data.get("position_y", obj.position_y)
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.font = FontConfig.from_flat(data)
        obj.best_laptime = CellConfig.from_flat(data, 'best_laptime')
        obj.best_laptime_from_recent_laps_in_race = CellConfig.from_flat(data, 'best_laptime_from_recent_laps_in_race')
        obj.brand_logo = CellConfig.from_flat(data, 'brand_logo')
        obj.class_ = CellConfig.from_flat(data, 'class')
        obj.class_style_for_position_in_class = CellConfig.from_flat(data, 'class_style_for_position_in_class')
        obj.delta_laptime = CellConfig.from_flat(data, 'delta_laptime')
        obj.delta_laptime_gain = CellConfig.from_flat(data, 'delta_laptime_gain')
        obj.delta_laptime_loss = CellConfig.from_flat(data, 'delta_laptime_loss')
        obj.driver = CellConfig.from_flat(data, 'driver')
        obj.driver_name = CellConfig.from_flat(data, 'driver_name')
        obj.energy_remaining = CellConfig.from_flat(data, 'energy_remaining')
        obj.energy_remaining_critical = CellConfig.from_flat(data, 'energy_remaining_critical')
        obj.energy_remaining_high = CellConfig.from_flat(data, 'energy_remaining_high')
        obj.energy_remaining_low = CellConfig.from_flat(data, 'energy_remaining_low')
        obj.energy_remaining_unavailable = CellConfig.from_flat(data, 'energy_remaining_unavailable')
        obj.garage = CellConfig.from_flat(data, 'garage')
        obj.inverted_delta_laptime_layout = CellConfig.from_flat(data, 'inverted_delta_laptime_layout')
        obj.laptime = CellConfig.from_flat(data, 'laptime')
        obj.penalty_count = CellConfig.from_flat(data, 'penalty_count')
        obj.pit = CellConfig.from_flat(data, 'pit')
        obj.pit_request = CellConfig.from_flat(data, 'pit_request')
        obj.pit_status = CellConfig.from_flat(data, 'pit_status')
        obj.pitstatus = CellConfig.from_flat(data, 'pitstatus')
        obj.pitstop_count = CellConfig.from_flat(data, 'pitstop_count')
        obj.pitstop_duration_while_requested_pitstop = CellConfig.from_flat(data, 'pitstop_duration_while_requested_pitstop')
        obj.position = CellConfig.from_flat(data, 'position')
        obj.position_change = CellConfig.from_flat(data, 'position_change')
        obj.position_change_in_class = CellConfig.from_flat(data, 'position_change_in_class')
        obj.position_gain = CellConfig.from_flat(data, 'position_gain')
        obj.position_in_class = CellConfig.from_flat(data, 'position_in_class')
        obj.position_loss = CellConfig.from_flat(data, 'position_loss')
        obj.position_same = CellConfig.from_flat(data, 'position_same')
        obj.speed_trap = CellConfig.from_flat(data, 'speed_trap')
        obj.stint_laps = CellConfig.from_flat(data, 'stint_laps')
        obj.time_interval = CellConfig.from_flat(data, 'time_interval')
        obj.time_interval_ahead = CellConfig.from_flat(data, 'time_interval_ahead')
        obj.time_interval_behind = CellConfig.from_flat(data, 'time_interval_behind')
        obj.timeinterval = CellConfig.from_flat(data, 'timeinterval')
        obj.tyre_compound = CellConfig.from_flat(data, 'tyre_compound')
        obj.vehicle = CellConfig.from_flat(data, 'vehicle')
        obj.vehicle_brand_as_name = CellConfig.from_flat(data, 'vehicle_brand_as_name')
        obj.vehicle_integrity = CellConfig.from_flat(data, 'vehicle_integrity')
        obj.vehicle_integrity_full = CellConfig.from_flat(data, 'vehicle_integrity_full')
        obj.vehicle_integrity_high = CellConfig.from_flat(data, 'vehicle_integrity_high')
        obj.vehicle_integrity_low = CellConfig.from_flat(data, 'vehicle_integrity_low')
        obj.vehicle_name = CellConfig.from_flat(data, 'vehicle_name')
        obj.yellow_flag = CellConfig.from_flat(data, 'yellow_flag')
        obj.brand_logo_width = data.get("brand_logo_width", obj.brand_logo_width)
        obj.class_width = data.get("class_width", obj.class_width)
        obj.driver_name_align_center = data.get("driver_name_align_center", obj.driver_name_align_center)
        obj.driver_name_shorten = data.get("driver_name_shorten", obj.driver_name_shorten)
        obj.driver_name_uppercase = data.get("driver_name_uppercase", obj.driver_name_uppercase)
        obj.driver_name_width = data.get("driver_name_width", obj.driver_name_width)
        obj.energy_remaining_decimal_places = data.get("energy_remaining_decimal_places", obj.energy_remaining_decimal_places)
        obj.garage_status_text = data.get("garage_status_text", obj.garage_status_text)
        obj.number_of_delta_laptime = data.get("number_of_delta_laptime", obj.number_of_delta_laptime)
        obj.pit_status_text = data.get("pit_status_text", obj.pit_status_text)
        obj.time_interval_align_center = data.get("time_interval_align_center", obj.time_interval_align_center)
        obj.time_interval_decimal_places = data.get("time_interval_decimal_places", obj.time_interval_decimal_places)
        obj.time_interval_width = data.get("time_interval_width", obj.time_interval_width)
        obj.vehicle_name_align_center = data.get("vehicle_name_align_center", obj.vehicle_name_align_center)
        obj.vehicle_name_uppercase = data.get("vehicle_name_uppercase", obj.vehicle_name_uppercase)
        obj.vehicle_name_width = data.get("vehicle_name_width", obj.vehicle_name_width)
        obj.yellow_flag_status_text = data.get("yellow_flag_status_text", obj.yellow_flag_status_text)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar_gap"] = self.bar_gap
        result["position_x"] = self.position_x
        result["position_y"] = self.position_y
        result["update_interval"] = self.update_interval
        result["font"] = self.font.to_dict()
        result["best_laptime"] = self.best_laptime.to_dict()
        result["best_laptime_from_recent_laps_in_race"] = self.best_laptime_from_recent_laps_in_race.to_dict()
        result["brand_logo"] = self.brand_logo.to_dict()
        result["class_"] = self.class_.to_dict()
        result["class_style_for_position_in_class"] = self.class_style_for_position_in_class.to_dict()
        result["delta_laptime"] = self.delta_laptime.to_dict()
        result["delta_laptime_gain"] = self.delta_laptime_gain.to_dict()
        result["delta_laptime_loss"] = self.delta_laptime_loss.to_dict()
        result["driver"] = self.driver.to_dict()
        result["driver_name"] = self.driver_name.to_dict()
        result["energy_remaining"] = self.energy_remaining.to_dict()
        result["energy_remaining_critical"] = self.energy_remaining_critical.to_dict()
        result["energy_remaining_high"] = self.energy_remaining_high.to_dict()
        result["energy_remaining_low"] = self.energy_remaining_low.to_dict()
        result["energy_remaining_unavailable"] = self.energy_remaining_unavailable.to_dict()
        result["garage"] = self.garage.to_dict()
        result["inverted_delta_laptime_layout"] = self.inverted_delta_laptime_layout.to_dict()
        result["laptime"] = self.laptime.to_dict()
        result["penalty_count"] = self.penalty_count.to_dict()
        result["pit"] = self.pit.to_dict()
        result["pit_request"] = self.pit_request.to_dict()
        result["pit_status"] = self.pit_status.to_dict()
        result["pitstatus"] = self.pitstatus.to_dict()
        result["pitstop_count"] = self.pitstop_count.to_dict()
        result["pitstop_duration_while_requested_pitstop"] = self.pitstop_duration_while_requested_pitstop.to_dict()
        result["position"] = self.position.to_dict()
        result["position_change"] = self.position_change.to_dict()
        result["position_change_in_class"] = self.position_change_in_class.to_dict()
        result["position_gain"] = self.position_gain.to_dict()
        result["position_in_class"] = self.position_in_class.to_dict()
        result["position_loss"] = self.position_loss.to_dict()
        result["position_same"] = self.position_same.to_dict()
        result["speed_trap"] = self.speed_trap.to_dict()
        result["stint_laps"] = self.stint_laps.to_dict()
        result["time_interval"] = self.time_interval.to_dict()
        result["time_interval_ahead"] = self.time_interval_ahead.to_dict()
        result["time_interval_behind"] = self.time_interval_behind.to_dict()
        result["timeinterval"] = self.timeinterval.to_dict()
        result["tyre_compound"] = self.tyre_compound.to_dict()
        result["vehicle"] = self.vehicle.to_dict()
        result["vehicle_brand_as_name"] = self.vehicle_brand_as_name.to_dict()
        result["vehicle_integrity"] = self.vehicle_integrity.to_dict()
        result["vehicle_integrity_full"] = self.vehicle_integrity_full.to_dict()
        result["vehicle_integrity_high"] = self.vehicle_integrity_high.to_dict()
        result["vehicle_integrity_low"] = self.vehicle_integrity_low.to_dict()
        result["vehicle_name"] = self.vehicle_name.to_dict()
        result["yellow_flag"] = self.yellow_flag.to_dict()
        result["brand_logo_width"] = self.brand_logo_width
        result["class_width"] = self.class_width
        result["driver_name_align_center"] = self.driver_name_align_center
        result["driver_name_shorten"] = self.driver_name_shorten
        result["driver_name_uppercase"] = self.driver_name_uppercase
        result["driver_name_width"] = self.driver_name_width
        result["energy_remaining_decimal_places"] = self.energy_remaining_decimal_places
        result["garage_status_text"] = self.garage_status_text
        result["number_of_delta_laptime"] = self.number_of_delta_laptime
        result["pit_status_text"] = self.pit_status_text
        result["time_interval_align_center"] = self.time_interval_align_center
        result["time_interval_decimal_places"] = self.time_interval_decimal_places
        result["time_interval_width"] = self.time_interval_width
        result["vehicle_name_align_center"] = self.vehicle_name_align_center
        result["vehicle_name_uppercase"] = self.vehicle_name_uppercase
        result["vehicle_name_width"] = self.vehicle_name_width
        result["yellow_flag_status_text"] = self.yellow_flag_status_text
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Rivals":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_gap = data.get("bar_gap", obj.bar_gap)
        obj.position_x = data.get("position_x", obj.position_x)
        obj.position_y = data.get("position_y", obj.position_y)
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.best_laptime = CellConfig.from_dict(data.get("best_laptime", {}), 'best_laptime')
        obj.best_laptime_from_recent_laps_in_race = CellConfig.from_dict(data.get("best_laptime_from_recent_laps_in_race", {}), 'best_laptime_from_recent_laps_in_race')
        obj.brand_logo = CellConfig.from_dict(data.get("brand_logo", {}), 'brand_logo')
        obj.class_ = CellConfig.from_dict(data.get("class_", {}), 'class')
        obj.class_style_for_position_in_class = CellConfig.from_dict(data.get("class_style_for_position_in_class", {}), 'class_style_for_position_in_class')
        obj.delta_laptime = CellConfig.from_dict(data.get("delta_laptime", {}), 'delta_laptime')
        obj.delta_laptime_gain = CellConfig.from_dict(data.get("delta_laptime_gain", {}), 'delta_laptime_gain')
        obj.delta_laptime_loss = CellConfig.from_dict(data.get("delta_laptime_loss", {}), 'delta_laptime_loss')
        obj.driver = CellConfig.from_dict(data.get("driver", {}), 'driver')
        obj.driver_name = CellConfig.from_dict(data.get("driver_name", {}), 'driver_name')
        obj.energy_remaining = CellConfig.from_dict(data.get("energy_remaining", {}), 'energy_remaining')
        obj.energy_remaining_critical = CellConfig.from_dict(data.get("energy_remaining_critical", {}), 'energy_remaining_critical')
        obj.energy_remaining_high = CellConfig.from_dict(data.get("energy_remaining_high", {}), 'energy_remaining_high')
        obj.energy_remaining_low = CellConfig.from_dict(data.get("energy_remaining_low", {}), 'energy_remaining_low')
        obj.energy_remaining_unavailable = CellConfig.from_dict(data.get("energy_remaining_unavailable", {}), 'energy_remaining_unavailable')
        obj.garage = CellConfig.from_dict(data.get("garage", {}), 'garage')
        obj.inverted_delta_laptime_layout = CellConfig.from_dict(data.get("inverted_delta_laptime_layout", {}), 'inverted_delta_laptime_layout')
        obj.laptime = CellConfig.from_dict(data.get("laptime", {}), 'laptime')
        obj.penalty_count = CellConfig.from_dict(data.get("penalty_count", {}), 'penalty_count')
        obj.pit = CellConfig.from_dict(data.get("pit", {}), 'pit')
        obj.pit_request = CellConfig.from_dict(data.get("pit_request", {}), 'pit_request')
        obj.pit_status = CellConfig.from_dict(data.get("pit_status", {}), 'pit_status')
        obj.pitstatus = CellConfig.from_dict(data.get("pitstatus", {}), 'pitstatus')
        obj.pitstop_count = CellConfig.from_dict(data.get("pitstop_count", {}), 'pitstop_count')
        obj.pitstop_duration_while_requested_pitstop = CellConfig.from_dict(data.get("pitstop_duration_while_requested_pitstop", {}), 'pitstop_duration_while_requested_pitstop')
        obj.position = CellConfig.from_dict(data.get("position", {}), 'position')
        obj.position_change = CellConfig.from_dict(data.get("position_change", {}), 'position_change')
        obj.position_change_in_class = CellConfig.from_dict(data.get("position_change_in_class", {}), 'position_change_in_class')
        obj.position_gain = CellConfig.from_dict(data.get("position_gain", {}), 'position_gain')
        obj.position_in_class = CellConfig.from_dict(data.get("position_in_class", {}), 'position_in_class')
        obj.position_loss = CellConfig.from_dict(data.get("position_loss", {}), 'position_loss')
        obj.position_same = CellConfig.from_dict(data.get("position_same", {}), 'position_same')
        obj.speed_trap = CellConfig.from_dict(data.get("speed_trap", {}), 'speed_trap')
        obj.stint_laps = CellConfig.from_dict(data.get("stint_laps", {}), 'stint_laps')
        obj.time_interval = CellConfig.from_dict(data.get("time_interval", {}), 'time_interval')
        obj.time_interval_ahead = CellConfig.from_dict(data.get("time_interval_ahead", {}), 'time_interval_ahead')
        obj.time_interval_behind = CellConfig.from_dict(data.get("time_interval_behind", {}), 'time_interval_behind')
        obj.timeinterval = CellConfig.from_dict(data.get("timeinterval", {}), 'timeinterval')
        obj.tyre_compound = CellConfig.from_dict(data.get("tyre_compound", {}), 'tyre_compound')
        obj.vehicle = CellConfig.from_dict(data.get("vehicle", {}), 'vehicle')
        obj.vehicle_brand_as_name = CellConfig.from_dict(data.get("vehicle_brand_as_name", {}), 'vehicle_brand_as_name')
        obj.vehicle_integrity = CellConfig.from_dict(data.get("vehicle_integrity", {}), 'vehicle_integrity')
        obj.vehicle_integrity_full = CellConfig.from_dict(data.get("vehicle_integrity_full", {}), 'vehicle_integrity_full')
        obj.vehicle_integrity_high = CellConfig.from_dict(data.get("vehicle_integrity_high", {}), 'vehicle_integrity_high')
        obj.vehicle_integrity_low = CellConfig.from_dict(data.get("vehicle_integrity_low", {}), 'vehicle_integrity_low')
        obj.vehicle_name = CellConfig.from_dict(data.get("vehicle_name", {}), 'vehicle_name')
        obj.yellow_flag = CellConfig.from_dict(data.get("yellow_flag", {}), 'yellow_flag')
        obj.brand_logo_width = data.get("brand_logo_width", obj.brand_logo_width)
        obj.class_width = data.get("class_width", obj.class_width)
        obj.driver_name_align_center = data.get("driver_name_align_center", obj.driver_name_align_center)
        obj.driver_name_shorten = data.get("driver_name_shorten", obj.driver_name_shorten)
        obj.driver_name_uppercase = data.get("driver_name_uppercase", obj.driver_name_uppercase)
        obj.driver_name_width = data.get("driver_name_width", obj.driver_name_width)
        obj.energy_remaining_decimal_places = data.get("energy_remaining_decimal_places", obj.energy_remaining_decimal_places)
        obj.garage_status_text = data.get("garage_status_text", obj.garage_status_text)
        obj.number_of_delta_laptime = data.get("number_of_delta_laptime", obj.number_of_delta_laptime)
        obj.pit_status_text = data.get("pit_status_text", obj.pit_status_text)
        obj.time_interval_align_center = data.get("time_interval_align_center", obj.time_interval_align_center)
        obj.time_interval_decimal_places = data.get("time_interval_decimal_places", obj.time_interval_decimal_places)
        obj.time_interval_width = data.get("time_interval_width", obj.time_interval_width)
        obj.vehicle_name_align_center = data.get("vehicle_name_align_center", obj.vehicle_name_align_center)
        obj.vehicle_name_uppercase = data.get("vehicle_name_uppercase", obj.vehicle_name_uppercase)
        obj.vehicle_name_width = data.get("vehicle_name_width", obj.vehicle_name_width)
        obj.yellow_flag_status_text = data.get("yellow_flag_status_text", obj.yellow_flag_status_text)
        return obj
