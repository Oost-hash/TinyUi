"""Global analysis pass - cross-widget analyse.

Bepaalt welke components shared zijn (2+ widgets) vs inline,
en verzamelt globale color palettes.
"""

from __future__ import annotations

from collections import Counter

from ..model import Component, WidgetAST


def mark_shared_components(widgets: list[WidgetAST]) -> list[Component]:
    """Markeer components die in 2+ widgets voorkomen als shared.

    Muteert component.shared op de AST nodes.
    Returns lijst van shared components voor _components.py.
    """
    class_count: Counter[str] = Counter()
    for widget in widgets:
        for comp in widget.components:
            class_count[comp.class_name] += 1

    shared = []
    seen = set()

    for widget in widgets:
        for comp in widget.components:
            if class_count[comp.class_name] >= 2:
                comp.shared = True
                if comp.class_name not in seen:
                    shared.append(comp)
                    seen.add(comp.class_name)

    return shared
