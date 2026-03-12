"""Patroon matching voor componenten."""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class Match:
    component_name: str
    index: Optional[int]  # None voor prefix, int voor numbered
    attribute: str


class Matcher:
    def __init__(self, patterns_config: Dict):
        self._prefix_patterns = []
        self._numbered_patterns = []

        for comp in patterns_config.get("prefix_components", []):
            self._prefix_patterns.append(
                {
                    "name": comp["name"],
                    "regex": re.compile(comp["pattern"]),
                    "attributes": set(comp["attributes"]),
                }
            )

        for comp in patterns_config.get("numbered_components", []):
            self._numbered_patterns.append(
                {
                    "name": comp["name"],
                    "regex": re.compile(comp["pattern"]),
                    "attributes": set(comp["attributes"]),
                }
            )

    def match(self, key: str) -> Optional[Match]:
        """Probeer key te matchen tegen alle patronen."""
        # Eerst prefix patterns
        for p in self._prefix_patterns:
            if m := p["regex"].match(key):
                return Match(component_name=p["name"], index=None, attribute=m.group(2))

        # Dan numbered patterns
        for p in self._numbered_patterns:
            if m := p["regex"].match(key):
                return Match(
                    component_name=p["name"],
                    index=int(m.group(1)),
                    attribute=m.group(2),
                )

        return None

    def get_component_names(self) -> Tuple[List[str], List[str]]:
        """Retourneer (prefix_names, numbered_names)."""
        prefix = [p["name"] for p in self._prefix_patterns]
        numbered = [p["name"] for p in self._numbered_patterns]
        return prefix, numbered
