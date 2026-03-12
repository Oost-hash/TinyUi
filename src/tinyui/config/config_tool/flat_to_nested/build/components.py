"""Bereidt component data voor templates."""

from typing import Dict, List


def prepare(prefix_components: Dict, numbered_components: Dict) -> List[tuple]:
    """
    Bouw data voor _components.py template.

    Returns: lijst van (class_name, suffixes_dict) tuples
    """
    components = []

    # Prefix components -> PascalCase + Config
    for name, data in prefix_components.items():
        class_name = name.capitalize() + "Config"
        suffixes = {}

        for suffix, info in data["attributes"].items():
            typ = info["type"]
            default = info["mode"]
            suffixes[suffix] = (typ, default)

        components.append((class_name, suffixes))

    # Numbered components -> PascalCase (zonder Config suffix)
    for name, data in numbered_components.items():
        class_name = name.capitalize()
        suffixes = {}

        for attr, info in data["attributes_info"].items():
            typ = info["type"]
            default = info["mode"]
            suffixes[attr] = (typ, default)

        components.append((class_name, suffixes))

    return components
