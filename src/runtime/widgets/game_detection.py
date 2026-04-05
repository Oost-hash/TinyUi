"""Game detection helpers for runtime-owned widget readiness."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import psutil

from app_schema.manifest import ConnectorGameDecl


def detect_active_game_id(
    connector_games: Sequence[ConnectorGameDecl],
    *,
    process_names: Iterable[str] | None = None,
) -> str | None:
    """Return the first declared game id whose detect_names match a running process."""

    normalized_process_names = _normalized_process_names(process_names)
    for game in connector_games:
        for detect_name in game.detect_names:
            if _normalize_process_name(detect_name) in normalized_process_names:
                return game.id
    return None


def _normalized_process_names(process_names: Iterable[str] | None) -> set[str]:
    if process_names is None:
        process_names = _iter_process_names()
    return {
        normalized
        for name in process_names
        if (normalized := _normalize_process_name(name))
    }


def _iter_process_names() -> Iterable[str]:
    for proc in psutil.process_iter(["name"]):
        try:
            name = proc.info.get("name")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        if isinstance(name, str):
            yield name


def _normalize_process_name(name: str) -> str:
    normalized = name.strip().casefold()
    if normalized.endswith(".exe"):
        normalized = normalized[:-4]
    return normalized
