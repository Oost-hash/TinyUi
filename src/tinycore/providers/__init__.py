"""tinycore.providers — pull-based data providers."""

from .protocol import Provider
from .registry import ProviderRegistry

__all__ = ["Provider", "ProviderRegistry"]
