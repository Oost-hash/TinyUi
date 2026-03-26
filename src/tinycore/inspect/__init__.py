#  TinyUI
"""Runtime inspection services."""

from .log_inspector import LogInspector, LogRecordEntry
from .runtime_inspector import RuntimeInspector

__all__ = ["RuntimeInspector", "LogInspector", "LogRecordEntry"]
