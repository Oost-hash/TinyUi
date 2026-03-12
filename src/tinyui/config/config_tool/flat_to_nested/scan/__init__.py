"""Analyseert widget configuraties."""

from .keys import infer_type, is_column
from .patterns import Match, Matcher
from .stats import aggregate, collect_by_component

__all__ = [
    "is_column",
    "infer_type",
    "Matcher",
    "Match",
    "aggregate",
    "collect_by_component",
]
