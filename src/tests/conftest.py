"""Pytest configuration for TinyUI tests."""

import sys
from pathlib import Path

# Add src to Python path for all tests
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)
