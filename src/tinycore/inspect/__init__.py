#  TinyUI
"""Runtime inspection services."""

from .log_inspector import LogInspector, LogRecordEntry
from .protocols import InspectionSnapshot, InspectionSnapshotProvider
from .runtime_inspector import RuntimeInspector

__all__ = [
    "InspectionSnapshot",
    "InspectionSnapshotProvider",
    "RuntimeInspector",
    "LogInspector",
    "LogRecordEntry",
]
