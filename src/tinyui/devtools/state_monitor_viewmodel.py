#  TinyUI
"""Thin Qt adapter over the runtime inspector."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from tinycore.inspect.runtime_inspector import RuntimeInspector

_SKIP_PROPS = frozenset({"objectName"})


@dataclass(frozen=True)
class _QObjectSource:
    id: str
    label: str
    obj: QObject


class StateMonitorViewModel(QObject):
    """Expose runtime inspector state to QML."""

    sourcesChanged = Signal()
    selectedChanged = Signal()
    entriesChanged = Signal()
    sectionsChanged = Signal()

    def __init__(self, inspector: RuntimeInspector, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._inspector = inspector
        self._qobject_sources: list[_QObjectSource] = []
        self._selected_index = -1
        self._entries: list[dict] = []
        self._sections: list[dict] = []
        self._collapsed_by_source: dict[str, set[str]] = {}
        self._timer = QTimer(self)
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._refresh)

        if self._inspector.sources():
            self._selected_index = 0

    def register_object(self, label: str, obj: QObject) -> None:
        """Register a QObject source locally in the Qt adapter layer."""
        self._qobject_sources.append(_QObjectSource(f"qobject:{label}", label, obj))
        if self._selected_index < 0 and self._all_sources():
            self._selected_index = 0
            self.selectedChanged.emit()
        self.sourcesChanged.emit()

    def start(self) -> None:
        """Start refreshing inspector snapshots."""
        self._timer.start()

    def shutdown(self) -> None:
        self._timer.stop()

    def _refresh(self) -> None:
        if self._selected_index < 0:
            return

        sources = self._all_sources()
        if self._selected_index >= len(sources):
            return

        selected = sources[self._selected_index]
        if selected["kind"] == "qobject":
            snapshot = self._snapshot_qobject(selected["id"])
        else:
            snapshot = self._inspector.snapshot(selected["id"])
        entries: list[dict] = []
        for entry in snapshot:
            if isinstance(entry, dict):
                entries.append(entry)
            else:
                entries.append(
                    {
                        "key": entry.key,
                        "value": entry.value,
                        "changed": entry.changed,
                        "changedAt": entry.changed_at,
                    }
                )
        self._entries = entries
        self._sections = self._build_sections(selected["id"], entries)
        self.entriesChanged.emit()
        self.sectionsChanged.emit()

    def _all_sources(self) -> list[dict]:
        runtime_sources = [
            {"id": info.id, "label": info.label, "kind": info.kind}
            for info in self._inspector.sources()
        ]
        qobject_sources = [
            {"id": source.id, "label": source.label, "kind": "qobject"}
            for source in self._qobject_sources
        ]
        return runtime_sources + qobject_sources

    def _snapshot_qobject(self, source_id: str):
        source = next((item for item in self._qobject_sources if item.id == source_id), None)
        if source is None:
            return []

        entries = []
        meta = source.obj.metaObject()
        for index in range(meta.propertyCount()):
            prop = meta.property(index)
            name = prop.name()
            if name in _SKIP_PROPS:
                continue
            try:
                value = prop.read(source.obj)
                if isinstance(value, list):
                    rendered = f"[{len(value)} items]"
                elif isinstance(value, dict):
                    rendered = "{…}"
                else:
                    try:
                        rendered = f"{float(value):.6g}"
                    except (ValueError, TypeError):
                        rendered = str(value)
            except Exception as exc:
                rendered = f"err: {exc}"
            entries.append(
                {
                    "key": name,
                    "value": rendered,
                    "changed": False,
                    "changedAt": 0,
                }
            )
        return entries

    def _build_sections(self, source_id: str, entries: list[dict]) -> list[dict]:
        grouped: dict[str, list[dict]] = {}
        order: list[str] = []
        for entry in entries:
            key = str(entry["key"])
            if "." in key:
                section, leaf = key.split(".", 1)
            else:
                section, leaf = "general", key
            if section not in grouped:
                grouped[section] = []
                order.append(section)
            grouped[section].append(
                {
                    "key": leaf,
                    "fullKey": key,
                    "value": entry["value"],
                    "changed": entry["changed"],
                    "changedAt": entry["changedAt"],
                }
            )

        collapsed = self._collapsed_by_source.setdefault(source_id, set())
        sections: list[dict] = []
        for section in order:
            sections.append(
                {
                    "name": section,
                    "title": section.replace("_", " ").title(),
                    "collapsed": section in collapsed,
                    "entries": grouped[section],
                }
            )
        return sections

    @Property("QVariantList", notify=sourcesChanged)
    def sources(self) -> list:
        return [
            {"label": info["label"], "index": index}
            for index, info in enumerate(self._all_sources())
        ]

    @Property(int, notify=selectedChanged)
    def selectedIndex(self) -> int:
        return self._selected_index

    @Slot(int)
    def selectSource(self, index: int) -> None:
        if 0 <= index < len(self._all_sources()) and index != self._selected_index:
            self._selected_index = index
            self._entries = []
            self._sections = []
            self.selectedChanged.emit()
            self.entriesChanged.emit()
            self.sectionsChanged.emit()

    @Slot(str)
    def toggleSection(self, name: str) -> None:
        sources = self._all_sources()
        if not (0 <= self._selected_index < len(sources)):
            return
        source_id = sources[self._selected_index]["id"]
        collapsed = self._collapsed_by_source.setdefault(source_id, set())
        if name in collapsed:
            collapsed.remove(name)
        else:
            collapsed.add(name)
        self._sections = self._build_sections(source_id, self._entries)
        self.sectionsChanged.emit()

    @Property("QVariantList", notify=entriesChanged)
    def entries(self) -> list:
        return self._entries

    @Property("QVariantList", notify=sectionsChanged)
    def sections(self) -> list:
        return self._sections
