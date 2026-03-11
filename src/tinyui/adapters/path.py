# src/tinyui/adapters/paths.py
"""Configure TinyPedal data paths to use src/data/ structure."""

import os
from pathlib import Path

# Root of all data
DATA_ROOT = Path(__file__).parent.parent.parent / "data"

# Mapping: TinyPedal attribute name -> folder name in data/
DATA_PATHS = {
    "brand_logo": "brandlogo",
    "car_setups": "carsetups",
    "delta_best": "deltabest",
    "energy_delta": "deltabest",  # Shares folder
    "fuel_delta": "deltabest",  # Shares folder
    "pace_notes": "pacenotes",
    "sector_best": "deltabest",  # Shares folder
    "settings": "settings",
    "track_map": "trackmap",
    "track_notes": "tracknotes",
}


def configure_data_paths(cfg):
    """Redirect all TinyPedal data paths to src/data/."""

    for attr_name, folder_name in DATA_PATHS.items():
        full_path = DATA_ROOT / folder_name

        # Set path WITH trailing slash (belangrijk!)
        setattr(cfg.path, attr_name, str(full_path) + os.sep)

        # Ensure folder exists
        full_path.mkdir(parents=True, exist_ok=True)

    import logging

    logger = logging.getLogger("TinyUi")
    logger.debug(f"Data paths configured to: {DATA_ROOT}")


def get_data_path(subfolder: str) -> Path:
    """Get path to a specific data subfolder."""
    return DATA_ROOT / subfolder
