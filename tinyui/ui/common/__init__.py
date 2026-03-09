# tinyui/ui/common/__init__.py
"""Shared UI primitives used across all layers."""

from .base_dialog import (
    BaseDialog,
    DialogSingleton,
    DialogSingletonError,
    singleton_dialog,
)
from .scaler import UIScaler
from .validators import (
    QVAL_COLOR,
    QVAL_FILENAME,
    QVAL_FLOAT,
    QVAL_HEATMAP,
    QVAL_INTEGER,
)

__all__ = [
    "UIScaler",
    "QVAL_INTEGER",
    "QVAL_FLOAT",
    "QVAL_COLOR",
    "QVAL_HEATMAP",
    "QVAL_FILENAME",
    "BaseDialog",
    "DialogSingleton",
    "DialogSingletonError",
    "singleton_dialog",
]
