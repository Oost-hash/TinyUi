"""Application-level runtime fundamentals."""

from runtime.app.identity import APP_NAME, VERSION
from runtime.app.paths import AppPaths

__all__ = [
    "APP_NAME",
    "AppPaths",
    "VERSION",
]
