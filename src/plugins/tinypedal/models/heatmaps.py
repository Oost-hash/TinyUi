# Auto-generated heatmaps
# temperature (C) -> color gradient mappings

from .base import HeatmapConfig, HeatmapEntry

HEATMAP_DEFAULT_BRAKE = HeatmapConfig(
    name='HEATMAP_DEFAULT_BRAKE',
    entries=(
        HeatmapEntry(-273.0, '#44F'),
        HeatmapEntry(100.0, '#48F'),
        HeatmapEntry(200.0, '#4FF'),
        HeatmapEntry(300.0, '#4F8'),
        HeatmapEntry(400.0, '#4F4'),
        HeatmapEntry(500.0, '#8F4'),
        HeatmapEntry(600.0, '#FF4'),
        HeatmapEntry(700.0, '#F84'),
        HeatmapEntry(800.0, '#F44'),
    ),
)

HEATMAP_DEFAULT_TYRE = HeatmapConfig(
    name='HEATMAP_DEFAULT_TYRE',
    entries=(
        HeatmapEntry(-273.0, '#44F'),
        HeatmapEntry(40.0, '#84F'),
        HeatmapEntry(60.0, '#F4F'),
        HeatmapEntry(80.0, '#F48'),
        HeatmapEntry(100.0, '#F44'),
        HeatmapEntry(120.0, '#F84'),
        HeatmapEntry(140.0, '#FF4'),
    ),
)

brake_optimal_300 = HeatmapConfig(
    name='brake_optimal_300',
    entries=(
        HeatmapEntry(-273.0, '#44F'),
        HeatmapEntry(75.0, '#48F'),
        HeatmapEntry(150.0, '#4FF'),
        HeatmapEntry(225.0, '#4F8'),
        HeatmapEntry(300.0, '#4F4'),
        HeatmapEntry(375.0, '#8F4'),
        HeatmapEntry(450.0, '#FF4'),
        HeatmapEntry(525.0, '#F84'),
        HeatmapEntry(600.0, '#F44'),
    ),
)

tyre_optimal_100 = HeatmapConfig(
    name='tyre_optimal_100',
    entries=(
        HeatmapEntry(-273.0, '#44F'),
        HeatmapEntry(70.0, '#48F'),
        HeatmapEntry(80.0, '#4FF'),
        HeatmapEntry(90.0, '#4F8'),
        HeatmapEntry(100.0, '#4F4'),
        HeatmapEntry(110.0, '#8F4'),
        HeatmapEntry(120.0, '#FF4'),
        HeatmapEntry(130.0, '#F84'),
        HeatmapEntry(140.0, '#F44'),
    ),
)

tyre_optimal_70 = HeatmapConfig(
    name='tyre_optimal_70',
    entries=(
        HeatmapEntry(-273.0, '#44F'),
        HeatmapEntry(40.0, '#48F'),
        HeatmapEntry(50.0, '#4FF'),
        HeatmapEntry(60.0, '#4F8'),
        HeatmapEntry(70.0, '#4F4'),
        HeatmapEntry(80.0, '#8F4'),
        HeatmapEntry(90.0, '#FF4'),
        HeatmapEntry(100.0, '#F84'),
        HeatmapEntry(110.0, '#F44'),
    ),
)

tyre_optimal_80 = HeatmapConfig(
    name='tyre_optimal_80',
    entries=(
        HeatmapEntry(-273.0, '#44F'),
        HeatmapEntry(50.0, '#48F'),
        HeatmapEntry(60.0, '#4FF'),
        HeatmapEntry(70.0, '#4F8'),
        HeatmapEntry(80.0, '#4F4'),
        HeatmapEntry(90.0, '#8F4'),
        HeatmapEntry(100.0, '#FF4'),
        HeatmapEntry(110.0, '#F84'),
        HeatmapEntry(120.0, '#F44'),
    ),
)

tyre_optimal_90 = HeatmapConfig(
    name='tyre_optimal_90',
    entries=(
        HeatmapEntry(-273.0, '#44F'),
        HeatmapEntry(60.0, '#48F'),
        HeatmapEntry(70.0, '#4FF'),
        HeatmapEntry(80.0, '#4F8'),
        HeatmapEntry(90.0, '#4F4'),
        HeatmapEntry(100.0, '#8F4'),
        HeatmapEntry(110.0, '#FF4'),
        HeatmapEntry(120.0, '#F84'),
        HeatmapEntry(130.0, '#F44'),
    ),
)


HEATMAPS: dict[str, HeatmapConfig] = {
    'HEATMAP_DEFAULT_BRAKE': HEATMAP_DEFAULT_BRAKE,
    'HEATMAP_DEFAULT_TYRE': HEATMAP_DEFAULT_TYRE,
    'brake_optimal_300': brake_optimal_300,
    'tyre_optimal_100': tyre_optimal_100,
    'tyre_optimal_70': tyre_optimal_70,
    'tyre_optimal_80': tyre_optimal_80,
    'tyre_optimal_90': tyre_optimal_90,
}
