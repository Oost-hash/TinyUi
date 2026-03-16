# Auto-generated widget
# Widget: relative

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, WidgetConfig
from ..colors import AMBER, CLASS_POSITION, CYAN, FASTEST, GAIN, GARAGE, LIME, LOSS, PENALTY, PIT, PIT_REQUEST, PLAYER, PLAYER_FASTEST, PLAYER_HIGHLIGHT, PLAYER_NAME, READING, RED, SUBTLE, TABLE_DIM, TABLE_HEADER, TABLE_ROW, WHITE_ON_LIGHT, YELLOW_FLAG


@dataclass
class Relative(WidgetConfig):
    name: str = "relative"

    # base overrides
    bar_gap: int = 1
    position_x: int = 320
    position_y: int = 148
    update_interval: int = 100

    # groups
    font: FontConfig = field(default_factory=FontConfig)

    # cells
    best_laptime: CellConfig = field(default_factory=lambda: CellConfig(id='best_laptime', font_color=TABLE_ROW.font_color, bkg_color=TABLE_ROW.bkg_color, show=False, column_index=11))
    best_laptime_from_recent_laps_in_race: CellConfig = field(default_factory=lambda: CellConfig(id='best_laptime_from_recent_laps_in_race', show=False))
    brand_logo: CellConfig = field(default_factory=lambda: CellConfig(id='brand_logo', show=False, column_index=8))
    class_: CellConfig = field(default_factory=lambda: CellConfig(id='class', font_color=TABLE_HEADER.font_color, bkg_color=TABLE_HEADER.bkg_color, column_index=5))
    class_style_for_position_in_class: CellConfig = field(default_factory=lambda: CellConfig(id='class_style_for_position_in_class', show=False))
    driver: CellConfig = field(default_factory=lambda: CellConfig(id='driver', column_index=2))
    driver_name: CellConfig = field(default_factory=lambda: CellConfig(id='driver_name'))
    energy_remaining: CellConfig = field(default_factory=lambda: CellConfig(id='energy_remaining', font_color=SUBTLE.font_color, bkg_color=SUBTLE.bkg_color, column_index=20))
    energy_remaining_critical: CellConfig = field(default_factory=lambda: CellConfig(id='energy_remaining_critical', font_color=RED.font_color, bkg_color=RED.bkg_color))
    energy_remaining_high: CellConfig = field(default_factory=lambda: CellConfig(id='energy_remaining_high', font_color=LIME.font_color, bkg_color=LIME.bkg_color))
    energy_remaining_low: CellConfig = field(default_factory=lambda: CellConfig(id='energy_remaining_low', font_color=AMBER.font_color, bkg_color=AMBER.bkg_color))
    energy_remaining_unavailable: CellConfig = field(default_factory=lambda: CellConfig(id='energy_remaining_unavailable', font_color=READING.font_color, bkg_color=READING.bkg_color))
    fastest_last_laptime: CellConfig = field(default_factory=lambda: CellConfig(id='fastest_last_laptime', font_color=FASTEST.font_color, bkg_color=FASTEST.bkg_color))
    garage: CellConfig = field(default_factory=lambda: CellConfig(id='garage', font_color=GARAGE.font_color, bkg_color=GARAGE.bkg_color))
    highlighted_fastest_last_laptime: CellConfig = field(default_factory=lambda: CellConfig(id='highlighted_fastest_last_laptime'))
    highlighted_nearest_time_gap: CellConfig = field(default_factory=lambda: CellConfig(id='highlighted_nearest_time_gap'))
    lap_difference: CellConfig = field(default_factory=lambda: CellConfig(id='lap_difference'))
    laps_ahead: CellConfig = field(default_factory=lambda: CellConfig(id='laps_ahead', font_color='#FF44CC'))
    laps_behind: CellConfig = field(default_factory=lambda: CellConfig(id='laps_behind', font_color=CYAN.font_color, bkg_color=CYAN.bkg_color))
    laptime: CellConfig = field(default_factory=lambda: CellConfig(id='laptime', font_color=TABLE_ROW.font_color, bkg_color=TABLE_ROW.bkg_color, column_index=3))
    nearest_time_gap: CellConfig = field(default_factory=lambda: CellConfig(id='nearest_time_gap', bkg_color='#AA22AA'))
    penalty_count: CellConfig = field(default_factory=lambda: CellConfig(id='penalty_count', font_color=PENALTY.font_color, bkg_color=PENALTY.bkg_color))
    pit: CellConfig = field(default_factory=lambda: CellConfig(id='pit', font_color=PIT.font_color, bkg_color=PIT.bkg_color))
    pit_request: CellConfig = field(default_factory=lambda: CellConfig(id='pit_request', font_color=PIT_REQUEST.font_color, bkg_color=PIT_REQUEST.bkg_color))
    pit_status: CellConfig = field(default_factory=lambda: CellConfig(id='pit_status'))
    pitstatus: CellConfig = field(default_factory=lambda: CellConfig(id='pitstatus', column_index=22))
    pitstop_count: CellConfig = field(default_factory=lambda: CellConfig(id='pitstop_count', font_color=TABLE_DIM.font_color, bkg_color=TABLE_DIM.bkg_color, column_index=10))
    pitstop_duration_while_requested_pitstop: CellConfig = field(default_factory=lambda: CellConfig(id='pitstop_duration_while_requested_pitstop'))
    player_best_laptime: CellConfig = field(default_factory=lambda: CellConfig(id='player_best_laptime', font_color=PLAYER.font_color, bkg_color=PLAYER.bkg_color))
    player_brand_logo: CellConfig = field(default_factory=lambda: CellConfig(id='player_brand_logo', font_color=WHITE_ON_LIGHT.font_color, bkg_color=WHITE_ON_LIGHT.bkg_color))
    player_driver_name: CellConfig = field(default_factory=lambda: CellConfig(id='player_driver_name', font_color=PLAYER_NAME.font_color, bkg_color=PLAYER_NAME.bkg_color))
    player_energy_remaining: CellConfig = field(default_factory=lambda: CellConfig(id='player_energy_remaining', font_color=PLAYER.font_color, bkg_color=PLAYER.bkg_color))
    player_fastest_last_laptime: CellConfig = field(default_factory=lambda: CellConfig(id='player_fastest_last_laptime', font_color=PLAYER_FASTEST.font_color, bkg_color=PLAYER_FASTEST.bkg_color))
    player_highlighted: CellConfig = field(default_factory=lambda: CellConfig(id='player_highlighted'))
    player_laptime: CellConfig = field(default_factory=lambda: CellConfig(id='player_laptime', font_color=PLAYER.font_color, bkg_color=PLAYER.bkg_color))
    player_pitstop_count: CellConfig = field(default_factory=lambda: CellConfig(id='player_pitstop_count', font_color=PLAYER.font_color, bkg_color=PLAYER.bkg_color))
    player_position: CellConfig = field(default_factory=lambda: CellConfig(id='player_position', font_color=PLAYER_HIGHLIGHT.font_color, bkg_color=PLAYER_HIGHLIGHT.bkg_color))
    player_position_change: CellConfig = field(default_factory=lambda: CellConfig(id='player_position_change', font_color=PLAYER_HIGHLIGHT.font_color, bkg_color=PLAYER_HIGHLIGHT.bkg_color))
    player_position_in_class: CellConfig = field(default_factory=lambda: CellConfig(id='player_position_in_class', font_color=PLAYER_HIGHLIGHT.font_color, bkg_color=PLAYER_HIGHLIGHT.bkg_color))
    player_speed_trap: CellConfig = field(default_factory=lambda: CellConfig(id='player_speed_trap', font_color=PLAYER.font_color, bkg_color=PLAYER.bkg_color))
    player_stint_laps: CellConfig = field(default_factory=lambda: CellConfig(id='player_stint_laps', font_color=PLAYER.font_color, bkg_color=PLAYER.bkg_color))
    player_time_gap: CellConfig = field(default_factory=lambda: CellConfig(id='player_time_gap', font_color=PLAYER_NAME.font_color, bkg_color=PLAYER_NAME.bkg_color))
    player_tyre_compound: CellConfig = field(default_factory=lambda: CellConfig(id='player_tyre_compound', font_color=PLAYER_NAME.font_color, bkg_color=PLAYER_NAME.bkg_color))
    player_vehicle_integrity: CellConfig = field(default_factory=lambda: CellConfig(id='player_vehicle_integrity', font_color=PLAYER.font_color, bkg_color=PLAYER.bkg_color))
    player_vehicle_name: CellConfig = field(default_factory=lambda: CellConfig(id='player_vehicle_name', font_color=PLAYER_NAME.font_color, bkg_color=PLAYER_NAME.bkg_color))
    position: CellConfig = field(default_factory=lambda: CellConfig(id='position', font_color=TABLE_HEADER.font_color, bkg_color=TABLE_HEADER.bkg_color, column_index=1))
    position_change: CellConfig = field(default_factory=lambda: CellConfig(id='position_change', column_index=12))
    position_change_in_class: CellConfig = field(default_factory=lambda: CellConfig(id='position_change_in_class'))
    position_gain: CellConfig = field(default_factory=lambda: CellConfig(id='position_gain', font_color=GAIN.font_color, bkg_color=GAIN.bkg_color))
    position_in_class: CellConfig = field(default_factory=lambda: CellConfig(id='position_in_class', font_color=CLASS_POSITION.font_color, bkg_color=CLASS_POSITION.bkg_color, column_index=4))
    position_loss: CellConfig = field(default_factory=lambda: CellConfig(id='position_loss', font_color=LOSS.font_color, bkg_color=LOSS.bkg_color))
    position_same: CellConfig = field(default_factory=lambda: CellConfig(id='position_same', font_color=TABLE_DIM.font_color, bkg_color=TABLE_DIM.bkg_color))
    same_lap: CellConfig = field(default_factory=lambda: CellConfig(id='same_lap'))
    speed_trap: CellConfig = field(default_factory=lambda: CellConfig(id='speed_trap', font_color=TABLE_ROW.font_color, bkg_color=TABLE_ROW.bkg_color, column_index=19))
    stint_laps: CellConfig = field(default_factory=lambda: CellConfig(id='stint_laps', font_color=TABLE_DIM.font_color, bkg_color=TABLE_DIM.bkg_color, column_index=16))
    time_gap: CellConfig = field(default_factory=lambda: CellConfig(id='time_gap'))
    time_gap_sign: CellConfig = field(default_factory=lambda: CellConfig(id='time_gap_sign', show=False))
    timegap: CellConfig = field(default_factory=lambda: CellConfig(id='timegap', column_index=15))
    tyre_compound: CellConfig = field(default_factory=lambda: CellConfig(id='tyre_compound', font_color=TABLE_ROW.font_color, bkg_color=TABLE_ROW.bkg_color, column_index=7))
    vehicle: CellConfig = field(default_factory=lambda: CellConfig(id='vehicle', column_index=6))
    vehicle_brand_as_name: CellConfig = field(default_factory=lambda: CellConfig(id='vehicle_brand_as_name'))
    vehicle_in_garage: CellConfig = field(default_factory=lambda: CellConfig(id='vehicle_in_garage', show=False))
    vehicle_integrity: CellConfig = field(default_factory=lambda: CellConfig(id='vehicle_integrity', font_color=SUBTLE.font_color, bkg_color=SUBTLE.bkg_color, column_index=17))
    vehicle_integrity_full: CellConfig = field(default_factory=lambda: CellConfig(id='vehicle_integrity_full', font_color=READING.font_color, bkg_color=READING.bkg_color))
    vehicle_integrity_high: CellConfig = field(default_factory=lambda: CellConfig(id='vehicle_integrity_high', font_color=CYAN.font_color, bkg_color=CYAN.bkg_color))
    vehicle_integrity_low: CellConfig = field(default_factory=lambda: CellConfig(id='vehicle_integrity_low', font_color=RED.font_color, bkg_color=RED.bkg_color))
    vehicle_name: CellConfig = field(default_factory=lambda: CellConfig(id='vehicle_name', show=False))
    yellow_flag: CellConfig = field(default_factory=lambda: CellConfig(id='yellow_flag', font_color=YELLOW_FLAG.font_color, bkg_color=YELLOW_FLAG.bkg_color))

    # config
    additional_players_behind: int = 0
    additional_players_front: int = 0
    brand_logo_width: int = 20
    class_width: int = 4
    driver_name_align_center: bool = False
    driver_name_shorten: bool = False
    driver_name_uppercase: bool = False
    driver_name_width: int = 10
    energy_remaining_decimal_places: int = 0
    garage_status_text: str = 'G'
    nearest_time_gap_threshold_behind: int = 2
    nearest_time_gap_threshold_front: int = 1
    pit_status_text: str = 'P'
    time_gap_align_center: bool = False
    time_gap_decimal_places: int = 1
    time_gap_width: int = 4
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
        result.update(self.driver.to_flat())
        result.update(self.driver_name.to_flat())
        result.update(self.energy_remaining.to_flat())
        result.update(self.energy_remaining_critical.to_flat())
        result.update(self.energy_remaining_high.to_flat())
        result.update(self.energy_remaining_low.to_flat())
        result.update(self.energy_remaining_unavailable.to_flat())
        result.update(self.fastest_last_laptime.to_flat())
        result.update(self.garage.to_flat())
        result.update(self.highlighted_fastest_last_laptime.to_flat())
        result.update(self.highlighted_nearest_time_gap.to_flat())
        result.update(self.lap_difference.to_flat())
        result.update(self.laps_ahead.to_flat())
        result.update(self.laps_behind.to_flat())
        result.update(self.laptime.to_flat())
        result.update(self.nearest_time_gap.to_flat())
        result.update(self.penalty_count.to_flat())
        result.update(self.pit.to_flat())
        result.update(self.pit_request.to_flat())
        result.update(self.pit_status.to_flat())
        result.update(self.pitstatus.to_flat())
        result.update(self.pitstop_count.to_flat())
        result.update(self.pitstop_duration_while_requested_pitstop.to_flat())
        result.update(self.player_best_laptime.to_flat())
        result.update(self.player_brand_logo.to_flat())
        result.update(self.player_driver_name.to_flat())
        result.update(self.player_energy_remaining.to_flat())
        result.update(self.player_fastest_last_laptime.to_flat())
        result.update(self.player_highlighted.to_flat())
        result.update(self.player_laptime.to_flat())
        result.update(self.player_pitstop_count.to_flat())
        result.update(self.player_position.to_flat())
        result.update(self.player_position_change.to_flat())
        result.update(self.player_position_in_class.to_flat())
        result.update(self.player_speed_trap.to_flat())
        result.update(self.player_stint_laps.to_flat())
        result.update(self.player_time_gap.to_flat())
        result.update(self.player_tyre_compound.to_flat())
        result.update(self.player_vehicle_integrity.to_flat())
        result.update(self.player_vehicle_name.to_flat())
        result.update(self.position.to_flat())
        result.update(self.position_change.to_flat())
        result.update(self.position_change_in_class.to_flat())
        result.update(self.position_gain.to_flat())
        result.update(self.position_in_class.to_flat())
        result.update(self.position_loss.to_flat())
        result.update(self.position_same.to_flat())
        result.update(self.same_lap.to_flat())
        result.update(self.speed_trap.to_flat())
        result.update(self.stint_laps.to_flat())
        result.update(self.time_gap.to_flat())
        result.update(self.time_gap_sign.to_flat())
        result.update(self.timegap.to_flat())
        result.update(self.tyre_compound.to_flat())
        result.update(self.vehicle.to_flat())
        result.update(self.vehicle_brand_as_name.to_flat())
        result.update(self.vehicle_in_garage.to_flat())
        result.update(self.vehicle_integrity.to_flat())
        result.update(self.vehicle_integrity_full.to_flat())
        result.update(self.vehicle_integrity_high.to_flat())
        result.update(self.vehicle_integrity_low.to_flat())
        result.update(self.vehicle_name.to_flat())
        result.update(self.yellow_flag.to_flat())
        result["additional_players_behind"] = self.additional_players_behind
        result["additional_players_front"] = self.additional_players_front
        result["brand_logo_width"] = self.brand_logo_width
        result["class_width"] = self.class_width
        result["driver_name_align_center"] = self.driver_name_align_center
        result["driver_name_shorten"] = self.driver_name_shorten
        result["driver_name_uppercase"] = self.driver_name_uppercase
        result["driver_name_width"] = self.driver_name_width
        result["energy_remaining_decimal_places"] = self.energy_remaining_decimal_places
        result["garage_status_text"] = self.garage_status_text
        result["nearest_time_gap_threshold_behind"] = self.nearest_time_gap_threshold_behind
        result["nearest_time_gap_threshold_front"] = self.nearest_time_gap_threshold_front
        result["pit_status_text"] = self.pit_status_text
        result["time_gap_align_center"] = self.time_gap_align_center
        result["time_gap_decimal_places"] = self.time_gap_decimal_places
        result["time_gap_width"] = self.time_gap_width
        result["vehicle_name_align_center"] = self.vehicle_name_align_center
        result["vehicle_name_uppercase"] = self.vehicle_name_uppercase
        result["vehicle_name_width"] = self.vehicle_name_width
        result["yellow_flag_status_text"] = self.yellow_flag_status_text
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Relative":
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
        obj.driver = CellConfig.from_flat(data, 'driver')
        obj.driver_name = CellConfig.from_flat(data, 'driver_name')
        obj.energy_remaining = CellConfig.from_flat(data, 'energy_remaining')
        obj.energy_remaining_critical = CellConfig.from_flat(data, 'energy_remaining_critical')
        obj.energy_remaining_high = CellConfig.from_flat(data, 'energy_remaining_high')
        obj.energy_remaining_low = CellConfig.from_flat(data, 'energy_remaining_low')
        obj.energy_remaining_unavailable = CellConfig.from_flat(data, 'energy_remaining_unavailable')
        obj.fastest_last_laptime = CellConfig.from_flat(data, 'fastest_last_laptime')
        obj.garage = CellConfig.from_flat(data, 'garage')
        obj.highlighted_fastest_last_laptime = CellConfig.from_flat(data, 'highlighted_fastest_last_laptime')
        obj.highlighted_nearest_time_gap = CellConfig.from_flat(data, 'highlighted_nearest_time_gap')
        obj.lap_difference = CellConfig.from_flat(data, 'lap_difference')
        obj.laps_ahead = CellConfig.from_flat(data, 'laps_ahead')
        obj.laps_behind = CellConfig.from_flat(data, 'laps_behind')
        obj.laptime = CellConfig.from_flat(data, 'laptime')
        obj.nearest_time_gap = CellConfig.from_flat(data, 'nearest_time_gap')
        obj.penalty_count = CellConfig.from_flat(data, 'penalty_count')
        obj.pit = CellConfig.from_flat(data, 'pit')
        obj.pit_request = CellConfig.from_flat(data, 'pit_request')
        obj.pit_status = CellConfig.from_flat(data, 'pit_status')
        obj.pitstatus = CellConfig.from_flat(data, 'pitstatus')
        obj.pitstop_count = CellConfig.from_flat(data, 'pitstop_count')
        obj.pitstop_duration_while_requested_pitstop = CellConfig.from_flat(data, 'pitstop_duration_while_requested_pitstop')
        obj.player_best_laptime = CellConfig.from_flat(data, 'player_best_laptime')
        obj.player_brand_logo = CellConfig.from_flat(data, 'player_brand_logo')
        obj.player_driver_name = CellConfig.from_flat(data, 'player_driver_name')
        obj.player_energy_remaining = CellConfig.from_flat(data, 'player_energy_remaining')
        obj.player_fastest_last_laptime = CellConfig.from_flat(data, 'player_fastest_last_laptime')
        obj.player_highlighted = CellConfig.from_flat(data, 'player_highlighted')
        obj.player_laptime = CellConfig.from_flat(data, 'player_laptime')
        obj.player_pitstop_count = CellConfig.from_flat(data, 'player_pitstop_count')
        obj.player_position = CellConfig.from_flat(data, 'player_position')
        obj.player_position_change = CellConfig.from_flat(data, 'player_position_change')
        obj.player_position_in_class = CellConfig.from_flat(data, 'player_position_in_class')
        obj.player_speed_trap = CellConfig.from_flat(data, 'player_speed_trap')
        obj.player_stint_laps = CellConfig.from_flat(data, 'player_stint_laps')
        obj.player_time_gap = CellConfig.from_flat(data, 'player_time_gap')
        obj.player_tyre_compound = CellConfig.from_flat(data, 'player_tyre_compound')
        obj.player_vehicle_integrity = CellConfig.from_flat(data, 'player_vehicle_integrity')
        obj.player_vehicle_name = CellConfig.from_flat(data, 'player_vehicle_name')
        obj.position = CellConfig.from_flat(data, 'position')
        obj.position_change = CellConfig.from_flat(data, 'position_change')
        obj.position_change_in_class = CellConfig.from_flat(data, 'position_change_in_class')
        obj.position_gain = CellConfig.from_flat(data, 'position_gain')
        obj.position_in_class = CellConfig.from_flat(data, 'position_in_class')
        obj.position_loss = CellConfig.from_flat(data, 'position_loss')
        obj.position_same = CellConfig.from_flat(data, 'position_same')
        obj.same_lap = CellConfig.from_flat(data, 'same_lap')
        obj.speed_trap = CellConfig.from_flat(data, 'speed_trap')
        obj.stint_laps = CellConfig.from_flat(data, 'stint_laps')
        obj.time_gap = CellConfig.from_flat(data, 'time_gap')
        obj.time_gap_sign = CellConfig.from_flat(data, 'time_gap_sign')
        obj.timegap = CellConfig.from_flat(data, 'timegap')
        obj.tyre_compound = CellConfig.from_flat(data, 'tyre_compound')
        obj.vehicle = CellConfig.from_flat(data, 'vehicle')
        obj.vehicle_brand_as_name = CellConfig.from_flat(data, 'vehicle_brand_as_name')
        obj.vehicle_in_garage = CellConfig.from_flat(data, 'vehicle_in_garage')
        obj.vehicle_integrity = CellConfig.from_flat(data, 'vehicle_integrity')
        obj.vehicle_integrity_full = CellConfig.from_flat(data, 'vehicle_integrity_full')
        obj.vehicle_integrity_high = CellConfig.from_flat(data, 'vehicle_integrity_high')
        obj.vehicle_integrity_low = CellConfig.from_flat(data, 'vehicle_integrity_low')
        obj.vehicle_name = CellConfig.from_flat(data, 'vehicle_name')
        obj.yellow_flag = CellConfig.from_flat(data, 'yellow_flag')
        obj.additional_players_behind = data.get("additional_players_behind", obj.additional_players_behind)
        obj.additional_players_front = data.get("additional_players_front", obj.additional_players_front)
        obj.brand_logo_width = data.get("brand_logo_width", obj.brand_logo_width)
        obj.class_width = data.get("class_width", obj.class_width)
        obj.driver_name_align_center = data.get("driver_name_align_center", obj.driver_name_align_center)
        obj.driver_name_shorten = data.get("driver_name_shorten", obj.driver_name_shorten)
        obj.driver_name_uppercase = data.get("driver_name_uppercase", obj.driver_name_uppercase)
        obj.driver_name_width = data.get("driver_name_width", obj.driver_name_width)
        obj.energy_remaining_decimal_places = data.get("energy_remaining_decimal_places", obj.energy_remaining_decimal_places)
        obj.garage_status_text = data.get("garage_status_text", obj.garage_status_text)
        obj.nearest_time_gap_threshold_behind = data.get("nearest_time_gap_threshold_behind", obj.nearest_time_gap_threshold_behind)
        obj.nearest_time_gap_threshold_front = data.get("nearest_time_gap_threshold_front", obj.nearest_time_gap_threshold_front)
        obj.pit_status_text = data.get("pit_status_text", obj.pit_status_text)
        obj.time_gap_align_center = data.get("time_gap_align_center", obj.time_gap_align_center)
        obj.time_gap_decimal_places = data.get("time_gap_decimal_places", obj.time_gap_decimal_places)
        obj.time_gap_width = data.get("time_gap_width", obj.time_gap_width)
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
        result["driver"] = self.driver.to_dict()
        result["driver_name"] = self.driver_name.to_dict()
        result["energy_remaining"] = self.energy_remaining.to_dict()
        result["energy_remaining_critical"] = self.energy_remaining_critical.to_dict()
        result["energy_remaining_high"] = self.energy_remaining_high.to_dict()
        result["energy_remaining_low"] = self.energy_remaining_low.to_dict()
        result["energy_remaining_unavailable"] = self.energy_remaining_unavailable.to_dict()
        result["fastest_last_laptime"] = self.fastest_last_laptime.to_dict()
        result["garage"] = self.garage.to_dict()
        result["highlighted_fastest_last_laptime"] = self.highlighted_fastest_last_laptime.to_dict()
        result["highlighted_nearest_time_gap"] = self.highlighted_nearest_time_gap.to_dict()
        result["lap_difference"] = self.lap_difference.to_dict()
        result["laps_ahead"] = self.laps_ahead.to_dict()
        result["laps_behind"] = self.laps_behind.to_dict()
        result["laptime"] = self.laptime.to_dict()
        result["nearest_time_gap"] = self.nearest_time_gap.to_dict()
        result["penalty_count"] = self.penalty_count.to_dict()
        result["pit"] = self.pit.to_dict()
        result["pit_request"] = self.pit_request.to_dict()
        result["pit_status"] = self.pit_status.to_dict()
        result["pitstatus"] = self.pitstatus.to_dict()
        result["pitstop_count"] = self.pitstop_count.to_dict()
        result["pitstop_duration_while_requested_pitstop"] = self.pitstop_duration_while_requested_pitstop.to_dict()
        result["player_best_laptime"] = self.player_best_laptime.to_dict()
        result["player_brand_logo"] = self.player_brand_logo.to_dict()
        result["player_driver_name"] = self.player_driver_name.to_dict()
        result["player_energy_remaining"] = self.player_energy_remaining.to_dict()
        result["player_fastest_last_laptime"] = self.player_fastest_last_laptime.to_dict()
        result["player_highlighted"] = self.player_highlighted.to_dict()
        result["player_laptime"] = self.player_laptime.to_dict()
        result["player_pitstop_count"] = self.player_pitstop_count.to_dict()
        result["player_position"] = self.player_position.to_dict()
        result["player_position_change"] = self.player_position_change.to_dict()
        result["player_position_in_class"] = self.player_position_in_class.to_dict()
        result["player_speed_trap"] = self.player_speed_trap.to_dict()
        result["player_stint_laps"] = self.player_stint_laps.to_dict()
        result["player_time_gap"] = self.player_time_gap.to_dict()
        result["player_tyre_compound"] = self.player_tyre_compound.to_dict()
        result["player_vehicle_integrity"] = self.player_vehicle_integrity.to_dict()
        result["player_vehicle_name"] = self.player_vehicle_name.to_dict()
        result["position"] = self.position.to_dict()
        result["position_change"] = self.position_change.to_dict()
        result["position_change_in_class"] = self.position_change_in_class.to_dict()
        result["position_gain"] = self.position_gain.to_dict()
        result["position_in_class"] = self.position_in_class.to_dict()
        result["position_loss"] = self.position_loss.to_dict()
        result["position_same"] = self.position_same.to_dict()
        result["same_lap"] = self.same_lap.to_dict()
        result["speed_trap"] = self.speed_trap.to_dict()
        result["stint_laps"] = self.stint_laps.to_dict()
        result["time_gap"] = self.time_gap.to_dict()
        result["time_gap_sign"] = self.time_gap_sign.to_dict()
        result["timegap"] = self.timegap.to_dict()
        result["tyre_compound"] = self.tyre_compound.to_dict()
        result["vehicle"] = self.vehicle.to_dict()
        result["vehicle_brand_as_name"] = self.vehicle_brand_as_name.to_dict()
        result["vehicle_in_garage"] = self.vehicle_in_garage.to_dict()
        result["vehicle_integrity"] = self.vehicle_integrity.to_dict()
        result["vehicle_integrity_full"] = self.vehicle_integrity_full.to_dict()
        result["vehicle_integrity_high"] = self.vehicle_integrity_high.to_dict()
        result["vehicle_integrity_low"] = self.vehicle_integrity_low.to_dict()
        result["vehicle_name"] = self.vehicle_name.to_dict()
        result["yellow_flag"] = self.yellow_flag.to_dict()
        result["additional_players_behind"] = self.additional_players_behind
        result["additional_players_front"] = self.additional_players_front
        result["brand_logo_width"] = self.brand_logo_width
        result["class_width"] = self.class_width
        result["driver_name_align_center"] = self.driver_name_align_center
        result["driver_name_shorten"] = self.driver_name_shorten
        result["driver_name_uppercase"] = self.driver_name_uppercase
        result["driver_name_width"] = self.driver_name_width
        result["energy_remaining_decimal_places"] = self.energy_remaining_decimal_places
        result["garage_status_text"] = self.garage_status_text
        result["nearest_time_gap_threshold_behind"] = self.nearest_time_gap_threshold_behind
        result["nearest_time_gap_threshold_front"] = self.nearest_time_gap_threshold_front
        result["pit_status_text"] = self.pit_status_text
        result["time_gap_align_center"] = self.time_gap_align_center
        result["time_gap_decimal_places"] = self.time_gap_decimal_places
        result["time_gap_width"] = self.time_gap_width
        result["vehicle_name_align_center"] = self.vehicle_name_align_center
        result["vehicle_name_uppercase"] = self.vehicle_name_uppercase
        result["vehicle_name_width"] = self.vehicle_name_width
        result["yellow_flag_status_text"] = self.yellow_flag_status_text
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Relative":
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
        obj.driver = CellConfig.from_dict(data.get("driver", {}), 'driver')
        obj.driver_name = CellConfig.from_dict(data.get("driver_name", {}), 'driver_name')
        obj.energy_remaining = CellConfig.from_dict(data.get("energy_remaining", {}), 'energy_remaining')
        obj.energy_remaining_critical = CellConfig.from_dict(data.get("energy_remaining_critical", {}), 'energy_remaining_critical')
        obj.energy_remaining_high = CellConfig.from_dict(data.get("energy_remaining_high", {}), 'energy_remaining_high')
        obj.energy_remaining_low = CellConfig.from_dict(data.get("energy_remaining_low", {}), 'energy_remaining_low')
        obj.energy_remaining_unavailable = CellConfig.from_dict(data.get("energy_remaining_unavailable", {}), 'energy_remaining_unavailable')
        obj.fastest_last_laptime = CellConfig.from_dict(data.get("fastest_last_laptime", {}), 'fastest_last_laptime')
        obj.garage = CellConfig.from_dict(data.get("garage", {}), 'garage')
        obj.highlighted_fastest_last_laptime = CellConfig.from_dict(data.get("highlighted_fastest_last_laptime", {}), 'highlighted_fastest_last_laptime')
        obj.highlighted_nearest_time_gap = CellConfig.from_dict(data.get("highlighted_nearest_time_gap", {}), 'highlighted_nearest_time_gap')
        obj.lap_difference = CellConfig.from_dict(data.get("lap_difference", {}), 'lap_difference')
        obj.laps_ahead = CellConfig.from_dict(data.get("laps_ahead", {}), 'laps_ahead')
        obj.laps_behind = CellConfig.from_dict(data.get("laps_behind", {}), 'laps_behind')
        obj.laptime = CellConfig.from_dict(data.get("laptime", {}), 'laptime')
        obj.nearest_time_gap = CellConfig.from_dict(data.get("nearest_time_gap", {}), 'nearest_time_gap')
        obj.penalty_count = CellConfig.from_dict(data.get("penalty_count", {}), 'penalty_count')
        obj.pit = CellConfig.from_dict(data.get("pit", {}), 'pit')
        obj.pit_request = CellConfig.from_dict(data.get("pit_request", {}), 'pit_request')
        obj.pit_status = CellConfig.from_dict(data.get("pit_status", {}), 'pit_status')
        obj.pitstatus = CellConfig.from_dict(data.get("pitstatus", {}), 'pitstatus')
        obj.pitstop_count = CellConfig.from_dict(data.get("pitstop_count", {}), 'pitstop_count')
        obj.pitstop_duration_while_requested_pitstop = CellConfig.from_dict(data.get("pitstop_duration_while_requested_pitstop", {}), 'pitstop_duration_while_requested_pitstop')
        obj.player_best_laptime = CellConfig.from_dict(data.get("player_best_laptime", {}), 'player_best_laptime')
        obj.player_brand_logo = CellConfig.from_dict(data.get("player_brand_logo", {}), 'player_brand_logo')
        obj.player_driver_name = CellConfig.from_dict(data.get("player_driver_name", {}), 'player_driver_name')
        obj.player_energy_remaining = CellConfig.from_dict(data.get("player_energy_remaining", {}), 'player_energy_remaining')
        obj.player_fastest_last_laptime = CellConfig.from_dict(data.get("player_fastest_last_laptime", {}), 'player_fastest_last_laptime')
        obj.player_highlighted = CellConfig.from_dict(data.get("player_highlighted", {}), 'player_highlighted')
        obj.player_laptime = CellConfig.from_dict(data.get("player_laptime", {}), 'player_laptime')
        obj.player_pitstop_count = CellConfig.from_dict(data.get("player_pitstop_count", {}), 'player_pitstop_count')
        obj.player_position = CellConfig.from_dict(data.get("player_position", {}), 'player_position')
        obj.player_position_change = CellConfig.from_dict(data.get("player_position_change", {}), 'player_position_change')
        obj.player_position_in_class = CellConfig.from_dict(data.get("player_position_in_class", {}), 'player_position_in_class')
        obj.player_speed_trap = CellConfig.from_dict(data.get("player_speed_trap", {}), 'player_speed_trap')
        obj.player_stint_laps = CellConfig.from_dict(data.get("player_stint_laps", {}), 'player_stint_laps')
        obj.player_time_gap = CellConfig.from_dict(data.get("player_time_gap", {}), 'player_time_gap')
        obj.player_tyre_compound = CellConfig.from_dict(data.get("player_tyre_compound", {}), 'player_tyre_compound')
        obj.player_vehicle_integrity = CellConfig.from_dict(data.get("player_vehicle_integrity", {}), 'player_vehicle_integrity')
        obj.player_vehicle_name = CellConfig.from_dict(data.get("player_vehicle_name", {}), 'player_vehicle_name')
        obj.position = CellConfig.from_dict(data.get("position", {}), 'position')
        obj.position_change = CellConfig.from_dict(data.get("position_change", {}), 'position_change')
        obj.position_change_in_class = CellConfig.from_dict(data.get("position_change_in_class", {}), 'position_change_in_class')
        obj.position_gain = CellConfig.from_dict(data.get("position_gain", {}), 'position_gain')
        obj.position_in_class = CellConfig.from_dict(data.get("position_in_class", {}), 'position_in_class')
        obj.position_loss = CellConfig.from_dict(data.get("position_loss", {}), 'position_loss')
        obj.position_same = CellConfig.from_dict(data.get("position_same", {}), 'position_same')
        obj.same_lap = CellConfig.from_dict(data.get("same_lap", {}), 'same_lap')
        obj.speed_trap = CellConfig.from_dict(data.get("speed_trap", {}), 'speed_trap')
        obj.stint_laps = CellConfig.from_dict(data.get("stint_laps", {}), 'stint_laps')
        obj.time_gap = CellConfig.from_dict(data.get("time_gap", {}), 'time_gap')
        obj.time_gap_sign = CellConfig.from_dict(data.get("time_gap_sign", {}), 'time_gap_sign')
        obj.timegap = CellConfig.from_dict(data.get("timegap", {}), 'timegap')
        obj.tyre_compound = CellConfig.from_dict(data.get("tyre_compound", {}), 'tyre_compound')
        obj.vehicle = CellConfig.from_dict(data.get("vehicle", {}), 'vehicle')
        obj.vehicle_brand_as_name = CellConfig.from_dict(data.get("vehicle_brand_as_name", {}), 'vehicle_brand_as_name')
        obj.vehicle_in_garage = CellConfig.from_dict(data.get("vehicle_in_garage", {}), 'vehicle_in_garage')
        obj.vehicle_integrity = CellConfig.from_dict(data.get("vehicle_integrity", {}), 'vehicle_integrity')
        obj.vehicle_integrity_full = CellConfig.from_dict(data.get("vehicle_integrity_full", {}), 'vehicle_integrity_full')
        obj.vehicle_integrity_high = CellConfig.from_dict(data.get("vehicle_integrity_high", {}), 'vehicle_integrity_high')
        obj.vehicle_integrity_low = CellConfig.from_dict(data.get("vehicle_integrity_low", {}), 'vehicle_integrity_low')
        obj.vehicle_name = CellConfig.from_dict(data.get("vehicle_name", {}), 'vehicle_name')
        obj.yellow_flag = CellConfig.from_dict(data.get("yellow_flag", {}), 'yellow_flag')
        obj.additional_players_behind = data.get("additional_players_behind", obj.additional_players_behind)
        obj.additional_players_front = data.get("additional_players_front", obj.additional_players_front)
        obj.brand_logo_width = data.get("brand_logo_width", obj.brand_logo_width)
        obj.class_width = data.get("class_width", obj.class_width)
        obj.driver_name_align_center = data.get("driver_name_align_center", obj.driver_name_align_center)
        obj.driver_name_shorten = data.get("driver_name_shorten", obj.driver_name_shorten)
        obj.driver_name_uppercase = data.get("driver_name_uppercase", obj.driver_name_uppercase)
        obj.driver_name_width = data.get("driver_name_width", obj.driver_name_width)
        obj.energy_remaining_decimal_places = data.get("energy_remaining_decimal_places", obj.energy_remaining_decimal_places)
        obj.garage_status_text = data.get("garage_status_text", obj.garage_status_text)
        obj.nearest_time_gap_threshold_behind = data.get("nearest_time_gap_threshold_behind", obj.nearest_time_gap_threshold_behind)
        obj.nearest_time_gap_threshold_front = data.get("nearest_time_gap_threshold_front", obj.nearest_time_gap_threshold_front)
        obj.pit_status_text = data.get("pit_status_text", obj.pit_status_text)
        obj.time_gap_align_center = data.get("time_gap_align_center", obj.time_gap_align_center)
        obj.time_gap_decimal_places = data.get("time_gap_decimal_places", obj.time_gap_decimal_places)
        obj.time_gap_width = data.get("time_gap_width", obj.time_gap_width)
        obj.vehicle_name_align_center = data.get("vehicle_name_align_center", obj.vehicle_name_align_center)
        obj.vehicle_name_uppercase = data.get("vehicle_name_uppercase", obj.vehicle_name_uppercase)
        obj.vehicle_name_width = data.get("vehicle_name_width", obj.vehicle_name_width)
        obj.yellow_flag_status_text = data.get("yellow_flag_status_text", obj.yellow_flag_status_text)
        return obj
