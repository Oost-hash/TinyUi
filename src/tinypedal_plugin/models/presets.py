# Auto-generated presets
# vehicle and tyre preset registries

from .base import BrakePreset, ClassPreset, CompoundPreset

BRAKES: dict[str, BrakePreset] = {
    'GT3 - Front Brake': BrakePreset(name='GT3 - Front Brake', failure_thickness=30.0),
    'GT3 - Rear Brake': BrakePreset(name='GT3 - Rear Brake', failure_thickness=30.0),
    'GTE - Front Brake': BrakePreset(name='GTE - Front Brake', failure_thickness=30.0),
    'GTE - Rear Brake': BrakePreset(name='GTE - Rear Brake', failure_thickness=30.0),
    'Hyper - Front Brake': BrakePreset(name='Hyper - Front Brake', failure_thickness=25.0),
    'Hyper - Rear Brake': BrakePreset(name='Hyper - Rear Brake', failure_thickness=25.0),
    'LMP2 - Front Brake': BrakePreset(name='LMP2 - Front Brake', failure_thickness=25.0),
    'LMP2 - Rear Brake': BrakePreset(name='LMP2 - Rear Brake', failure_thickness=25.0),
}

CLASSES: dict[str, ClassPreset] = {
    'DPi': ClassPreset(name='DPi', alias='DPi'),
    'FR3.5_2014': ClassPreset(name='FR3.5_2014', alias='FR35', color='#4488AA'),
    'Formula Pro': ClassPreset(name='Formula Pro', alias='FPro', color='#FF3300'),
    'GT3': ClassPreset(name='GT3', alias='GT3', color='#229900'),
    'GTE': ClassPreset(name='GTE', alias='GTE', color='#00CC44'),
    'Hyper': ClassPreset(name='Hyper', alias='HY', color='#FF4400'),
    'Hypercar': ClassPreset(name='Hypercar', alias='HY', color='#FF4400'),
    'LMP1': ClassPreset(name='LMP1', alias='LMP1', color='#FF00AA'),
    'LMP2': ClassPreset(name='LMP2', alias='LMP2', color='#0088FF'),
    'LMP2_ELMS': ClassPreset(name='LMP2_ELMS', alias='LMP2_ELMS'),
    'LMP3': ClassPreset(name='LMP3', alias='LMP3', color='#880088'),
}

COMPOUNDS: dict[str, CompoundPreset] = {
    'BTCC - Hard': CompoundPreset(name='BTCC - Hard', symbol='H'),
    'BTCC - Medium': CompoundPreset(name='BTCC - Medium', symbol='M'),
    'BTCC - Soft': CompoundPreset(name='BTCC - Soft', symbol='S'),
    'BTCC - Wet': CompoundPreset(name='BTCC - Wet', symbol='W'),
    'GT3 - Hard': CompoundPreset(name='GT3 - Hard', heatmap='tyre_optimal_100', symbol='H'),
    'GT3 - Medium': CompoundPreset(name='GT3 - Medium', heatmap='tyre_optimal_90', symbol='M'),
    'GT3 - P2M (Rain)': CompoundPreset(name='GT3 - P2M (Rain)', symbol='W'),
    'GT3 - Soft': CompoundPreset(name='GT3 - Soft', heatmap='tyre_optimal_80', symbol='S'),
    'GT3 - Wet': CompoundPreset(name='GT3 - Wet', symbol='W'),
    'GTE - Hard': CompoundPreset(name='GTE - Hard', heatmap='tyre_optimal_100', symbol='H'),
    'GTE - Medium': CompoundPreset(name='GTE - Medium', heatmap='tyre_optimal_90', symbol='M'),
    'GTE - P2M (Rain)': CompoundPreset(name='GTE - P2M (Rain)', symbol='W'),
    'GTE - Soft': CompoundPreset(name='GTE - Soft', heatmap='tyre_optimal_80', symbol='S'),
    'GTE - Wet': CompoundPreset(name='GTE - Wet', symbol='W'),
    'Hyper - Hard': CompoundPreset(name='Hyper - Hard', heatmap='tyre_optimal_90', symbol='H'),
    'Hyper - Medium': CompoundPreset(name='Hyper - Medium', heatmap='tyre_optimal_80', symbol='M'),
    'Hyper - Soft': CompoundPreset(name='Hyper - Soft', heatmap='tyre_optimal_70', symbol='S'),
    'Hyper - Wet': CompoundPreset(name='Hyper - Wet', symbol='W'),
    'Hypercar - Hard': CompoundPreset(name='Hypercar - Hard', symbol='H'),
    'Hypercar - Medium': CompoundPreset(name='Hypercar - Medium', symbol='M'),
    'Hypercar - Soft': CompoundPreset(name='Hypercar - Soft', symbol='S'),
    'Hypercar - Wet': CompoundPreset(name='Hypercar - Wet', symbol='W'),
    'LMP2 - H5M (Inter)': CompoundPreset(name='LMP2 - H5M (Inter)', symbol='I'),
    'LMP2 - Hard': CompoundPreset(name='LMP2 - Hard', heatmap='tyre_optimal_90', symbol='H'),
    'LMP2 - Medium': CompoundPreset(name='LMP2 - Medium', heatmap='tyre_optimal_80', symbol='M'),
    'LMP2 - P2M (Rain)': CompoundPreset(name='LMP2 - P2M (Rain)', symbol='W'),
    'LMP2 - S7M (Soft)': CompoundPreset(name='LMP2 - S7M (Soft)', symbol='S'),
    'LMP2 - S8M (Medium)': CompoundPreset(name='LMP2 - S8M (Medium)', symbol='M'),
    'LMP2 - S9M (Hard)': CompoundPreset(name='LMP2 - S9M (Hard)', symbol='H'),
    'LMP2 - Soft': CompoundPreset(name='LMP2 - Soft', heatmap='tyre_optimal_70', symbol='S'),
    'LMP2 - Wet': CompoundPreset(name='LMP2 - Wet', symbol='W'),
    'LMP3 - P2M (Rain)': CompoundPreset(name='LMP3 - P2M (Rain)', symbol='W'),
    'LMP3 - S8M (Medium)': CompoundPreset(name='LMP3 - S8M (Medium)', symbol='M'),
}
