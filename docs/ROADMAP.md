# Roadmap

TinyUi tracks roadmap items latest-first.

## Next

These are on the radar, not tied to a release yet:

- Widget globals (font, background, opacity, layout)
- Processing / derived data layer
- Game detection and automatic source handoff inside provider families
- Provider selection UI
- Editor surface for compounds, vehicle-specific data, and other user-managed plugin data
- Spotter?
- Custom widgets
- Grouping widgets

---

# Last update

## 0.4.0 — Runtime consolidation

This release rewrote the shape of TinyUi's core. `tinycore.runtime` is now the
live execution owner. The old `app`, `session`, `capabilities`, and `poll` layers
are gone. Plugin participation, process supervision, scheduling, staged updates,
and runtime diagnostics all live under one coherent runtime model.

- [x] Replace the `App` container and flat registry boot path with explicit host/runtime composition
- [x] Move live plugin participation into `tinycore.runtime.plugins` (activation, providers, exports, subprocess lifecycle)
- [x] Introduce staged update model with explicit `refresh` and `derive` phases driven by one `RuntimeUpdateLoop`
- [x] Build a runtime graph with declared units, process relationships, scheduling metadata, and live state
- [x] Add a runtime inspector with devtools Runtime tab: tree view, state filters, sorting, update-stage visibility
- [x] Remove `session`, `capabilities`, and `poll` as architectural owners
- [x] Clean up runtime vocabulary around activation, participants, exports, update, and runtime
