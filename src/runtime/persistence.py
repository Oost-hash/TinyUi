"""SettingsRegistry — central store for all user-configurable settings."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SettingsSpec:
    key:     str
    label:   str
    default: Any
    type:    str                       # "bool" | "str" | "int" | "float" | "choice"
    choices: list[str] = field(default_factory=list)


_VALID_TYPES = {"bool", "str", "int", "float", "choice"}


class SettingsRegistry:
    def __init__(self, config_dir: Path | None = None) -> None:
        self._dir = config_dir
        self._specs:  dict[str, list[SettingsSpec]] = {}   # namespace → specs
        self._values: dict[str, dict[str, Any]]     = {}   # namespace → {key: value}

    # ── Registration ──────────────────────────────────────────────────────

    def register(self, namespace: str, spec: SettingsSpec) -> None:
        self._specs.setdefault(namespace, []).append(spec)
        self._values.setdefault(namespace, {}).setdefault(spec.key, spec.default)

    # ── Reading ───────────────────────────────────────────────────────────

    def get(self, namespace: str, key: str) -> Any:
        return self._values.get(namespace, {}).get(key)

    def by_namespace(self) -> dict[str, list[SettingsSpec]]:
        return {ns: list(specs) for ns, specs in self._specs.items()}

    # ── Writing ───────────────────────────────────────────────────────────

    def set(self, namespace: str, key: str, value: Any) -> None:
        spec = next((s for s in self._specs.get(namespace, []) if s.key == key), None)
        if spec is not None:
            _validate(spec, value)
        self._values.setdefault(namespace, {})[key] = value

    # ── Persistence ───────────────────────────────────────────────────────

    def load_persisted(self) -> None:
        if not self._dir:
            return
        for namespace in self._specs:
            path = self._dir / namespace / "settings.json"
            if not path.exists():
                continue
            try:
                with path.open(encoding="utf-8") as f:
                    values: dict = json.load(f)
                self._values.setdefault(namespace, {}).update(values)
            except Exception:
                pass  # corrupt file — keep defaults

    def save(self, namespace: str) -> None:
        if not self._dir:
            return
        path = self._dir / namespace / "settings.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(self._values.get(namespace, {}), f, indent=2, ensure_ascii=False)

    # ── Scoped access ─────────────────────────────────────────────────────

    def scoped(self, namespace: str) -> "ScopedSettings":
        return ScopedSettings(self, namespace)


class ScopedSettings:
    """Settings view for a single namespace — plugins use this, not the registry directly."""

    def __init__(self, registry: SettingsRegistry, namespace: str) -> None:
        self._registry = registry
        self._namespace = namespace

    def register(self, spec: SettingsSpec) -> None:
        self._registry.register(self._namespace, spec)

    def get(self, key: str) -> Any:
        return self._registry.get(self._namespace, key)

    def set(self, key: str, value: Any) -> None:
        self._registry.set(self._namespace, key, value)

    def save(self) -> None:
        self._registry.save(self._namespace)


def _validate(spec: SettingsSpec, value: Any) -> None:
    expected = {
        "bool":  bool,
        "str":   str,
        "int":   int,
        "float": (int, float),
        "choice": str,
    }.get(spec.type)
    if expected and not isinstance(value, expected):
        raise TypeError(f"Setting '{spec.key}' expects {spec.type}, got {type(value).__name__}")
    if spec.type == "choice" and value not in spec.choices:
        raise ValueError(f"Setting '{spec.key}': '{value}' not in {spec.choices}")
