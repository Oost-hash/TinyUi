#  TinyUI
"""Thin compatibility layer over core-owned runtime boot."""

from tinycore.runtime.boot import boot_runtime as bootstrap_runtime
from tinycore.runtime.boot import discover_manifests

__all__ = ["bootstrap_runtime", "discover_manifests"]
